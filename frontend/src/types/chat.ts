export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tool_events?: AgentEvent[];
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

// ----- Agent SSE protocol -----

export type AgentEventType =
  | 'text'
  | 'tool_use_start'
  | 'tool_result'
  | 'tool_proposal'
  | 'tool_executing'
  | 'error';

export interface TextEvent {
  type: 'text';
  content: string;
}

export interface ToolUseStartEvent {
  type: 'tool_use_start';
  id: string;
  name: string;
  summary: string;
}

export interface ToolResultEvent {
  type: 'tool_result';
  id: string;
  name: string;
  ok: boolean;
  summary: string;
  result?: Record<string, unknown>;
}

export interface ToolProposalEvent {
  type: 'tool_proposal';
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  summary: string;
}

export interface ToolExecutingEvent {
  type: 'tool_executing';
  id: string;
}

export interface ErrorEvent {
  type: 'error';
  message: string;
}

export type AgentEvent =
  | TextEvent
  | ToolUseStartEvent
  | ToolResultEvent
  | ToolProposalEvent
  | ToolExecutingEvent
  | ErrorEvent;

export type ProposalStatus =
  | 'pending'
  | 'executing'
  | 'approved'
  | 'rejected'
  | 'error';

export interface ToolProposal {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  summary: string;
  status: ProposalStatus;
  resultSummary?: string;
  result?: Record<string, unknown>;
  error?: string;
}
