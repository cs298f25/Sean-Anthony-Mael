// User ID management - generates and stores a unique device ID

const USER_ID_KEY = 'app_user_id';
const USER_NAME_KEY = 'app_user_name';

/**
 * Get or create a user ID for this device
 * @returns {Promise<string>} User ID
 */
export async function getOrCreateUserId() {
  let userId = localStorage.getItem(USER_ID_KEY);
  
  if (!userId) {
    // Register with backend to get a user ID
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: localStorage.getItem(USER_NAME_KEY) || null,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        // Use the user_id from the backend
        userId = data.user_id;
        localStorage.setItem(USER_ID_KEY, userId);
      } else {
        // If backend fails, generate a local ID as fallback
        userId = generateUserId();
        localStorage.setItem(USER_ID_KEY, userId);
      }
    } catch (error) {
      console.error('Failed to register user with backend:', error);
      // Generate a local ID as fallback
      userId = generateUserId();
      localStorage.setItem(USER_ID_KEY, userId);
    }
  }
  
  return userId;
}

/**
 * Generate a unique user ID
 * @returns {string} User ID
 */
function generateUserId() {
  return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Get current user ID from localStorage
 * @returns {string|null} User ID or null
 */
export function getUserId() {
  return localStorage.getItem(USER_ID_KEY);
}

/**
 * Update user location
 * @param {number} latitude 
 * @param {number} longitude 
 */
export async function updateUserLocation(latitude, longitude) {
  const userId = getUserId();
  if (!userId) return;
  
  try {
    await fetch(`/api/users/${userId}/location`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ latitude, longitude }),
    });
  } catch (error) {
    console.error('Failed to update user location:', error);
  }
}

/**
 * Update user name
 * @param {string} name 
 * @returns {Promise<void>}
 */
export async function updateUserName(name) {
  const userId = getUserId();
  if (!userId) {
    throw new Error('User ID not found');
  }
  
  const response = await fetch(`/api/users/${userId}/name`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Failed to update name' }));
    throw new Error(errorData.error || 'Failed to update name');
  }
  
  localStorage.setItem(USER_NAME_KEY, name);
}

