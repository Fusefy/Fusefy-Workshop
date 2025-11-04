export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  capabilities: string[];
  module: 'onboarding' | 'interview-scheduler';
  subModule?: string;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentId?: string;
  type?: 'text' | 'action' | 'system';
  actions?: MessageAction[];
}

export interface MessageAction {
  id: string;
  label: string;
  type: 'button' | 'link' | 'form';
  action: string;
  data?: any;
}

export interface ChatSession {
  id: string;
  agentId: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  dueDate?: Date;
  assignedAgent?: string;
}

export interface InterviewSlot {
  id: string;
  date: Date;
  duration: number;
  interviewer: string;
  interviewType: string;
  available: boolean;
  timezone: string;
}

export interface Module {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  agents: Agent[];
}