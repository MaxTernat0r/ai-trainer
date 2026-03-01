'use client';

import { useState, useRef, useEffect } from 'react';
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
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import type { ChatMessage, ConversationBrief } from '@/types/chat';

// --- Mock data ---
const mockConversations: ConversationBrief[] = [
  {
    id: 'c1',
    title: 'Программа тренировок',
    is_active: true,
    created_at: '2026-03-01T10:00:00Z',
  },
  {
    id: 'c2',
    title: 'Советы по питанию',
    is_active: false,
    created_at: '2026-02-28T14:00:00Z',
  },
  {
    id: 'c3',
    title: 'Техника приседаний',
    is_active: false,
    created_at: '2026-02-25T09:00:00Z',
  },
  {
    id: 'c4',
    title: 'Восстановление после травмы',
    is_active: false,
    created_at: '2026-02-20T16:00:00Z',
  },
];

const mockMessages: ChatMessage[] = [
  {
    id: 'm1',
    role: 'assistant',
    content:
      'Привет! Я ваш персональный ИИ-тренер. Я помогу вам с тренировками, питанием и достижением ваших фитнес-целей. Чем могу помочь?',
    created_at: '2026-03-01T10:00:00Z',
  },
  {
    id: 'm2',
    role: 'user',
    content:
      'Привет! Хочу набрать мышечную массу. Какую программу тренировок посоветуешь?',
    created_at: '2026-03-01T10:01:00Z',
  },
  {
    id: 'm3',
    role: 'assistant',
    content:
      'Отличная цель! Для набора мышечной массы я рекомендую программу Push/Pull/Legs (PPL). Это один из самых эффективных сплитов.\n\n**Структура PPL:**\n\n- **Push (Жимовые):** грудь, плечи, трицепс\n- **Pull (Тяговые):** спина, бицепс\n- **Legs (Ноги):** квадрицепсы, задняя поверхность бедра, икры\n\nДля набора массы важно:\n1. Прогрессивная перегрузка (увеличение веса/повторений)\n2. Достаточное количество белка (1.6-2.2 г/кг массы тела)\n3. Профицит калорий (300-500 ккал сверх нормы)\n4. Качественный сон (7-9 часов)\n\nХотите, чтобы я составил детальную программу на основе вашего уровня подготовки и доступного оборудования?',
    created_at: '2026-03-01T10:02:00Z',
  },
  {
    id: 'm4',
    role: 'user',
    content: 'Да, составь, пожалуйста! Уровень средний, занимаюсь в зале.',
    created_at: '2026-03-01T10:03:00Z',
  },
  {
    id: 'm5',
    role: 'assistant',
    content:
      'Отлично! Я составил для вас программу тренировок. Она доступна в разделе "Тренировки". Программа рассчитана на 8 недель с 4 тренировками в неделю по схеме PPL + Upper.\n\nОсновные принципы вашей программы:\n- Базовые упражнения в начале тренировки\n- Диапазон 8-12 повторений для гипертрофии\n- Отдых 60-120 секунд между подходами\n- Прогрессия нагрузки каждую неделю\n\nНачните с комфортных весов и постепенно увеличивайте. Если будут вопросы по технике выполнения упражнений, спрашивайте!',
    created_at: '2026-03-01T10:04:00Z',
  },
];

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
  const [messages, setMessages] = useState<ChatMessage[]>(mockMessages);
  const [inputValue, setInputValue] = useState('');
  const [activeConversation, setActiveConversation] = useState('c1');
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;

    const newMessage: ChatMessage = {
      id: `m${Date.now()}`,
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue('');

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: `m${Date.now() + 1}`,
        role: 'assistant',
        content:
          'Спасибо за ваш вопрос! Я обрабатываю его и скоро дам развёрнутый ответ. Это демо-версия чата, в полной версии я смогу полноценно помогать вам с тренировками и питанием.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    }, 1000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

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
            <Button variant="ghost" size="icon-xs">
              <Plus className="size-4" />
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
            {mockConversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setActiveConversation(conv.id)}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors',
                  activeConversation === conv.id
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
              </button>
            ))}
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
              <p className="text-xs text-muted-foreground">Онлайн</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((message) => (
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
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
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
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick actions */}
        <div className="border-t border-border bg-background px-4 pt-3">
          <div className="mx-auto flex max-w-3xl gap-2 overflow-x-auto pb-2">
            {quickActions.map((action) => (
              <Button
                key={action.label}
                variant="outline"
                size="sm"
                className="shrink-0 gap-1.5"
                onClick={() => sendMessage(action.label)}
              >
                <action.icon className="size-3.5" />
                {action.label}
              </Button>
            ))}
          </div>
        </div>

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
            />
            <Button type="submit" size="icon" disabled={!inputValue.trim()}>
              <Send className="size-4" />
              <span className="sr-only">Отправить</span>
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
