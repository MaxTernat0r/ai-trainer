'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
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
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import {
  useConversations,
  useConversation,
  useCreateConversation,
  useDeleteConversation,
} from '@/lib/queries/use-chat';
import { useChatStream } from '@/lib/hooks/use-chat-stream';
import type { ChatMessage } from '@/types/chat';

const quickActions = [
  {
    label: 'Составь тренировку',
    icon: Dumbbell,
  },
  {
    label: 'Посоветуй питание',
    icon: UtensilsCrossed,
  },
  {
    label: 'Как улучшить технику?',
    icon: HelpCircle,
  },
];

export default function ChatPage() {
  const [inputValue, setInputValue] = useState('');
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>(undefined);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Queries
  const { data: conversations, isLoading: conversationsLoading } = useConversations();
  const { data: activeConversation, isLoading: conversationLoading } = useConversation(activeConversationId);

  // Mutations
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();

  // Chat streaming
  const { streamMessage, isStreaming, sendMessage: sendStreamMessage } = useChatStream();

  // Auto-select first conversation
  useEffect(() => {
    if (!activeConversationId && conversations && conversations.length > 0) {
      setActiveConversationId(conversations[0].id);
    }
  }, [conversations, activeConversationId]);

  // Build messages array: real messages + streaming message
  const messages: ChatMessage[] = (() => {
    const base = activeConversation?.messages ?? [];
    if (isStreaming && streamMessage) {
      return [
        ...base,
        {
          id: '__streaming__',
          role: 'assistant' as const,
          content: streamMessage,
          created_at: new Date().toISOString(),
        },
      ];
    }
    return base;
  })();

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamMessage, scrollToBottom]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    let conversationId = activeConversationId;

    // Create a new conversation if none is active
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

    try {
      await sendStreamMessage(conversationId, text.trim());
    } catch {
      toast.error('Ошибка отправки сообщения');
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

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteConversation.mutate(id, {
      onSuccess: () => {
        if (activeConversationId === id) {
          setActiveConversationId(undefined);
        }
        toast.success('Диалог удалён');
      },
      onError: () => {
        toast.error('Не удалось удалить диалог');
      },
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="-m-4 flex h-[calc(100vh-4rem)] sm:-m-6 lg:-m-8 md:h-[calc(100vh-4rem)]">
      {/* Sidebar - conversations list */}
      <aside
        className={cn(
          'flex-col border-r border-border bg-muted/30 transition-all duration-300',
          sidebarVisible ? 'hidden w-72 md:flex' : 'hidden'
        )}
      >
        <div className="flex items-center justify-between border-b border-border p-4">
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
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setSidebarVisible(false)}
            >
              <PanelLeftClose className="size-4" />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          <div className="flex flex-col gap-1">
            {conversationsLoading ? (
              <>
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex items-center gap-3 rounded-lg px-3 py-2.5">
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
                    'group flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors',
                    activeConversationId === conv.id
                      ? 'bg-background shadow-sm'
                      : 'hover:bg-background/50'
                  )}
                >
                  <MessageSquare className="size-4 shrink-0 text-muted-foreground" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">
                      {conv.title ?? 'Новый диалог'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(conv.created_at).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    className="hidden shrink-0 group-hover:flex"
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                  >
                    <Trash2 className="size-3 text-muted-foreground" />
                  </Button>
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

      {/* Main chat area */}
      <div className="flex flex-1 flex-col">
        {/* Chat header */}
        <div className="flex items-center gap-3 border-b border-border px-4 py-3">
          {!sidebarVisible && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setSidebarVisible(true)}
            >
              <PanelLeft className="size-4" />
            </Button>
          )}
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-full bg-primary/10">
              <Bot className="size-4 text-primary" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">Чат с ИИ-тренером</h2>
              <p className="text-xs text-muted-foreground">
                {isStreaming ? 'Печатает...' : 'Онлайн'}
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {conversationLoading ? (
              <div className="flex flex-col gap-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className={cn(
                      'flex gap-3',
                      i % 2 === 0 ? 'flex-row-reverse' : 'flex-row'
                    )}
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
                    Задайте вопрос о тренировках, питании или технике упражнений.
                    Я помогу составить программу и достичь ваших целей.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-3',
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  )}
                >
                  {/* Avatar */}
                  <div
                    className={cn(
                      'flex size-8 shrink-0 items-center justify-center rounded-full',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    )}
                  >
                    {message.role === 'user' ? (
                      <User className="size-4" />
                    ) : (
                      <Bot className="size-4" />
                    )}
                  </div>

                  {/* Message bubble */}
                  <div
                    className={cn(
                      'max-w-[80%] rounded-2xl px-4 py-2.5',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    )}
                  >
                    <div className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                      {message.role === 'user' ? (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      ) : (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      )}
                      {message.id === '__streaming__' && (
                        <span className="ml-1 inline-block size-2 animate-pulse rounded-full bg-current" />
                      )}
                    </div>
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
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick actions */}
        {!hasMessages && !conversationLoading && (
          <div className="border-t border-border bg-background px-4 pt-3">
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

        {/* Input */}
        <div className="border-t border-border bg-background p-4">
          <form
            onSubmit={handleSubmit}
            className="mx-auto flex max-w-3xl items-center gap-2"
          >
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
              disabled={!inputValue.trim() || isStreaming}
            >
              {isStreaming ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
              <span className="sr-only">Отправить</span>
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
