import api from './api'
import type { ChatResponse, Conversation } from '../types'

export const chatService = {
  ask: (payload: { message: string; portfolio_id?: number; conversation_id?: number }) =>
    api.post<ChatResponse>('/chat', payload).then((response) => response.data),
  conversations: () => api.get<Conversation[]>('/conversations').then((response) => response.data),
  conversation: (id: number) => api.get<Conversation & { messages: Array<{ id: number; role: 'user' | 'assistant'; content: string; created_at: string }> }>(`/conversations/${id}`).then((response) => response.data),
  create: (title?: string) => api.post<Conversation>('/conversations', { title }).then((response) => response.data),
  remove: (id: number) => api.delete(`/conversations/${id}`),
}
