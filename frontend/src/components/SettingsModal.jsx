import React, { useState, useEffect } from 'react'
import { updateUserName } from '../utils/userId'
import './SettingsModal.css'

const USER_NAME_KEY = 'app_user_name'

export default function SettingsModal({ isOpen, onClose, currentName, onNameUpdate }) {
  const [name, setName] = useState(currentName || '')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setName(currentName || '')
      setError('')
      setSuccess(false)
    }
  }, [isOpen, currentName])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!name.trim()) {
      setError('Please enter your name')
      return
    }

    if (name.trim() === currentName) {
      onClose()
      return
    }

    setIsLoading(true)
    setError('')
    setSuccess(false)

    try {
      await updateUserName(name.trim())
      localStorage.setItem(USER_NAME_KEY, name.trim())
      onNameUpdate(name.trim())
      setSuccess(true)
      
      // Close modal after a brief success message
      setTimeout(() => {
        onClose()
        setSuccess(false)
      }, 1000)
    } catch (err) {
      setError(err.message || 'Failed to update name. Please try again.')
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    if (!isLoading) {
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="settings-modal-overlay" onClick={handleClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-modal-header">
          <h2>Settings</h2>
          <button className="settings-modal-close" onClick={handleClose} disabled={isLoading}>
            ×
          </button>
        </div>
        
        <div className="settings-modal-content">
          <form onSubmit={handleSubmit} className="settings-form">
            <div className="settings-field">
              <label htmlFor="user-name">Your Name</label>
              <input
                id="user-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="settings-input"
                autoFocus
                disabled={isLoading}
                maxLength={50}
              />
            </div>
            
            {error && <div className="settings-error">{error}</div>}
            {success && <div className="settings-success">Name updated successfully!</div>}
            
            <div className="settings-actions">
              <button
                type="button"
                className="settings-button settings-button-cancel"
                onClick={handleClose}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="settings-button settings-button-save"
                disabled={isLoading || !name.trim()}
              >
                {isLoading ? (
                  <>
                    <span className="settings-spinner"></span>
                    <span>Saving...</span>
                  </>
                ) : (
                  'Save'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

