import React from 'react'
import { useWeatherContext } from '../contexts/WeatherContext'

export default function WeatherBackground() {
  const { conditionClass = 'default', timeOfDay = 'day' } = useWeatherContext()

  // Combine time of day with condition for background
  const bgClass = React.useMemo(() => {
    if (timeOfDay === 'night') return 'night'
    if (timeOfDay === 'sunrise') return 'sunrise'
    if (timeOfDay === 'sunset') return 'sunset'
    return conditionClass
  }, [timeOfDay, conditionClass])

  return (
    <div className={`weather-background scene ${bgClass} ${timeOfDay} ${conditionClass}`}>
      <div className="sun" />
      <div className="cloud cloud-1" />
      <div className="cloud cloud-2" />
      <div className="rain-layer">
        {Array.from({ length: 40 }).map((_, i) => (
          <span 
            key={i} 
            className="raindrop" 
            style={{ 
              left: `${(i * 2.5) % 100}%`, 
              animationDelay: `${(i % 10) * 0.2}s` 
            }} 
          />
        ))}
      </div>
      <div className="snow-layer">
        {Array.from({ length: 30 }).map((_, i) => (
          <span 
            key={i} 
            className="snowflake" 
            style={{ 
              left: `${(i * 3.3) % 100}%`, 
              animationDelay: `${(i % 10) * 0.3}s` 
            }} 
          />
        ))}
      </div>
    </div>
  )
}

