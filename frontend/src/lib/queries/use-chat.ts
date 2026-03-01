'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { chatApi } from '@/lib/api/chat';
import type { Conversation, ConversationBrief } from '@/types/chat';

export function useConversations() {
  return useQuery<ConversationBrief[]>({
    queryKey: queryKeys.chat.conversations(),
    queryFn: chatApi.getConversations,
  });
}

export function useConversation(id: string | undefined) {
  return useQuery<Conversation>({
    queryKey: queryKeys.chat.conversation(id!),
    queryFn: () => chatApi.getConversation(id!),
    enabled: !!id,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();

  return useMutation<Conversation, Error, string | undefined>({
    mutationFn: (title) => chatApi.createConversation(title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chat.conversations() });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => chatApi.deleteConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chat.conversations() });
    },
  });
}
