import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { SystemStatus, ChatMessage, RelationshipData } from '@/types/api';
import { getSystemStatus } from '@/services/api';

export const useAppStore = defineStore('app', () => {
  // State
  const systemStatus = ref<SystemStatus | null>(null);
  const voiceCloned = ref(false);
  const voiceId = ref<string | null>(null);
  const voiceName = ref<string | null>(null);
  const agentCreated = ref(false);
  const agentName = ref<string | null>(null);
  const chatHistory = ref<ChatMessage[]>([]);
  const currentUserId = ref(1); // Demo user ID
  const relationships = ref<RelationshipData[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentStep = ref(0); // 0: verification, 1: voice, 2: agent, 3: chat
  
  // Auth State
  const isLoggedIn = ref(false);
  const walletAddress = ref<string | null>(null);
  const isAdmin = ref(false);

  function setWalletAddress(addr: string) {
    walletAddress.value = addr;
    isLoggedIn.value = true;
  }


  // Computed
  const isSystemReady = computed(() => 
    voiceCloned.value && agentCreated.value
  );

  const setupProgress = computed(() => {
    let progress = 0;
    if (relationships.value.some(r => r.verification_status === 'approved')) progress += 25;
    if (voiceCloned.value) progress += 25;
    if (agentCreated.value) progress += 25;
    if (chatHistory.value.length > 0) progress += 25;
    return progress;
  });

  const approvedRelationships = computed(() =>
    relationships.value.filter(r => r.verification_status === 'approved')
  );

  const hasApprovedRelationship = computed(() => 
    approvedRelationships.value.length > 0
  );

  // Actions
  async function fetchSystemStatus() {
    try {
      loading.value = true;
      error.value = null;
      systemStatus.value = await getSystemStatus();
      
      // Update local state based on system status
      if (systemStatus.value.voice_ready && systemStatus.value.voice_id) {
        voiceCloned.value = true;
        voiceId.value = systemStatus.value.voice_id;
      }
      
      if (systemStatus.value.agent_ready && systemStatus.value.agent_name) {
        agentCreated.value = true;
        agentName.value = systemStatus.value.agent_name;
      }

      // Auto advance step
      if (!hasApprovedRelationship.value) {
        currentStep.value = 0;
      } else if (!voiceCloned.value) {
        currentStep.value = 1;
      } else if (!agentCreated.value) {
        currentStep.value = 2;
      } else {
        currentStep.value = 3;
      }
    } catch (err: any) {
      error.value = err.message;
      console.error('Failed to fetch system status:', err);
    } finally {
      loading.value = false;
    }
  }

  function setVoiceCloned(id: string, name: string) {
    voiceCloned.value = true;
    voiceId.value = id;
    voiceName.value = name;
  }

  function setAgentCreated(name: string) {
    agentCreated.value = true;
    agentName.value = name;
  }

  function addChatMessage(message: ChatMessage) {
    chatHistory.value.push({
      ...message,
      timestamp: message.timestamp || new Date().toISOString()
    });
  }

  function clearChatHistory() {
    chatHistory.value = [];
  }

  function setRelationships(data: RelationshipData[]) {
    relationships.value = data;
  }

  function addRelationship(relationship: RelationshipData) {
    relationships.value.push(relationship);
  }

  function updateRelationship(id: number, updates: Partial<RelationshipData>) {
    const index = relationships.value.findIndex(r => r.id === id);
    if (index !== -1) {
      relationships.value[index] = { ...relationships.value[index], ...updates };
    }
  }

  function setCurrentStep(step: number) {
    currentStep.value = step;
  }

  function setCurrentUserId(userId: number) {
    currentUserId.value = userId;
  }

  function setLoggedIn(status: boolean, address?: string, admin: boolean = false) {
    isLoggedIn.value = status;
    if (address) walletAddress.value = address;
    isAdmin.value = admin;
  }

  function setAdmin(status: boolean) {
    isAdmin.value = status;
  }

  function logout() {
    isLoggedIn.value = false;
    walletAddress.value = null;
    isAdmin.value = false;
    currentUserId.value = 1;
    reset();
  }

  function reset() {
    systemStatus.value = null;
    voiceCloned.value = false;
    voiceId.value = null;
    voiceName.value = null;
    agentCreated.value = false;
    agentName.value = null;
    chatHistory.value = [];
    relationships.value = [];
    currentStep.value = 0;
    error.value = null;
  }

  return {
    // State
    systemStatus,
    voiceCloned,
    voiceId,
    voiceName,
    agentCreated,
    agentName,
    chatHistory,
    currentUserId,
    relationships,
    loading,
    error,
    currentStep,
    isLoggedIn,
    walletAddress,
    isAdmin,
    // Computed
    isSystemReady,
    setupProgress,
    approvedRelationships,
    hasApprovedRelationship,
    // Actions
    fetchSystemStatus,
    setVoiceCloned,
    setAgentCreated,
    setWalletAddress,
    addChatMessage,
    clearChatHistory,
    setRelationships,
    addRelationship,
    updateRelationship,
    setCurrentStep,
    setCurrentUserId,
    setLoggedIn,
    setAdmin,
    logout,
    reset
  };
});
