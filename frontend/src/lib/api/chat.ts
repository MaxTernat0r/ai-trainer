import { apiClient } from './client';
import type { Conversation, ConversationBrief } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

  // Streaming approval. Returns the raw fetch Response so the caller
  // (use-chat-stream) can pipe SSE through the same parser.
  approveProposal: async (
    proposalId: string,
    approved: boolean,
    accessToken: string | null,
    signal?: AbortSignal,
  ): Promise<Response> => {
    return fetch(`${API_BASE_URL}/api/v1/chat/proposals/${proposalId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({ approved }),
      signal,
    });
  },
};