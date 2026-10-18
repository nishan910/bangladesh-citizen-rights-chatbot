FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && python -c "import torch; print('torch==' + torch.__version__)" > /tmp/torch-constraints.txt \
    && pip install --no-cache-dir -r requirements.txt --constraint /tmp/torch-constraints.txt \
    && rm /tmp/torch-constraints.txt

COPY backend/ ./backend/
COPY data/processed/chroma_db/ ./data/processed/chroma_db/

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
