import React, { useState, useRef, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getUserId } from '../utils/userId'
import { useWeatherContext } from '../contexts/WeatherContext'
import WeatherBackground from '../components/WeatherBackground'

export default function ChatBotPage() {
  const [isOpen, setIsOpen] = useState(true)
  const [messages, setMessages] = useState([
    { role: 'ai', text: "Hi! I'm Zen, your study assistant and music expert. I can help with:\n\n• Study strategies and tips\n• Music genre recommendations\n• Music suggestions for studying\n\nWhat would you like help with?" }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const navigate = useNavigate()
  const { conditionClass, timeOfDay } = useWeatherContext()

  const bgClass = useMemo(() => {
    if (timeOfDay === 'night') return 'night'
    if (timeOfDay === 'sunrise') return 'sunrise'
    if (timeOfDay === 'sunset') return 'sunset'
    return conditionClass
  }, [timeOfDay, conditionClass])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
    inputRef.current?.focus()
  }, [messages, isOpen])

  const handleSend = async () => {
    const message = inputValue.trim()
    if (!message || isLoading) return

    const userMessage = { role: 'user', text: message }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const userId = getUserId()
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message,
          user_id: userId 
        }),
      })

      // Check if response has content before parsing JSON
      const text = await response.text()
      if (!text || !text.trim()) {
        throw new Error('Empty response from server')
      }

      let data
      try {
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Failed to parse JSON:', parseError)
        console.error('Response text:', text)
        throw new Error('Invalid response from server')
      }

      if (response.ok) {
        setMessages(prev => [...prev, { role: 'ai', text: data.response || 'No response received' }])
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: `Error: ${data.error || 'Unknown error'}` }])
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, { role: 'ai', text: `Error: ${error.message || 'Failed to get response. Please try again.'}` }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={`chatbot-page app ${bgClass} ${timeOfDay} ${conditionClass}`}>
      <WeatherBackground />
      <div className="chatbot-page-header overlay">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Home
        </button>
        <h1>AI Chatbot</h1>
      </div>
      
      <div className="chatbot-container overlay">
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>AI Assistant</h3>
          </div>
          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chatbot-message ${msg.role}`}>
                <div className="chatbot-message-bubble">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}
                    components={{
                      a: (props) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                      ul: (props) => <ul style={{ paddingLeft: '1.25rem', margin: 0 }} {...props} />,
                      ol: (props) => <ol style={{ paddingLeft: '1.25rem', margin: 0 }} {...props} />,
                      li: (props) => <li style={{ marginBottom: '0.25rem' }} {...props} />,
                      strong: (props) => <strong style={{ fontWeight: 700 }} {...props} />,
                      code: (props) => <code style={{ background: 'rgba(0,0,0,0.1)', padding: '0.1rem 0.3rem', borderRadius: 4 }} {...props} />
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message ai">
                <div className="chatbot-message-bubble">
                  <div className="chatbot-loading">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="chatbot-input-container">
            <input
              ref={inputRef}
              type="text"
              className="chatbot-input"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className="chatbot-send"
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

