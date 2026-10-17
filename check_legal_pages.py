import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "processed" / "legal_sources.json"

PAGES = [
    "https://legislativediv.gov.bd/pages/static-pages/694032a335ce18e1c055fc2d",
    "https://legislativediv.gov.bd/pages/static-pages/694032c535ce18e1c0562238",
    "https://legislativediv.gov.bd/pages/static-pages/694032b735ce18e1c0561103",
    "https://legislativediv.gov.bd/pages/static-pages/6940329835ce18e1c055f04c",
]

GENERIC_NAMES = {"ডাউনলোড", "download", "click here", "দেখুন", ""}
records = []
seen = set()

with requests.Session() as session:
    session.headers["User-Agent"] = "BangladeshCitizenRightsChatbot/0.1"

    for page_url in PAGES:
        try:
            response = session.get(page_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.select("a[href]"):
                pdf_url = urljoin(page_url, link["href"]).split("#")[0]
                if not pdf_url.lower().split("?")[0].endswith(".pdf"):
                    continue
                if pdf_url in seen:
                    continue

                seen.add(pdf_url)
                title = link.get_text(" ", strip=True)

                if title.casefold() in GENERIC_NAMES:
                    for parent in link.parents:
                        if parent.name in {"body", "html"}:
                            break
                        nearby = parent.get_text(" ", strip=True)
                        nearby = " ".join(nearby.split())
                        if nearby and nearby.casefold() not in GENERIC_NAMES:
                            title = nearby
                            break

                title = re.sub(
                    r"\s*(ডাউনলোড|download)\s*$",
                    "",
                    title,
                    flags=re.IGNORECASE,
                ).strip()

                title = re.sub(r"^[০-৯0-9]+\s+", "", title)

                year_markers = list(re.finditer(
                    r"[০-৯0-9]{4}\s*(?:সনের|সালের)",
                    title,
                ))
                if len(year_markers) >= 2:
                    title = title[:year_markers[1].start()].strip()

                needs_review = title.casefold() in GENERIC_NAMES
                if needs_review:
                    title = "নাম শনাক্ত করা যায়নি"

                records.append({
                    "title": title,
                    "pdf_url": pdf_url,
                    "source_page": page_url,
                    "source_organization": "Bangladesh Legislative and Parliamentary Affairs Division",
                    "verification_status": (
                        "needs_title_review" if needs_review
                        else "source_link_collected"
                    ),
                })

            print("OK:", page_url)

        except requests.RequestException as error:
            print("ERROR:", page_url, "-", error)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

generic_count = sum(
    item["verification_status"] == "needs_title_review"
    for item in records
)

print("\nUnique PDF links:", len(records))
print("Titles needing review:", generic_count)
print("Saved:", OUTPUT)
