'use client';

import { useState, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { useAuthStore } from '@/lib/stores/auth-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseChatStreamReturn {
  streamMessage: string;
  isStreaming: boolean;
  sendMessage: (conversationId: string, content: string) => Promise<void>;
}

export function useChatStream(): UseChatStreamReturn {
  const [streamMessage, setStreamMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();

  const sendMessage = useCallback(
    async (conversationId: string, content: string) => {
      // Abort any in-flight stream
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setStreamMessage('');
      setIsStreaming(true);

      try {
        const token = useAuthStore.getState().accessToken;

        const response = await fetch(
          `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({ content }),
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`Chat request failed: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let accumulated = '';
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE lines
          const lines = buffer.split('\n');
          // Keep the last potentially incomplete line in the buffer
          buffer = lines.pop() ?? '';

          for (const line of lines) {
            const trimmed = line.trim();

            if (trimmed.startsWith('data: ')) {
              const data = trimmed.slice(6);

              if (data === '[DONE]') {
                continue;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  accumulated += parsed.content;
                  setStreamMessage(accumulated);
                }
              } catch {
                // If not valid JSON, treat data as plain text chunk
                accumulated += data;
                setStreamMessage(accumulated);
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          // Request was intentionally aborted
          return;
        }
        throw error;
      } finally {
        setIsStreaming(false);
        abortRef.current = null;

        // Invalidate the conversation query to refetch complete messages
        queryClient.invalidateQueries({
          queryKey: queryKeys.chat.conversation(conversationId),
        });
        queryClient.invalidateQueries({
          queryKey: queryKeys.chat.conversations(),
        });
      }
    },
    [queryClient]
  );

  return { streamMessage, isStreaming, sendMessage };
}
