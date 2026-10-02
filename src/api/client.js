import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 3000,
})

// Fetch skills with query string (GET /skills?q=...)
export async function fetchSkills(query = '') {
  const response = await client.get('/skills', {
    params: { q: query }
  })
  return response.data
}

// Fetch role families (GET /roles)
export async function fetchRoles() {
  const response = await client.get('/roles')
  return response.data
}

// Fetch role matches (POST /match)
export async function fetchMatch(skills = []) {
  const response = await client.post('/match', { skills })
  return response.data
}

// Check API health (GET /health)
export async function checkApiHealth() {
  const response = await client.get('/health')
  return response.data
}

export default client
