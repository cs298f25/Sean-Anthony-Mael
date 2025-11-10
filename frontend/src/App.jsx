import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { WeatherProvider } from './contexts/WeatherContext'
import Home from './pages/Home'
import Weather from './pages/Weather'
import ChatBot from './pages/ChatBot'
import { getOrCreateUserId } from './utils/userId'

function App() {
  useEffect(() => {
    // Initialize user ID on app load
    getOrCreateUserId().catch(console.error)
  }, [])

  return (
    <WeatherProvider>
      <BrowserRouter>
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
