export * from './api';

export interface AudioRecording {
  blob: Blob;
  url: string;
  duration: number;
}

export interface ConversationHistory {
  id: string;
  messages: {
    role: 'user' | 'agent';
    content: string;
    timestamp: Date;
    audioUrl?: string;
  }[];
  createdAt: Date;
}
