export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  is_active: boolean;
  created_at: string;
  messages: ChatMessage[];
}

export interface ConversationBrief {
  id: string;
  title: string | null;
  is_active: boolean;
  created_at: string;
}
