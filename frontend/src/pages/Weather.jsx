import React, { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWeatherContext } from '../contexts/WeatherContext'
import WeatherBackground from '../components/WeatherBackground'

export default function Weather() {
  const { data, loading, error, conditionClass, timeOfDay } = useWeatherContext()
  const navigate = useNavigate()

  const bgClass = useMemo(() => {
    if (timeOfDay === 'night') return 'night'
    if (timeOfDay === 'sunrise') return 'sunrise'
    if (timeOfDay === 'sunset') return 'sunset'
    return conditionClass
  }, [timeOfDay, conditionClass])

  return (
    <div className={`weather-page app ${bgClass} ${timeOfDay} ${conditionClass}`}>
      <div className="overlay">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Home
        </button>
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

      <WeatherBackground />
    </div>
  )
}

