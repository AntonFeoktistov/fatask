import apiClient from './client'
import type { TaskCreate, TaskResponse, TaskUpdate } from '@/types/api'

export const tasksApi = {
  async list(): Promise<TaskResponse[]> {
    const { data } = await apiClient.get<TaskResponse[]>('/api/tasks')
    return data
  },

  async create(payload: TaskCreate): Promise<TaskResponse> {
    const { data } = await apiClient.post<TaskResponse>('/api/tasks', payload)
    return data
  },

  async update(oid: string, payload: TaskUpdate): Promise<TaskResponse> {
    const { data } = await apiClient.patch<TaskResponse>(`/api/tasks/${oid}`, payload)
    return data
  },

  async remove(oid: string): Promise<void> {
    await apiClient.delete(`/api/tasks/${oid}`)
  },
}