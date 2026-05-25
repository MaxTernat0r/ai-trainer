'use client';

import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Send,
  MessageSquare,
  Plus,
  Bot,
  User,
  Dumbbell,
  UtensilsCrossed,
  HelpCircle,
  PanelLeftClose,
  PanelLeft,
  Loader2,
  Menu,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { cn } from '@/lib/utils';
import {
  useConversations,
  useConversation,
  useCreateConversation,
} from '@/lib/queries/use-chat';
import { useChatStream } from '@/lib/hooks/use-chat-stream';
import type {
  AgentEvent,
  ChatMessage,
  PersistedToolCall,
  ToolProposal,
} from '@/types/chat';
import { ToolCard } from '@/components/chat/tool-card';
import { ToolProposalCard } from '@/components/chat/tool-proposal-card';

const quickActions = [
  { label: 'Составь тренировку', icon: Dumbbell },
  { label: 'Посоветуй питание', icon: UtensilsCrossed },
  { label: 'Как улучшить технику?', icon: HelpCircle },
];

interface AgentBubbleSegments {
  textChunks: string[];
  toolCards: { id: string; name: string; summary: string; state: 'running' | 'ok' | 'error' }[];
  proposalIds: string[];
}

function partitionEvents(events: AgentEvent[]): AgentBubbleSegments {
  const textChunks: string[] = [];
  // Use a map to merge tool_use_start + later tool_result on the same id.
  const toolCardsMap = new Map<string, AgentBubbleSegments['toolCards'][number]>();
  const proposalIds: string[] = [];

  for (const ev of events) {
    if (ev.type === 'text') {
      textChunks.push(ev.content);
    } else if (ev.type === 'tool_use_start') {
      toolCardsMap.set(ev.id, {
        id: ev.id,
        name: ev.name,
        summary: ev.summary,
        state: 'running',
      });
    } else if (ev.type === 'tool_result') {
      const existing = toolCardsMap.get(ev.id);
      // Skip if this id is a proposal — proposal cards handle their own state
      if (proposalIds.includes(ev.id)) continue;
      toolCardsMap.set(ev.id, {
        id: ev.id,
        name: ev.name,
        summary: ev.summary,
        state: ev.ok ? 'ok' : 'error',
      });
      if (!existing) {
        // tool_result без предшествующего tool_use_start — например, после approve
      }
    } else if (ev.type === 'tool_proposal') {
      proposalIds.push(ev.id);
    }
  }

  return { textChunks, toolCards: [...toolCardsMap.values()], proposalIds };
}

export default function ChatPage() {
  const [inputValue, setInputValue] = useState('');
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>(undefined);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [pendingUserMessage, setPendingUserMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: conversations, isLoading: conversationsLoading } = useConversations();
  const { data: activeConversation, isLoading: conversationLoading } = useConversation(activeConversationId);
  const createConversation = useCreateConversation();

  const {
    streamText,
    streamEvents,
    pendingProposals,
    isStreaming,
    sendMessage: sendStreamMessage,
    approveProposal,
    resetStream,
  } = useChatStream();

  useEffect(() => {
    if (!activeConversationId && conversations && conversations.length > 0) {
      setActiveConversationId(conversations[0].id);
    }
  }, [conversations, activeConversationId]);

  // When switching conversation, clear stream state
  useEffect(() => {
    resetStream();
  }, [activeConversationId, resetStream]);

  const timeline = useMemo(() => {
    type TimelineItem =
      | { kind: 'message'; data: ChatMessage; sortKey: string }
      | { kind: 'tool'; data: PersistedToolCall; sortKey: string };

    const persistedMessages = activeConversation?.messages ?? [];
    const persistedToolCalls = activeConversation?.tool_calls ?? [];

    const items: TimelineItem[] = [];

    for (const m of persistedMessages) {
      items.push({ kind: 'message', data: m, sortKey: m.created_at });
    }

    // Hide persisted tool cards whose ids are currently live in pendingProposals
    // (the streaming bubble owns them until collapseAfterStreamEnd fires).
    for (const tc of persistedToolCalls) {
      if (pendingProposals[tc.id]) continue;
      items.push({ kind: 'tool', data: tc, sortKey: tc.created_at });
    }

    items.sort((a, b) => a.sortKey.localeCompare(b.sortKey));

    if (pendingUserMessage) {
      const lastUserInBase = [...persistedMessages].reverse().find((m) => m.role === 'user');
      const alreadyShown = lastUserInBase?.content.trim() === pendingUserMessage.trim();
      if (!alreadyShown) {
        items.push({
          kind: 'message',
          data: {
            id: '__pending_user__',
            role: 'user',
            content: pendingUserMessage,
            created_at: new Date().toISOString(),
          },
          sortKey: new Date().toISOString(),
        });
      }
    }

    if (isStreaming || streamEvents.length > 0) {
      items.push({
        kind: 'message',
        data: {
          id: '__streaming__',
          role: 'assistant',
          content: streamText,
          created_at: new Date().toISOString(),
          tool_events: streamEvents,
        },
        sortKey: '￿', // always last
      });
    }

    return items;
  }, [
    activeConversation?.messages,
    activeConversation?.tool_calls,
    pendingProposals,
    pendingUserMessage,
    isStreaming,
    streamEvents,
    streamText,
  ]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [timeline, streamText, streamEvents, scrollToBottom]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    let conversationId = activeConversationId;
    if (!conversationId) {
      try {
        const newConv = await createConversation.mutateAsync(undefined);
        conversationId = newConv.id;
        setActiveConversationId(newConv.id);
      } catch {
        toast.error('Не удалось создать диалог');
        return;
      }
    }

    setInputValue('');
    setPendingUserMessage(text.trim());

    try {
      await sendStreamMessage(conversationId, text.trim());
    } catch {
      toast.error('Ошибка отправки сообщения');
    } finally {
      setPendingUserMessage(null);
    }
  };

  const handleApproveProposal = async (
    proposalId: string,
    approved: boolean,
    seedProposal?: ToolProposal,
  ) => {
    if (!activeConversationId || isStreaming) return;
    try {
      await approveProposal(activeConversationId, proposalId, approved, seedProposal);
    } catch {
      toast.error('Не удалось обработать действие');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const handleNewConversation = () => {
    createConversation.mutate(undefined, {
      onSuccess: (newConv) => {
        setActiveConversationId(newConv.id);
      },
      onError: () => {
        toast.error('Не удалось создать диалог');
      },
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  const hasMessages = timeline.length > 0;

  const renderConversationList = (onSelect?: () => void) => (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 items-center justify-between border-b border-[rgb(var(--theme-shade-rgb)/55%)] p-4">
        <h2 className="font-semibold">Диалоги</h2>
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => {
            handleNewConversation();
            onSelect?.();
          }}
          disabled={createConversation.isPending}
        >
          {createConversation.isPending ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Plus className="size-4" />
          )}
        </Button>
      </div>
      <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
        <div className="flex flex-col gap-2">
          {conversationsLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="glass-lane flex items-center gap-3 rounded-lg px-3 py-2.5">
                  <Skeleton className="size-4 shrink-0 rounded" />
                  <div className="min-w-0 flex-1">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="mt-1 h-3 w-20" />
                  </div>
                </div>
              ))}
            </>
          ) : conversations && conversations.length > 0 ? (
            conversations.map((conv) => (
              <div
                key={conv.id}
                role="button"
                tabIndex={0}
                onClick={() => {
                  setActiveConversationId(conv.id);
                  onSelect?.();
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setActiveConversationId(conv.id);
                    onSelect?.();
                  }
                }}
                className={cn(
                  'group glass-lane flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-200',
                  activeConversationId === conv.id
                    ? 'border-primary/45 bg-primary/12 shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_20px_rgb(var(--brand-accent)/_10%)]'
                    : 'border-[rgb(var(--theme-shade-rgb)/30%)] hover:border-primary/35 hover:bg-white/[0.055]'
                )}
              >
                <MessageSquare
                  className={cn(
                    'size-4 shrink-0',
                    activeConversationId === conv.id ? 'text-primary' : 'text-muted-foreground'
                  )}
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{conv.title ?? 'Новый диалог'}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(conv.created_at).toLocaleDateString('ru-RU')}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              Нет диалогов. Создайте новый!
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const persistedToProposal = (tc: PersistedToolCall): ToolProposal => ({
    id: tc.id,
    name: tc.tool_name,
    arguments: tc.arguments,
    summary: tc.summary,
    status: tc.status,
    resultSummary: tc.result_summary ?? undefined,
    error: tc.error ?? undefined,
  });

  const renderAssistantBubble = (message: ChatMessage) => {
    if (message.id !== '__streaming__') {
      // Persisted assistant message — just markdown text. Tool history is on the
      // streaming bubble; once the turn is committed only text survives.
      return (
        <div className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      );
    }

    const events = message.tool_events ?? [];
    const segments = partitionEvents(events);
    const text = segments.textChunks.join('');
    const showThinkingDots = !text && segments.toolCards.length === 0 && segments.proposalIds.length === 0;

    return (
      <div className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
        {showThinkingDots ? (
          <div className="flex items-center gap-1 py-1">
            <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
            <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
            <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60" />
          </div>
        ) : (
          <>
            {text && <ReactMarkdown>{text}</ReactMarkdown>}
            {segments.toolCards.map((card) => (
              <ToolCard key={card.id} summary={card.summary} state={card.state} />
            ))}
            {segments.proposalIds.map((pid) => {
              const proposal: ToolProposal | undefined = pendingProposals[pid];
              if (!proposal) return null;
              return (
                <ToolProposalCard
                  key={pid}
                  proposal={proposal}
                  disabled={isStreaming}
                  onApprove={() => handleApproveProposal(pid, true)}
                  onReject={() => handleApproveProposal(pid, false)}
                />
              );
            })}
            {isStreaming && text && (
              <span className="ml-1 inline-block size-2 animate-pulse rounded-full bg-current" />
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="cockpit-panel flex h-full min-h-0 overflow-hidden rounded-lg">
      {/* Sidebar - desktop */}
      <aside
        className={cn(
          'hidden min-h-0 flex-col border-r border-[rgb(var(--theme-shade-rgb)/55%)] bg-black/[0.18] transition-all duration-300',
          sidebarVisible ? 'md:flex md:w-80' : 'md:hidden'
        )}
      >
        <div className="flex shrink-0 items-center justify-between border-b border-[rgb(var(--theme-shade-rgb)/55%)] p-4">
          <h2 className="font-semibold">Диалоги</h2>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={handleNewConversation}
              disabled={createConversation.isPending}
            >
              {createConversation.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Plus className="size-4" />
              )}
            </Button>
            <Button variant="ghost" size="icon-xs" onClick={() => setSidebarVisible(false)}>
              <PanelLeftClose className="size-4" />
            </Button>
          </div>
        </div>
        <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
          <div className="flex flex-col gap-2">
            {conversationsLoading ? (
              <>
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="glass-lane flex items-center gap-3 rounded-lg px-3 py-2.5">
                    <Skeleton className="size-4 shrink-0 rounded" />
                    <div className="min-w-0 flex-1">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="mt-1 h-3 w-20" />
                    </div>
                  </div>
                ))}
              </>
            ) : conversations && conversations.length > 0 ? (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => setActiveConversationId(conv.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setActiveConversationId(conv.id);
                    }
                  }}
                  className={cn(
                    'group glass-lane flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-200',
                    activeConversationId === conv.id
                      ? 'border-primary/45 bg-primary/12 shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_20px_rgb(var(--brand-accent)/_10%)]'
                      : 'border-[rgb(var(--theme-shade-rgb)/30%)] hover:border-primary/35 hover:bg-white/[0.055]'
                  )}
                >
                  <MessageSquare
                    className={cn(
                      'size-4 shrink-0',
                      activeConversationId === conv.id ? 'text-primary' : 'text-muted-foreground'
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{conv.title ?? 'Новый диалог'}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(conv.created_at).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="px-3 py-6 text-center text-sm text-muted-foreground">
                Нет диалогов. Создайте новый!
              </p>
            )}
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex shrink-0 items-center gap-3 border-b border-[rgb(var(--theme-shade-rgb)/55%)] px-4 py-3">
          <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon-xs" className="md:hidden">
                <Menu className="size-4" />
                <span className="sr-only">Открыть список диалогов</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 max-w-[85vw] p-0" showCloseButton={false}>
              <SheetHeader className="sr-only">
                <SheetTitle>Диалоги</SheetTitle>
              </SheetHeader>
              {renderConversationList(() => setMobileSidebarOpen(false))}
            </SheetContent>
          </Sheet>
          {!sidebarVisible && (
            <Button
              variant="ghost"
              size="icon-xs"
              className="hidden md:inline-flex"
              onClick={() => setSidebarVisible(true)}
            >
              <PanelLeft className="size-4" />
            </Button>
          )}
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-lg border border-primary/35 bg-primary/12">
              <Bot className="size-4 text-primary" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">Чат с ИИ-тренером</h2>
              <p className="text-xs text-muted-foreground">
                {isStreaming ? 'Думает и работает...' : 'Онлайн (агент)'}
              </p>
            </div>
          </div>
        </div>

        <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {conversationLoading ? (
              <div className="flex flex-col gap-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className={cn('flex gap-3', i % 2 === 0 ? 'flex-row-reverse' : 'flex-row')}
                  >
                    <Skeleton className="size-8 shrink-0 rounded-full" />
                    <Skeleton className={cn('h-20 rounded-2xl', i % 2 === 0 ? 'w-1/3' : 'w-2/3')} />
                  </div>
                ))}
              </div>
            ) : !hasMessages ? (
              <div className="flex flex-col items-center justify-center gap-4 py-16">
                <div className="flex size-16 items-center justify-center rounded-full bg-primary/10">
                  <Bot className="size-8 text-primary" />
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold">ИИ-тренер</h3>
                  <p className="mt-1 max-w-md text-sm text-muted-foreground">
                    Я могу не только отвечать словами, но и реально менять твой профиль,
                    создавать планы, записывать вес и анализировать прогресс. Любое
                    важное действие сначала покажу карточкой с подтверждением.
                  </p>
                </div>
              </div>
            ) : (
              timeline.map((item) => {
                if (item.kind === 'tool') {
                  const tc = item.data;
                  const proposal = persistedToProposal(tc);
                  return (
                    <div key={`tool-${tc.id}`} className="flex gap-3">
                      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
                        <Bot className="size-4" />
                      </div>
                      <div className="max-w-[80%] flex-1">
                        <ToolProposalCard
                          proposal={proposal}
                          disabled={isStreaming}
                          onApprove={() => handleApproveProposal(tc.id, true, proposal)}
                          onReject={() => handleApproveProposal(tc.id, false, proposal)}
                        />
                      </div>
                    </div>
                  );
                }

                const message = item.data;
                return (
                  <div
                    key={message.id}
                    className={cn(
                      'flex gap-3',
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    )}
                  >
                    <div
                      className={cn(
                        'flex size-8 shrink-0 items-center justify-center rounded-full',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      )}
                    >
                      {message.role === 'user' ? <User className="size-4" /> : <Bot className="size-4" />}
                    </div>

                    <div
                      className={cn(
                        'max-w-[80%] rounded-2xl px-4 py-2.5',
                        message.role === 'user' ? 'bg-primary/15 text-foreground' : 'bg-muted'
                      )}
                    >
                      {message.role === 'user' ? (
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                      ) : (
                        renderAssistantBubble(message)
                      )}
                      {message.id !== '__streaming__' && (
                        <p
                          className={cn(
                            'mt-1 text-right text-xs',
                            message.role === 'user'
                              ? 'text-primary-foreground/70'
                              : 'text-muted-foreground'
                          )}
                        >
                          {formatTime(message.created_at)}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {!hasMessages && !conversationLoading && (
          <div className="shrink-0 border-t border-[rgb(var(--theme-shade-rgb)/55%)] bg-black/[0.18] px-4 pt-3">
            <div className="mx-auto flex max-w-3xl gap-2 overflow-x-auto pb-2">
              {quickActions.map((action) => (
                <Button
                  key={action.label}
                  variant="outline"
                  size="sm"
                  className="shrink-0 gap-1.5"
                  onClick={() => handleSendMessage(action.label)}
                  disabled={isStreaming}
                >
                  <action.icon className="size-3.5" />
                  {action.label}
                </Button>
              ))}
            </div>
          </div>
        )}

        <div className="shrink-0 border-t border-[rgb(var(--theme-shade-rgb)/55%)] bg-black/[0.18] p-4">
          <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl items-center gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Напишите сообщение..."
              className="flex-1"
              disabled={isStreaming}
            />
            <Button
              type="submit"
              size="icon"
              className="priority-action"
              disabled={!inputValue.trim() || isStreaming}
            >
              {isStreaming ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
              <span className="sr-only">Отправить</span>
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
