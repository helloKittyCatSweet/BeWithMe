export interface RelationshipData {
  id?: number;
  user_id: number;
  guardian_name?: string;
  relative_name: string;
  relationship_type: 'parent' | 'grandparent' | 'sibling' | 'child' | 'spouse' | 'other';
  purpose: string;
  birth_date?: string;
  death_date?: string;
  additional_info?: string;
  verification_status?: 'pending' | 'approved' | 'rejected';
  created_at?: string;
  updated_at?: string;
  reviewer_notes?: string;
}

export interface VoiceCloneRequest {
  audio_file: File;
  voice_name: string;
  description: string;
  user_id: number;
  relationship_id?: number;
}

export interface VoiceCloneResponse {
  success: boolean;
  voice_id: string;
  voice_name: string;
  message: string;
  analysis?: {
    duration?: number;
    sample_rate?: number;
    channels?: number;
    quality_score?: number;
    audio_format?: string;
  };
  ipfs_hash?: string;
  ipfs_gateway_url?: string;
  blockchain_saved?: boolean;
}

export interface Voice {
  voice_id: string;
  name: string;
  labels?: {
    use_case?: string;
    description?: string;
  };
  samples?: any[];
}

export interface AgentProfile {
  name: string;
  relationship: string;
  personality_traits: string;
  speech_patterns: string[];
  background_story?: string;
  memories?: string[];
  voice_id?: string;
}

export interface ChatMessage {
  user: string;
  agent: string;
  timestamp?: string;
  blockchain_tx_hash?: string;  // 区块链交易哈希
  ipfs_hash?: string;  // IPFS 内容哈希
  on_chain_timestamp?: string;  // 上链时间戳
  role?: string;  // For PhoneCall mapping
}

export interface SystemStatus {
  agent_ready: boolean;
  voice_ready: boolean;
  database_connected: boolean;
  agent_name?: string;
  voice_id?: string;
  database_stats?: {
    total_users?: number;
    total_relationships?: number;
    pending_verifications?: number;
  };
}
