import React from 'react'
import { Link } from 'react-router-dom'
import { useWeatherContext } from '../contexts/WeatherContext'
import WeatherBackground from '../components/WeatherBackground'

export default function Home() {
  const { conditionClass, timeOfDay } = useWeatherContext()

  const bgClass = React.useMemo(() => {
    if (timeOfDay === 'night') return 'night'
    if (timeOfDay === 'sunrise') return 'sunrise'
    if (timeOfDay === 'sunset') return 'sunset'
    return conditionClass
  }, [timeOfDay, conditionClass])

  return (
    <div className={`home-page app ${bgClass} ${timeOfDay} ${conditionClass}`}>
      <WeatherBackground />
      <div className="home-container overlay">
        <h1>Zen</h1>
        <p>your personal study assistant</p>
        <div className="home-links">
          <Link to="/weather" className="home-link">
            <div className="home-link-card">
              <h2>Weather</h2>
              <p>Check current weather conditions</p>
            </div>
          </Link>
          <Link to="/chatbot" className="home-link">
            <div className="home-link-card">
              <h2>AI Chatbot</h2>
              <p>Chat with our AI assistant</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}

