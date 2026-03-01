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

export const loginWithEmail = async (
  email: string,
  password: string
): Promise<{
  success: boolean;
  access_token: string;
  token_type: string;
  user: { id: number; username: string; email: string; is_admin: boolean };
}> => {
  const { data } = await apiClient.post('/auth/login', { email, password });
  return data;
};

export const registerUser = async (
  username: string,
  email: string,
  password: string
): Promise<{
  success: boolean;
  access_token: string;
  token_type: string;
  user: { id: number; username: string; email: string; is_admin: boolean };
}> => {
  const { data } = await apiClient.post('/auth/register', { username, email, password });
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

export const uploadMultipleVerificationDocuments = async (
  relationshipId: number,
  userId: number,
  documents: File[],
  documentTypes?: string[],
  descriptions?: string[]
): Promise<{
  status: string;
  uploaded_count: number;
  failed_count: number;
  uploaded_files: any[];
  failed_files: any[];
  message: string;
}> => {
  const formData = new FormData();
  
  // 添加所有文件
  documents.forEach(doc => {
    formData.append('documents', doc);
  });
  
  // 添加文档类型（如果提供）
  if (documentTypes && documentTypes.length > 0) {
    formData.append('document_types', JSON.stringify(documentTypes));
  }
  
  // 添加描述（如果提供）
  if (descriptions && descriptions.length > 0) {
    formData.append('descriptions', JSON.stringify(descriptions));
  }

  const { data } = await apiClient.post(
    `/relationships/${relationshipId}/upload-documents`,
    formData,
    {
      params: { user_id: userId },
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  return data;
};

export const getRelationshipDocuments = async (
  relationshipId: number,
  userId: number
): Promise<{
  relationship_id: number;
  document_count: number;
  documents: Array<{
    id: number;
    filename: string;
    file_size: number;
    file_type: string;
    document_type?: string;
    description?: string;
    uploaded_at?: string;
  }>;
}> => {
  const { data } = await apiClient.get(
    `/relationships/${relationshipId}/documents`,
    {
      params: { user_id: userId }
    }
  );
  return data;
};

export const deleteVerificationDocument = async (
  relationshipId: number,
  documentId: number,
  userId: number
): Promise<{ status: string; message: string }> => {
  const { data } = await apiClient.delete(
    `/relationships/${relationshipId}/documents/${documentId}`,
    {
      params: { user_id: userId }
    }
  );
  return data;
};

export const getPendingRelationships = async (
  reviewerId: number
): Promise<RelationshipData[]> => {
  const { data } = await apiClient.get('/relationships/admin/pending', {
    params: { reviewer_id: reviewerId }
  });
  return data;
};

export const verifyRelationshipByAdmin = async (
  relationshipId: number,
  payload: { action: 'approve' | 'reject'; reviewer: string; notes?: string },
  reviewerId: number
): Promise<RelationshipData> => {
  const { data } = await apiClient.post(
    `/relationships/${relationshipId}/verify`,
    payload,
    { params: { reviewer_id: reviewerId } }
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

  try {
    const { data } = await apiClient.post('/voice/quick-tts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    });
    return data;
  } catch (error: any) {
    const blobData = error?.response?.data;
    if (blobData instanceof Blob) {
      try {
        const text = await blobData.text();
        const parsed = JSON.parse(text);
        const detail = parsed?.detail || parsed?.error || parsed?.message;
        throw new Error(detail || 'TTS request failed');
      } catch {
        throw new Error('TTS request failed');
      }
    }
    throw error;
  }
};

// ============ Agent APIs ============

export const createAgent = async (
  profile: AgentProfile
): Promise<{ success: boolean; message: string; agent_name: string }> => {
  const { data } = await apiClient.post('/agent/create', profile);
  return {
    success: !!data.success,
    message: data.message,
    agent_name: data.agent_name || data.profile?.name || profile.name,
  };
};

export const resetAgent = async (): Promise<{ success: boolean; message: string }> => {
  const { data } = await apiClient.post('/agent/reset');
  return data;
};

export const listVoiceProfiles = async (
  userId: number
): Promise<any[]> => {
  const { data } = await apiClient.get('/voice/list', {
    params: { user_id: userId }
  });
  return data;
};

// ============ Agent APIs ============

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
  audioFile: Blob
): Promise<{ 
  agent_response: string
  audio_url: string | null
  user_message: string
  ipfs_hash?: string
  blockchain_tx_hash?: string
}> => {
  const formData = new FormData();
  // Convert blob to file if needed
  const file = audioFile instanceof File ? audioFile : new File([audioFile], 'audio.wav', { type: 'audio/wav' });
  formData.append('audio_file', file);

  const response = await apiClient.post<{
    user_message: string;
    agent_response: string;
    has_audio: boolean;
    audio_data?: string;
    audio_format?: string;
    ipfs_hash?: string;
    blockchain_tx_hash?: string;
  }>('/chat/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  let audioUrl: string | null = null;
  
  // Handle audio data if present
  if (response.data.has_audio && response.data.audio_data) {
    try {
      // Decode base64 audio data
      const binaryString = atob(response.data.audio_data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob and object URL
      const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
      audioUrl = URL.createObjectURL(audioBlob);
    } catch (e) {
      console.error('Failed to decode audio data:', e);
    }
  }
  
  return {
    user_message: response.data.user_message,
    agent_response: response.data.agent_response,
    audio_url: audioUrl,
    ipfs_hash: response.data.ipfs_hash,
    blockchain_tx_hash: response.data.blockchain_tx_hash
  };
};

export const simulateCall = async (
  audioFile: File,
  voiceId: string,
  agentName: string = 'Loved One'
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
  const { data } = await apiClient.post('/chat/clear');
  return data;
};
// ============ Blockchain APIs ============

export const saveVoiceToBlockchain = async (
  voiceId: string,
  voiceName: string,
  ipfsHash: string,
  userAddress: string
): Promise<{ success: boolean; tx_hash?: string; error?: string }> => {
  const { data } = await apiClient.post('/voice/save-to-blockchain', {
    voice_id: voiceId,
    voice_name: voiceName,
    ipfs_hash: ipfsHash,
    user_address: userAddress
  });
  return data;
};

export const saveRelationshipToBlockchain = async (
  relationshipId: number,
  ipfsHash: string,
  userAddress: string
): Promise<{ success: boolean; tx_hash?: string; error?: string }> => {
  const { data } = await apiClient.post('/relationships/save-to-blockchain', {
    relationship_id: relationshipId,
    ipfs_hash: ipfsHash,
    user_address: userAddress
  });
  return data;
};

export const saveAgentToBlockchain = async (
  payload: {
    agent_name: string;
    ipfs_hash: string;
    wallet_address: string;
    agent_data?: any;
  }
): Promise<{ success: boolean; tx_hash?: string; error?: string }> => {
  const { data } = await apiClient.post('/agent/save-agent-to-blockchain', payload);
  return data;
};

export const getUserBlockchainMemories = async (
  userAddress: string,
  userId: number
): Promise<{ memories: any[]; count: number }> => {
  const { data } = await apiClient.get(`/blockchain/memories/${userAddress}`, {
    params: { user_id: userId }
  });
  return data;
};