'use client';

import { useState, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { useAuthStore } from '@/lib/stores/auth-store';
import type { AgentEvent, ToolProposal } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseChatStreamReturn {
  streamText: string;
  streamEvents: AgentEvent[];
  pendingProposals: Record<string, ToolProposal>;
  isStreaming: boolean;
  sendMessage: (conversationId: string, content: string) => Promise<void>;
  approveProposal: (
    conversationId: string,
    proposalId: string,
    approved: boolean,
    seedProposal?: ToolProposal,
  ) => Promise<void>;
  resetStream: () => void;
}

const QUERIES_TO_INVALIDATE_AFTER_WRITE = (qc: ReturnType<typeof useQueryClient>) => {
  qc.invalidateQueries({ queryKey: queryKeys.workouts.all });
  qc.invalidateQueries({ queryKey: queryKeys.nutrition.all });
  qc.invalidateQueries({ queryKey: queryKeys.analytics.all });
  qc.invalidateQueries({ queryKey: queryKeys.auth.profile() });
};

export function useChatStream(): UseChatStreamReturn {
  const [streamText, setStreamText] = useState('');
  const [streamEvents, setStreamEvents] = useState<AgentEvent[]>([]);
  const [pendingProposals, setPendingProposals] = useState<Record<string, ToolProposal>>({});
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();

  const resetStream = useCallback(() => {
    setStreamText('');
    setStreamEvents([]);
    setPendingProposals({});
  }, []);

  const collapseAfterStreamEnd = useCallback(() => {
    setStreamText('');
    setStreamEvents((prev) => {
      const resolvedIds = new Set(
        prev
          .filter((ev) => ev.type === 'tool_result')
          .map((ev) => (ev as { id: string }).id),
      );
      const remaining = prev.filter(
        (ev) => ev.type === 'tool_proposal' && !resolvedIds.has((ev as { id: string }).id),
      );
      return remaining;
    });
    // Drop proposals that reached a terminal state — the refetched
    // conversation now carries them as persisted tool_calls. Keep entries
    // still pending so the user can act on them after reload.
    setPendingProposals((prev) => {
      const next: Record<string, ToolProposal> = {};
      for (const [id, proposal] of Object.entries(prev)) {
        if (proposal.status === 'pending' || proposal.status === 'executing') {
          next[id] = proposal;
        }
      }
      return next;
    });
  }, []);

  const handleEvent = useCallback((event: AgentEvent) => {
    setStreamEvents((prev) => [...prev, event]);

    if (event.type === 'text') {
      setStreamText((prev) => prev + event.content);
      return;
    }
    if (event.type === 'tool_proposal') {
      setPendingProposals((prev) => ({
        ...prev,
        [event.id]: {
          id: event.id,
          name: event.name,
          arguments: event.arguments,
          summary: event.summary,
          status: 'pending',
        },
      }));
      return;
    }
    if (event.type === 'tool_executing') {
      setPendingProposals((prev) => {
        const existing = prev[event.id];
        if (!existing) return prev;
        return { ...prev, [event.id]: { ...existing, status: 'executing' } };
      });
      return;
    }
    if (event.type === 'tool_result') {
      setPendingProposals((prev) => {
        const existing = prev[event.id];
        if (!existing) return prev;
        return {
          ...prev,
          [event.id]: {
            ...existing,
            status: event.ok ? 'approved' : 'error',
            resultSummary: event.summary,
            result: event.result,
            error: event.ok ? undefined : event.summary,
          },
        };
      });
    }
  }, []);

  const consumeStream = useCallback(async (response: Response, signal: AbortSignal) => {
    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.status}`);
    }
    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      if (signal.aborted) break;
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data: ')) continue;
        const payload = trimmed.slice(6);
        if (payload === '[DONE]') continue;
        try {
          const parsed = JSON.parse(payload) as AgentEvent;
          handleEvent(parsed);
        } catch {
          // Legacy plain-text fallback (older non-agent endpoints)
          handleEvent({ type: 'text', content: payload });
        }
      }
    }
  }, [handleEvent]);

  const fetchWithRefresh = useCallback(async (
    url: string,
    init: RequestInit,
  ): Promise<Response> => {
    let token = useAuthStore.getState().accessToken;
    let response = await fetch(url, {
      ...init,
      headers: {
        ...(init.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (response.status === 401) {
      try {
        const refreshRes = await fetch('/api/auth/refresh', { method: 'POST' });
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          useAuthStore.getState().setAccessToken(data.accessToken);
          token = data.accessToken;
          response = await fetch(url, {
            ...init,
            headers: {
              ...(init.headers || {}),
              Authorization: `Bearer ${token}`,
            },
          });
        }
      } catch { /* refresh failed */ }
    }
    return response;
  }, []);

  const sendMessage = useCallback(
    async (conversationId: string, content: string) => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      resetStream();
      setIsStreaming(true);

      try {
        const response = await fetchWithRefresh(
          `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content }),
            signal: controller.signal,
          },
        );
        await consumeStream(response, controller.signal);
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') return;
        throw error;
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
        await queryClient.invalidateQueries({
          queryKey: queryKeys.chat.conversation(conversationId),
        });
        queryClient.invalidateQueries({
          queryKey: queryKeys.chat.conversations(),
        });
        QUERIES_TO_INVALIDATE_AFTER_WRITE(queryClient);
        collapseAfterStreamEnd();
      }
    },
    [collapseAfterStreamEnd, consumeStream, fetchWithRefresh, queryClient, resetStream],
  );

  const approveProposal = useCallback(
    async (
      conversationId: string,
      proposalId: string,
      approved: boolean,
      seedProposal?: ToolProposal,
    ) => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setPendingProposals((prev) => {
        const existing = prev[proposalId] ?? seedProposal;
        if (!existing) return prev;
        return {
          ...prev,
          [proposalId]: { ...existing, status: approved ? 'executing' : 'rejected' },
        };
      });

      setIsStreaming(true);

      try {
        const response = await fetchWithRefresh(
          `${API_BASE_URL}/api/v1/chat/proposals/${proposalId}/approve`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ approved }),
            signal: controller.signal,
          },
        );
        await consumeStream(response, controller.signal);
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') return;
        throw error;
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
        await queryClient.invalidateQueries({
          queryKey: queryKeys.chat.conversation(conversationId),
        });
        QUERIES_TO_INVALIDATE_AFTER_WRITE(queryClient);
        collapseAfterStreamEnd();
      }
    },
    [collapseAfterStreamEnd, consumeStream, fetchWithRefresh, queryClient],
  );

  return {
    streamText,
    streamEvents,
    pendingProposals,
    isStreaming,
    sendMessage,
    approveProposal,
    resetStream,
  };
}
