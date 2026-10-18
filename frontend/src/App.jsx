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
      if (!response.ok) throw new Error('à¦¸à¦¾à¦°à§à¦­à¦¾à¦°à§‡ à¦¸à¦®à¦¸à§à¦¯à¦¾ à¦¹à§Ÿà§‡à¦›à§‡à¥¤')

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'à¦•à§‹à¦¨à§‹ à¦‰à¦¤à§à¦¤à¦° à¦ªà¦¾à¦“à§Ÿà¦¾ à¦¯à¦¾à§Ÿà¦¨à¦¿à¥¤',
          sources: data.sources || [],
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'à¦¸à¦‚à¦¯à§‹à¦— à¦•à¦°à¦¾ à¦¯à¦¾à¦šà§à¦›à§‡ à¦¨à¦¾à¥¤ Backend à¦šà¦¾à¦²à§ à¦†à¦›à§‡ à¦•à¦¿ à¦¨à¦¾ à¦ªà¦°à§€à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨à¥¤',
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
        <div className="brand-icon">âš–ï¸</div>
        <div>
          <h1>à¦¨à¦¾à¦—à¦°à¦¿à¦• à¦…à¦§à¦¿à¦•à¦¾à¦° à¦¸à¦¹à¦¾à¦¯à¦¼à¦•</h1>
          <p>à¦¬à¦¾à¦‚à¦²à¦¾à¦¦à§‡à¦¶à§‡à¦° à¦†à¦‡à¦¨ à¦“ à¦¨à¦¾à¦—à¦°à¦¿à¦• à¦…à¦§à¦¿à¦•à¦¾à¦° à¦¸à¦®à§à¦ªà¦°à§à¦•à§‡ à¦œà¦¾à¦¨à§à¦¨</p>
        </div>
      </header>

      <section className="chat">
        {messages.length === 0 && (
          <div className="welcome">
            <div className="welcome-icon">ðŸ“š</div>
            <h2>à¦†à¦ªà¦¨à¦¾à¦•à§‡ à¦¸à§à¦¬à¦¾à¦—à¦¤à¦®</h2>
            <p>à¦¬à¦¾à¦‚à¦²à¦¾à¦¦à§‡à¦¶à§‡à¦° à¦†à¦‡à¦¨ à¦¸à¦®à§à¦ªà¦°à§à¦•à§‡ à¦†à¦ªà¦¨à¦¾à¦° à¦ªà§à¦°à¦¶à§à¦¨à¦Ÿà¦¿ à¦¬à¦¾à¦‚à¦²à¦¾à§Ÿ à¦²à¦¿à¦–à§à¦¨à¥¤</p>
            <button
              className="suggestion"
              onClick={() =>
                setQuestion('à¦ªà¦¾à¦°à¦¿à¦¬à¦¾à¦°à¦¿à¦• à¦¸à¦¹à¦¿à¦‚à¦¸à¦¤à¦¾à¦° à¦¶à¦¿à¦•à¦¾à¦° à¦¹à¦²à§‡ à¦•à§€ à¦¸à§à¦°à¦•à§à¦·à¦¾ à¦ªà¦¾à¦“à§Ÿà¦¾ à¦¯à¦¾à§Ÿ?')
              }
            >
              à¦ªà¦¾à¦°à¦¿à¦¬à¦¾à¦°à¦¿à¦• à¦¸à¦¹à¦¿à¦‚à¦¸à¦¤à¦¾ à¦¸à¦®à§à¦ªà¦°à§à¦•à§‡ à¦œà¦¿à¦œà§à¦žà¦¾à¦¸à¦¾ à¦•à¦°à§à¦¨
            </button>
          </div>
        )}

        {messages.map((message, index) => (
          <article className={`message ${message.role}`} key={index}>
            <strong>
              {message.role === 'user' ? 'à¦†à¦ªà¦¨à¦¾à¦° à¦ªà§à¦°à¦¶à§à¦¨' : 'à¦†à¦‡à¦¨ à¦¸à¦¹à¦¾à¦¯à¦¼à¦•'}
            </strong>
            <p className="message-content">{message.content}</p>

            {message.sources?.length > 0 && (
              <details className="sources">
                <summary>à¦†à¦‡à¦¨à§‡à¦° à¦‰à§Žà¦¸ ({message.sources.length})</summary>
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

        {loading && <p className="loading">à¦‰à¦¤à§à¦¤à¦° à¦¤à§ˆà¦°à¦¿ à¦¹à¦šà§à¦›à§‡â€¦</p>}
      </section>

      <form className="composer" onSubmit={sendMessage}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="à¦à¦–à¦¾à¦¨à§‡ à¦†à¦ªà¦¨à¦¾à¦° à¦ªà§à¦°à¦¶à§à¦¨ à¦²à¦¿à¦–à§à¦¨..."
          rows={2}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'à¦…à¦ªà§‡à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨â€¦' : 'à¦ªà§à¦°à¦¶à§à¦¨ à¦ªà¦¾à¦ à¦¾à¦¨ â†‘'}
        </button>
      </form>

      <footer className="footer">
        à¦à¦‡ à¦šà§à¦¯à¦¾à¦Ÿà¦¬à¦Ÿ à¦¸à¦¾à¦§à¦¾à¦°à¦£ à¦†à¦‡à¦¨à¦¿ à¦¤à¦¥à§à¦¯ à¦¦à§‡à§Ÿ, à¦†à¦‡à¦¨à¦œà§€à¦¬à§€à¦° à¦¬à¦¿à¦•à¦²à§à¦ª à¦¨à§Ÿà¥¤ à¦—à§à¦°à§à¦¤à§à¦¬à¦ªà§‚à¦°à§à¦£
        à¦¸à¦¿à¦¦à§à¦§à¦¾à¦¨à§à¦¤à§‡à¦° à¦†à¦—à§‡ à¦®à§‚à¦² à¦†à¦‡à¦¨ à¦¯à¦¾à¦šà¦¾à¦‡ à¦•à¦°à§à¦¨à¥¤
      </footer>
    </main>
  )
}

export default App
