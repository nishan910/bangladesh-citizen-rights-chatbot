import { useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  async function sendMessage(event) {
    event.preventDefault()
    const text = question.trim()
    if (!text || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setQuestion('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      })

      const data = await response.json()
      if (!response.ok) throw new Error('সার্ভারে সমস্যা হয়েছে।')

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'কোনো উত্তর পাওয়া যায়নি।',
          sources: data.sources || [],
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'সংযোগ করা যাচ্ছে না। Backend চালু আছে কি না পরীক্ষা করুন।',
          sources: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div className="brand-icon">⚖️</div>
        <div>
          <h1>নাগরিক অধিকার সহায়ক</h1>
          <p>বাংলাদেশের আইন ও নাগরিক অধিকার সম্পর্কে জানুন</p>
        </div>
      </header>

      <section className="chat">
        {messages.length === 0 && (
          <div className="welcome">
            <div className="welcome-icon">📚</div>
            <h2>আপনাকে স্বাগতম</h2>
            <p>বাংলাদেশের আইন সম্পর্কে আপনার প্রশ্নটি বাংলায় লিখুন।</p>
            <button
              className="suggestion"
              onClick={() =>
                setQuestion('পারিবারিক সহিংসতার শিকার হলে কী সুরক্ষা পাওয়া যায়?')
              }
            >
              পারিবারিক সহিংসতা সম্পর্কে জিজ্ঞাসা করুন
            </button>
          </div>
        )}

        {messages.map((message, index) => (
          <article className={`message ${message.role}`} key={index}>
            <strong>
              {message.role === 'user' ? 'আপনার প্রশ্ন' : 'আইন সহায়ক'}
            </strong>
            <p className="message-content">{message.content}</p>

            {message.sources?.length > 0 && (
              <details className="sources">
                <summary>আইনের উৎস ({message.sources.length})</summary>
                <ul>
                  {message.sources.map((source, i) => (
                    <li key={i}>
                      {/^https?:\/\//i.test(source) ? (
                        <a href={source} target="_blank" rel="noreferrer">
                          {source}
                        </a>
                      ) : (
                        source
                      )}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </article>
        ))}

        {loading && <p className="loading">উত্তর তৈরি হচ্ছে…</p>}
      </section>

      <form className="composer" onSubmit={sendMessage}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="এখানে আপনার প্রশ্ন লিখুন..."
          rows={2}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'অপেক্ষা করুন…' : 'প্রশ্ন পাঠান ↑'}
        </button>
      </form>

      <footer className="footer">
        এই চ্যাটবট সাধারণ আইনি তথ্য দেয়, আইনজীবীর বিকল্প নয়। গুরুত্বপূর্ণ
        সিদ্ধান্তের আগে মূল আইন যাচাই করুন।
      </footer>
    </main>
  )
}

export default App
