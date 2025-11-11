import React from 'react'
import { getUserId } from '../utils/userId'
import './UserGreeting.css'

const USER_NAME_KEY = 'app_user_name'

export default function UserGreeting() {
  const [name, setName] = React.useState(null)
  const [greeting, setGreeting] = React.useState('')

  React.useEffect(() => {
    // Get user name from localStorage
    const userName = localStorage.getItem(USER_NAME_KEY)
    if (userName) {
      setName(userName)
    } else {
      // Try to get from API if not in localStorage
      const userId = getUserId()
      if (userId) {
        fetch(`/api/users/${userId}`)
          .then(res => res.json())
          .then(data => {
            if (data.name) {
              setName(data.name)
              localStorage.setItem(USER_NAME_KEY, data.name)
            }
          })
          .catch(console.error)
      }
    }
  }, [])

  React.useEffect(() => {
    // Update greeting based on time of day
    const updateGreeting = () => {
      const hour = new Date().getHours()
      if (hour >= 5 && hour < 12) {
        setGreeting('Good morning')
      } else if (hour >= 12 && hour < 17) {
        setGreeting('Good afternoon')
      } else if (hour >= 17 && hour < 22) {
        setGreeting('Good evening')
      } else {
        setGreeting('Good evening')
      }
    }

    updateGreeting()
    // Update every minute to handle day transitions
    const interval = setInterval(updateGreeting, 60000)
    return () => clearInterval(interval)
  }, [])

  // Don't show if no name
  if (!name) {
    return null
  }

  return (
    <div className="user-greeting">
      <span className="greeting-text">
        {greeting}, <span className="user-name">{name}</span>
      </span>
    </div>
  )
}

