import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getBoards = async (skip = 0, limit = 100, category = null) => {
  const params = { skip, limit }
  if (category) params.category = category
  const response = await api.get('/boards', { params })
  return response.data
}

export const getBoard = async (boardId) => {
  const response = await api.get(`/boards/${boardId}`)
  return response.data
}

export const getRepos = async (filters = {}) => {
  const response = await api.get('/repos', { params: filters })
  return response.data
}

export const getRepo = async (repoId) => {
  const response = await api.get(`/repos/${repoId}`)
  return response.data
}

export const searchRepos = async (query, limit = 20) => {
  const response = await api.get('/search', { params: { q: query, limit } })
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}

