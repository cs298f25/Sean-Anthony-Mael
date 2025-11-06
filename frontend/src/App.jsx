import React, { useEffect, useMemo, useState } from 'react'
import ChatBot from './ChatBot'
function useWeather() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true
    async function fetchWeather() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch('/weather')
        if (!res.ok) {
          const text = await res.text()
          throw new Error(`HTTP ${res.status}: ${text.substring(0, 100)}`)
        }
        const contentType = res.headers.get('content-type')
        if (!contentType || !contentType.includes('application/json')) {
          const text = await res.text()
          throw new Error(`Expected JSON but got: ${contentType}. Response: ${text.substring(0, 100)}`)
        }
        const json = await res.json()
        if (isMounted) setData(json)
      } catch (e) {
        if (isMounted) setError(e.message)
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    fetchWeather()
    const id = setInterval(fetchWeather, 5 * 60 * 1000)
    return () => {
      isMounted = false
      clearInterval(id)
    }
  }, [])

  return { data, loading, error }
}

function normalizeCondition(conditionText) {
  const t = (conditionText || '').toLowerCase()
  if (t.includes('sun') || t.includes('clear')) return 'sunny'
  if (t.includes('rain') || t.includes('drizzle')) return 'rain'
  if (t.includes('snow') || t.includes('sleet')) return 'snow'
  if (t.includes('cloud')) return 'clouds'
  if (t.includes('storm') || t.includes('thunder')) return 'storm'
  return 'default'
}

function getTimeOfDay(sunrise, sunset) {
  if (!sunrise || !sunset) return 'day'
  
  const now = new Date()
  const today = now.toISOString().split('T')[0]
  
  // Parse sunrise and sunset times (format: "06:30 AM" or "18:45 PM")
  const parseTime = (timeStr) => {
    const [time, period] = timeStr.split(' ')
    const [hours, minutes] = time.split(':').map(Number)
    const hour24 = period === 'PM' && hours !== 12 ? hours + 12 : (period === 'AM' && hours === 12 ? 0 : hours)
    const date = new Date(`${today}T${String(hour24).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`)
    return date
  }
  
  const sunriseTime = parseTime(sunrise)
  const sunsetTime = parseTime(sunset)
  
  // Add 30 minutes buffer for sunrise/sunset transitions
  const sunriseStart = new Date(sunriseTime.getTime() - 30 * 60 * 1000)
  const sunriseEnd = new Date(sunriseTime.getTime() + 30 * 60 * 1000)
  const sunsetStart = new Date(sunsetTime.getTime() - 30 * 60 * 1000)
  const sunsetEnd = new Date(sunsetTime.getTime() + 30 * 60 * 1000)
  
  if (now >= sunriseStart && now <= sunriseEnd) {
    return 'sunrise'
  } else if (now >= sunsetStart && now <= sunsetEnd) {
    return 'sunset'
  } else if (now >= sunriseEnd && now < sunsetStart) {
    return 'day'
  } else {
    return 'night'
  }
}

export default function App() {
  const { data, loading, error } = useWeather()

  const conditionClass = useMemo(() => normalizeCondition(data?.condition_text), [data])
  const timeOfDay = useMemo(() => getTimeOfDay(data?.sunrise, data?.sunset), [data])
  
  // Combine time of day with condition for background
  const bgClass = useMemo(() => {
    if (timeOfDay === 'night') return 'night'
    if (timeOfDay === 'sunrise') return 'sunrise'
    if (timeOfDay === 'sunset') return 'sunset'
    return conditionClass
  }, [timeOfDay, conditionClass])

  return (
    <div className={`app ${bgClass} ${timeOfDay} ${conditionClass}`}>
      <div className="overlay">
        <h1>Weather {data ? `in ${data.city}, ${data.region}` : ''}</h1>
        {loading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        {data && (
          <div className="card">
            <div className="row">
              <span className="label">City</span>
              <span className="value">{data.city}, {data.region}</span>
            </div>
            <div className="row">
              <span className="label">Temperature</span>
              <span className="value">{Math.round(data.temperature_f)}°F</span>
            </div>
            <div className="row">
              <span className="label">Feels like</span>
              <span className="value">{Math.round(data.feels_like_f)}°F</span>
            </div>
            <div className="row">
              <span className="label">Condition</span>
              <span className="value">{data.condition_text}</span>
            </div>
            {data.sunrise && (
              <div className="row small">
                <span className="label">Sunrise</span>
                <span className="value">{data.sunrise}</span>
              </div>
            )}
            {data.sunset && (
              <div className="row small">
                <span className="label">Sunset</span>
                <span className="value">{data.sunset}</span>
              </div>
            )}
            <div className="row small">
              <span className="label">Last updated</span>
              <span className="value">{new Date(data.last_updated.replace(' ', 'T')).toLocaleString()}</span>
            </div>
          </div>
        )}
      </div>

      {/* Scene elements for simple background animations */}
      <div className="scene">
        <div className="sun" />
        <div className="cloud cloud-1" />
        <div className="cloud cloud-2" />
        <div className="rain-layer">
          {Array.from({ length: 40 }).map((_, i) => (
            <span key={i} className="raindrop" style={{ left: `${(i * 2.5) % 100}%`, animationDelay: `${(i % 10) * 0.2}s` }} />
          ))}
        </div>
        <div className="snow-layer">
          {Array.from({ length: 30 }).map((_, i) => (
            <span key={i} className="snowflake" style={{ left: `${(i * 3.3) % 100}%`, animationDelay: `${(i % 10) * 0.3}s` }} />
          ))}
        </div>
      </div>
      
      {/* AI Chat Bot */}
      <ChatBot />
    </div>
  )
}


