import axios from 'axios'
import type { Expense } from '../types/expense'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}

export const submitAudio = async (audioBlob: Blob): Promise<ApiResponse<Expense>> => {
  const formData = new FormData()
  formData.append('file', audioBlob, 'recording.wav')

  const response = await api.post('/audio/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const confirmExpense = async (expense: Expense): Promise<ApiResponse<void>> => {
  const response = await api.post('/expenses', expense)
  return response.data
}