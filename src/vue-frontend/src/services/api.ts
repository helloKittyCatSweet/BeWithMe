import axios, { AxiosError } from 'axios';
import type {
  RelationshipData,
  VoiceCloneRequest,
  VoiceCloneResponse,
  Voice,
  AgentProfile,
  ChatMessage,
  SystemStatus
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ============ System APIs ============

export const getSystemStatus = async (): Promise<SystemStatus> => {
  const { data } = await apiClient.get<SystemStatus>('/status');
  return data;
};

export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  const { data } = await apiClient.get('/health');
  return data;
};

// ============ Relationship APIs ============

export const registerRelationship = async (
  relationshipData: RelationshipData
): Promise<RelationshipData> => {
  const { data } = await apiClient.post('/relationships/register', relationshipData, {
    params: { user_id: relationshipData.user_id }
  });
  return data;
};

export const listRelationships = async (
  userId: number,
  status?: string
): Promise<RelationshipData[]> => {
  const { data } = await apiClient.get('/relationships/list', {
    params: { user_id: userId, status }
  });
  return data;
};

export const uploadVerificationDocument = async (
  relationshipId: number,
  userId: number,
  document: File
): Promise<{ message: string; document_id: number }> => {
  const formData = new FormData();
  formData.append('document', document);

  const { data } = await apiClient.post(
    `/relationships/${relationshipId}/upload-document`,
    formData,
    {
      params: { user_id: userId },
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  return data;
};

// ============ Voice APIs ============

export const cloneVoice = async (
  request: VoiceCloneRequest
): Promise<VoiceCloneResponse> => {
  const formData = new FormData();
  formData.append('audio_file', request.audio_file);
  formData.append('voice_name', request.voice_name);
  formData.append('description', request.description);
  formData.append('user_id', request.user_id.toString());
  
  if (request.relationship_id) {
    formData.append('relationship_id', request.relationship_id.toString());
  }

  const { data } = await apiClient.post<VoiceCloneResponse>(
    '/voice/clone',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000 // 5 minutes for voice cloning
    }
  );
  return data;
};

export const listVoices = async (): Promise<{ success: boolean; voices: Voice[] }> => {
  const { data } = await apiClient.get('/voice/list');
  return data;
};

export const deleteVoice = async (voiceId: string): Promise<{ success: boolean; message: string }> => {
  const { data } = await apiClient.delete(`/voice/${voiceId}`);
  return data;
};

export const quickTTS = async (
  text: string,
  voiceId: string
): Promise<Blob> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('voice_id', voiceId);

  const { data } = await apiClient.post('/voice/quick-tts', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob'
  });
  return data;
};

// ============ Agent APIs ============

export const createAgent = async (
  profile: AgentProfile
): Promise<{ success: boolean; message: string; agent_name: string }> => {
  const { data } = await apiClient.post('/conversation/create-agent', profile);
  return data;
};

export const resetAgent = async (): Promise<{ success: boolean; message: string }> => {
  const { data } = await apiClient.post('/conversation/reset-agent');
  return data;
};

// ============ Chat APIs ============

export const sendTextMessage = async (
  message: string,
  useVoice: boolean = false
): Promise<{ user_message: string; agent_response: string; audio_url?: string }> => {
  const { data } = await apiClient.post('/chat/text', {
    message,
    use_voice: useVoice
  });
  return data;
};

export const sendVoiceMessage = async (
  audioFile: File
): Promise<Blob> => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);

  const { data } = await apiClient.post('/chat/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob'
  });
  return data;
};

export const simulateCall = async (
  audioFile: File,
  voiceId: string,
  agentName: string = '亲人'
): Promise<{ audio: Blob; userMessage: string; aiResponse: string }> => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  formData.append('voice_id', voiceId);
  formData.append('agent_name', agentName);

  const response = await apiClient.post('/voice/simulate-call', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob'
  });

  return {
    audio: response.data,
    userMessage: response.headers['x-user-message'] || '',
    aiResponse: response.headers['x-ai-response'] || ''
  };
};

export const getChatHistory = async (): Promise<{ history: ChatMessage[] }> => {
  const { data } = await apiClient.get('/chat/history');
  return data;
};

export const clearChatHistory = async (): Promise<{ message: string }> => {
  const { data } = await apiClient.post('/chat/clear-history');
  return data;
};
