import { apiClient } from './client';
import type { Conversation, ConversationBrief } from '@/types/chat';

export const chatApi = {
  getConversations: async (): Promise<ConversationBrief[]> => {
    return apiClient.get('chat/conversations').json<ConversationBrief[]>();
  },

  getConversation: async (id: string): Promise<Conversation> => {
    return apiClient.get(`chat/conversations/${id}`).json<Conversation>();
  },

  createConversation: async (title?: string): Promise<Conversation> => {
    return apiClient
      .post('chat/conversations', { json: { title: title ?? null } })
      .json<Conversation>();
  },

  deleteConversation: async (id: string): Promise<void> => {
    await apiClient.delete(`chat/conversations/${id}`);
  },
};
