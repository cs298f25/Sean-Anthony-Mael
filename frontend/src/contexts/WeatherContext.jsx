import React, { createContext, useContext, useState, useEffect } from 'react'

const WeatherContext = createContext()

export function useWeatherContext() {
  const context = useContext(WeatherContext)
  if (!context) {
    throw new Error('useWeatherContext must be used within a WeatherProvider')
  }
  return context
}

function normalizeCondition(conditionText) {
  if (!conditionText) return 'default'
  const t = conditionText.toLowerCase()
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
  
  const parseTime = (timeStr) => {
    const [time, period] = timeStr.split(' ')
    const [hours, minutes] = time.split(':').map(Number)
    const hour24 = period === 'PM' && hours !== 12 ? hours + 12 : (period === 'AM' && hours === 12 ? 0 : hours)
    const date = new Date(`${today}T${String(hour24).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`)
    return date
  }
  
  const sunriseTime = parseTime(sunrise)
  const sunsetTime = parseTime(sunset)
  
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

export function WeatherProvider({ children }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true
    async function fetchWeather() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch('/api/weather')
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

  const conditionClass = normalizeCondition(data?.condition_text)
  const timeOfDay = getTimeOfDay(data?.sunrise, data?.sunset)

  const value = {
    data,
    loading,
    error,
    conditionClass,
    timeOfDay
  }

  return (
    <WeatherContext.Provider value={value}>
      {children}
    </WeatherContext.Provider>
  )
}

