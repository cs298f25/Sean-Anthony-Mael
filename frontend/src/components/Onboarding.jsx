import React, { useState, useEffect } from 'react'
import './Onboarding.css'

export default function Onboarding({ onComplete }) {
  const [name, setName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showAnimation, setShowAnimation] = useState(true)

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setShowAnimation(false), 500)
    return () => clearTimeout(timer)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!name.trim()) {
      setError('Please enter your name')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Get user's location
      let latitude = null
      let longitude = null

      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            timeout: 5000,
            enableHighAccuracy: false
          })
        })
        latitude = position.coords.latitude
        longitude = position.coords.longitude
      } catch (geoError) {
        console.log('Geolocation not available or denied, continuing without location')
        // Continue without location - it's optional
      }

      // Create user with name and location
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          latitude,
          longitude,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to create user')
      }

      const data = await response.json()
      
      // Store user ID in localStorage
      localStorage.setItem('app_user_id', data.user_id)
      localStorage.setItem('app_user_name', name.trim())
      localStorage.setItem('onboarding_completed', 'true')

      // Call onComplete callback
      onComplete(data.user_id)
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
      setIsLoading(false)
    }
  }

  return (
    <div className={`onboarding-container ${showAnimation ? 'entering' : 'entered'}`}>
      <div className="onboarding-background">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
        </div>
      </div>
      
      <div className="onboarding-content">
        <div className="onboarding-card">
          <div className="welcome-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="45" stroke="currentColor" strokeWidth="3" fill="none" className="icon-circle"/>
              <path d="M35 50 L45 60 L65 40" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="icon-check"/>
            </svg>
          </div>
          
          <h1 className="onboarding-title">Welcome to Zen</h1>
          <p className="onboarding-subtitle">Let's personalize your experience</p>
          
          <form onSubmit={handleSubmit} className="onboarding-form">
            <div className="input-group">
              <label htmlFor="name">What's your name?</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="name-input"
                autoFocus
                disabled={isLoading}
                maxLength={50}
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button 
              type="submit" 
              className="submit-button"
              disabled={isLoading || !name.trim()}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  <span>Creating your profile...</span>
                </>
              ) : (
                'Get Started'
              )}
            </button>
          </form>
          
          <p className="privacy-note">
            We'll use your location to provide personalized weather information
          </p>
        </div>
      </div>
    </div>
  )
}

