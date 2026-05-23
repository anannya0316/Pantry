const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

export const signup = async (data) => {
  const res = await fetch(`${BASE_URL}/auth/create-account`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
  return res.json()
}

export const googleAuth = async (credential, mode, preferences = {}) => {
  const res = await fetch(`${BASE_URL}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential, mode, ...preferences })
  })
  return res.json()
}

export const login = async (data) => {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
  return res.json()
}

// Inventory APIs
export const addInventoryItems = async (items, userId) => {
  const res = await fetch(`${BASE_URL}/inventory/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "user-id": userId },
    body: JSON.stringify({ items })
  })
  return res.json()
}

export const getInventory = async (userId) => {
  const res = await fetch(`${BASE_URL}/inventory/`, {
    method: "GET",
    headers: { "Content-Type": "application/json", "user-id": userId }
  })
  return res.json()
}

export const getProfile = async (userId) => {
  const res = await fetch(`${BASE_URL}/profile/`, {
    method: "GET",
    headers: { "Content-Type": "application/json", "user-id": userId }
  })
  return res.json()
}

export const updateGoals = async (goals, userId) => {
  const res = await fetch(`${BASE_URL}/profile/update-goals`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "user-id": userId },
    body: JSON.stringify({ goals })
  })
  return res.json()
}

export const updateProfile = async (data, userId) => {
  const res = await fetch(`${BASE_URL}/profile/update`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "user-id": userId },
    body: JSON.stringify(data)
  })
  return res.json()
}

export const getNotifications = async (userId) => {
  const res = await fetch(`${BASE_URL}/notifications/`, {
    method: "GET",
    headers: { "Content-Type": "application/json", "user-id": userId }
  })
  return res.json()
}