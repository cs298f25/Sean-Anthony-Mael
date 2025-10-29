import React, { useEffect, useMemo, useState } from 'react'
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
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
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

export default function App() {
  const { data, loading, error } = useWeather()

  const bgClass = useMemo(() => normalizeCondition(data?.condition_text), [data])

  return (
    <div className={`app ${bgClass}`}>
      <div className="overlay">
        <h1>Weather in Bethlehem, PA</h1>
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
    </div>
  )
}


