import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { WeatherProvider } from './contexts/WeatherContext'
import Home from './pages/Home'
import Weather from './pages/Weather'
import ChatBot from './pages/ChatBot'
import Onboarding from './components/Onboarding'
import UserGreeting from './components/UserGreeting'
import { getUserId } from './utils/userId'

function App() {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // Check if user has completed onboarding
    const userId = getUserId()
    const onboardingCompleted = localStorage.getItem('onboarding_completed')
    
    if (!userId || !onboardingCompleted) {
      setShowOnboarding(true)
    } else {
      // Update last_updated for returning users
      fetch(`/api/users/${userId}/visit`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      }).catch(console.error)
    }
    
    setIsChecking(false)
  }, [])

  const handleOnboardingComplete = async (userId) => {
    // Update last_updated timestamp on backend
    try {
      await fetch(`/api/users/${userId}/visit`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      })
    } catch (error) {
      console.error('Failed to update visit timestamp:', error)
    }
    
    setShowOnboarding(false)
  }

  // Show loading state while checking
  if (isChecking) {
    return null
  }

  // Show onboarding if needed
  if (showOnboarding) {
    return <Onboarding onComplete={handleOnboardingComplete} />
  }

  return (
    <WeatherProvider>
      <BrowserRouter>
        <UserGreeting />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/weather" element={<Weather />} />
          <Route path="/chatbot" element={<ChatBot />} />
        </Routes>
      </BrowserRouter>
    </WeatherProvider>
  )
}

export default App
