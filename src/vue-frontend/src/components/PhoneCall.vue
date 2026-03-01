<template>
  <div class="phone-call-container">
    <!-- Agent Selection Overlay -->
    <div v-if="!isAgentSelected" class="agent-selection-overlay">
      <div class="selection-card">
        <h2>Select an Agent to Call</h2>
        <p>Choose which loved one you would like to talk to today.</p>
        
        <div v-if="loadingAgents" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="availableAgents.length === 0" class="empty-state">
          <el-empty description="No agents created yet">
            <el-button type="primary" @click="$router.push('/create-agent')">Create Your First Agent</el-button>
          </el-empty>
        </div>
        
        <div v-else class="agent-grid">
          <div 
            v-for="agent in availableAgents" 
            :key="agent.id" 
            class="agent-select-item"
            @click="handleSelectAgent(agent)"
          >
            <div class="agent-avatar">{{ agent.name.charAt(0).toUpperCase() }}</div>
            <div class="agent-info">
              <span class="name">{{ agent.name }}</span>
              <span class="relation">{{ agent.relationship }}</span>
            </div>
            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Interface (Only shown if agent selected) -->
    <template v-else>
      <!-- Call History Section -->
      <div class="call-history-section">
        <div class="history-header">
          <div class="header-title">
            <h3>Call History</h3>
            <el-tag size="small" type="info" class="agent-tag">{{ agentName }}</el-tag>
          </div>
          <div class="header-actions">
            <el-button text link @click="isAgentSelected = false">Switch Agent</el-button>
            <el-button text link @click="fetchHistory" :icon="Refresh">Refresh</el-button>
          </div>
        </div>
        <el-scrollbar height="600px">
          <div v-if="filteredHistory.length === 0" class="empty-history">
            <el-empty description="No calls yet with this agent" :image-size="100" />
          </div>
          <div v-else class="history-list">
            <div v-for="(call, index) in filteredHistory" :key="index" class="history-item" :class="{ 'on-chain': call.blockchain_tx_hash }">
              <div class="call-icon">
                <el-icon :class="call.type === 'incoming' ? 'incoming' : 'outgoing'"><Phone /></el-icon>
              </div>
              <div class="call-info">
                <div class="caller-name">
                  {{ call.name || 'Unknown' }}
                  <el-tag v-if="call.blockchain_tx_hash" type="success" size="small" effect="plain" style="margin-left: 8px;">
                    On-Chain
                  </el-tag>
                </div>
                <div class="call-time">{{ call.timestamp ? formatTime(call.timestamp) : 'Unknown time' }}</div>
                <div v-if="call.blockchain_tx_hash" class="blockchain-proof">
                  <div class="proof-item">
                    <span class="proof-label">TX:</span>
                    <a :href="`https://sepolia.etherscan.io/tx/${call.blockchain_tx_hash}`" target="_blank" class="proof-link">
                      {{ call.blockchain_tx_hash.substring(0, 10) }}...{{ call.blockchain_tx_hash.substring(call.blockchain_tx_hash.length - 8) }}
                    </a>
                  </div>
                  <div v-if="call.ipfs_hash" class="proof-item">
                    <span class="proof-label">IPFS:</span>
                    <span class="proof-value">{{ call.ipfs_hash.substring(0, 10) }}...{{ call.ipfs_hash.substring(call.ipfs_hash.length - 8) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- Phone Simulator Section -->
      <div class="phone-simulator">
        <div class="phone-frame">
          <div class="notch"></div>
          <div class="screen" :class="callStatus">
            <!-- Back Button for Call/Message -->
            <div v-if="callStatus !== 'idle'" class="back-nav" @click="backToIdle">
              <el-icon><ArrowLeft /></el-icon>
              <span>Back</span>
            </div>
            
            <!-- Idle / Contact Screen -->
            <div v-if="callStatus === 'idle'" class="screen-content idle">
              <div class="status-bar">
                <span>9:41</span>
                <div class="status-icons">
                  <el-icon><Connection /></el-icon>
                  <div class="battery-indicator">
                    <el-progress :percentage="batteryPercentage" :color="batteryColor" :show-text="false" style="width: 50px; margin: 0 4px;"></el-progress>
                  </div>
                </div>
              </div>
              <div class="contact-info">
                <div class="avatar-placeholder">{{ agentInitial }}</div>
                <h2>{{ agentName }}</h2>
                <p>Mobile</p>
              </div>
              <div class="actions">
                <div class="action-btn" @click="startSimulation">
                  <div class="btn-circle green">
                    <el-icon><PhoneFilled /></el-icon>
                  </div>
                  <span>Call</span>
                </div>
                <div class="action-btn" @click="openMessaging">
                  <div class="btn-circle grey">
                    <el-icon><Message /></el-icon>
                  </div>
                  <span>Message</span>
                </div>
              </div>
            </div>

            <!-- Messaging Screen (WeChat Style) -->
            <div v-if="callStatus === 'messaging'" class="screen-content messaging">
              <div class="chat-header">
                <div class="header-info">
                  <div class="mini-avatar">{{ agentInitial }}</div>
                  <span class="chat-name">{{ agentName }}</span>
                </div>
              </div>
              
              <div class="chat-messages" ref="chatScrollRef">
                <div v-for="(msg, idx) in chatHistory" :key="idx" class="chat-bubble-wrapper" :class="msg.role">
                  <div class="chat-bubble">
                    {{ msg.content }}
                  </div>
                </div>
                <div v-if="isProcessing" class="chat-bubble-wrapper agent">
                  <div class="chat-bubble typing">
                    <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
                  </div>
                </div>
              </div>

              <div class="chat-input-wrapper">
                <div class="voice-toggle">
                  <el-tooltip :content="useVoiceInMessage ? 'Voice ON' : 'Voice OFF'">
                    <el-icon :class="{ active: useVoiceInMessage }" @click="useVoiceInMessage = !useVoiceInMessage">
                      <Microphone />
                    </el-icon>
                  </el-tooltip>
                </div>
                <input 
                  v-model="textMessage" 
                  placeholder="Type message..." 
                  @keyup.enter="sendTextReply"
                  :disabled="isProcessing"
                />
                <el-icon class="send-icon" @click="sendTextReply" :class="{ disabled: !textMessage.trim() || isProcessing }">
                  <Promotion />
                </el-icon>
              </div>
            </div>

            <!-- Incoming Call Screen -->
            <div v-if="callStatus === 'incoming'" class="screen-content incoming">
              <div class="caller-info">
                <h2>{{ agentName }}</h2>
                <p>Incoming Call...</p>
              </div>
              <div class="call-actions">
                <div class="action-btn" @click="rejectCall">
                  <div class="btn-circle red big">
                    <el-icon><PhoneFilled /></el-icon>
                  </div>
                  <span>Decline</span>
                </div>
                <div class="action-btn" @click="answerCall">
                  <div class="btn-circle green big">
                    <el-icon><PhoneFilled /></el-icon>
                  </div>
                  <span>Accept</span>
                </div>
              </div>
            </div>

            <!-- In Call Screen -->
            <div v-if="callStatus === 'connected'" class="screen-content connected">
              <div class="caller-info">
                <h2>{{ agentName }}</h2>
                <p>{{ callDurationFormatted }}</p>
              </div>
              
              <div class="waveform-viz">
                <div class="bar" v-for="i in 10" :key="i" :style="{ height: getBarHeight(i) + 'px' }"></div>
              </div>

              <div class="transcript-preview" v-if="lastMessage">
                 "{{ lastMessage }}"
              </div>

              <!-- Blockchain Verification Info -->
              <div class="blockchain-verification" v-if="blockchainVerificationVisible">
                <div class="verification-item" v-if="lastIPFSHash">
                  <span class="label">IPFS:</span>
                  <span class="hash">{{ lastIPFSHash.substring(0, 16) }}...</span>
                </div>
                <div class="verification-item" v-if="lastBlockchainTxHash">
                  <span class="label">Chain:</span>
                  <a :href="`https://sepolia.etherscan.io/tx/${lastBlockchainTxHash}`" target="_blank" class="chain-link">
                    {{ lastBlockchainTxHash.substring(0, 10) }}...
                  </a>
                </div>
              </div>

              <div class="call-controls">
                <div class="call-actions" style="justify-content: center; gap: 60px;">
                  <div class="action-btn" @click="toggleRecording" :style="{ opacity: isProcessing ? 0.6 : 1, pointerEvents: isProcessing ? 'none' : 'auto' }">
                    <div class="btn-circle big" :class="isRecording ? 'red recording-pulse' : 'blue'" :title="isRecording ? '点击停止并发送 (' + recordingDuration + ')' : '点击开始录音'">
                      <el-icon><Microphone /></el-icon>
                    </div>
                    <span style="color: white; margin-top: 8px;">{{ isRecording ? '结束并发送 (' + recordingDuration + ')' : (isProcessing ? '处理中...' : '开始录音') }}</span>
                  </div>

                  <div class="action-btn" @click="endCall">
                    <div class="btn-circle red big" title="挂断电话">
                      <el-icon><PhoneFilled style="transform: rotate(135deg);" /></el-icon>
                    </div>
                    <span style="color: white; margin-top: 8px;">挂断电话</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useAppStore } from '@/stores/app';
import { getChatHistory, sendVoiceMessage, listAgents, selectAgent, sendTextMessage } from '@/services/api';
import { Phone, PhoneFilled, Connection, Message, Microphone, VideoCamera, Mute, ArrowRight, Refresh, ArrowLeft, Promotion } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

interface CallHistoryItem {
  type: 'incoming' | 'outgoing';
  name: string;
  timestamp?: string;
  duration: string;
  blockchain_tx_hash?: string;
  ipfs_hash?: string;
  on_chain_timestamp?: string;
}

const appStore = useAppStore();
const history = ref<CallHistoryItem[]>([]);
const callStatus = ref<'idle' | 'incoming' | 'connected' | 'messaging'>('idle');
const callDuration = ref(0);
const timer = ref<any>(null);
const lastMessage = ref('');
const isRecording = ref(false);
const isProcessing = ref(false);
const batteryPercentage = ref(100);
const lastIPFSHash = ref('');
const lastBlockchainTxHash = ref('');
const blockchainVerificationVisible = ref(false);

// Messaging State
const textMessage = ref('');
const useVoiceInMessage = ref(true);
const chatScrollRef = ref<HTMLElement | null>(null);

// Local chat history for the messaging screen (transient)
const chatHistory = ref<Array<{ role: 'user' | 'agent', content: string }>>([]);

// Agent Selection State
const isAgentSelected = ref(false);
const loadingAgents = ref(false);
const availableAgents = ref<any[]>([]);
const selectedAgentId = ref<number | null>(null);

// Audio recording variables
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioContext: AudioContext | null = null;
const recordingStartTime = ref(0);
const recordingDurationSeconds = ref(0);
let recordingTimer: any = null;

const recordingDuration = computed(() => {
  if (!isRecording.value) return '0:00';
  const mins = Math.floor(recordingDurationSeconds.value / 60);
  const secs = recordingDurationSeconds.value % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
});

const agentName = computed(() => appStore.agentName || 'Loved One');
const agentInitial = computed(() => agentName.value.charAt(0).toUpperCase());

// Filter history by agent name
const filteredHistory = computed(() => {
  if (!isAgentSelected.value) return [];
  // For now, filter by name match since backend doesn't support ID filtering
  return history.value.filter(item => 
    item.name === 'Me' || item.name === agentName.value
  );
});

// Watch for chatHistory changes to scroll to bottom
watch(chatHistory, () => {
  nextTick(() => {
    if (chatScrollRef.value) {
      chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight;
    }
  });
}, { deep: true });

const batteryColor = computed(() => {
  if (batteryPercentage.value > 50) return '#67c23a';
  if (batteryPercentage.value > 20) return '#e6a23c';
  return '#f56c6c';
});

const callDurationFormatted = computed(() => {
  const mins = Math.floor(callDuration.value / 60).toString().padStart(2, '0');
  const secs = (callDuration.value % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
});

onMounted(async () => {
  await fetchAgents();
  // If appStore already has an agent name, we might be able to skip selection
  // but it's safer to let the user confirm.
  if (appStore.agentCreated && appStore.agentName) {
    // Optionally auto-select if only one agent exists
    if (availableAgents.value.length === 1) {
      handleSelectAgent(availableAgents.value[0]);
    }
  }
});

onUnmounted(() => {
  stopTimer();
  stopRecording();
});

async function fetchAgents() {
  loadingAgents.value = true;
  try {
    const data = await listAgents(appStore.currentUserId);
    availableAgents.value = data;
  } catch (e) {
    console.error('Failed to fetch agents', e);
    ElMessage.error('Failed to load agents');
  } finally {
    loadingAgents.value = false;
  }
}

async function handleSelectAgent(agent: any) {
  try {
    const res = await selectAgent(agent.id);
    if (res.success) {
      appStore.setAgentCreated(agent.name);
      selectedAgentId.value = agent.id;
      isAgentSelected.value = true;
      await fetchHistory();
    }
  } catch (e) {
    console.error('Failed to select agent', e);
    ElMessage.error('Failed to activate agent');
  }
}

async function fetchHistory() {
  try {
    const res = await getChatHistory();
    if(res.history) {
        history.value = res.history.map((msg: any) => ({
        type: (msg.role === 'user' ? 'outgoing' : 'incoming') as 'incoming' | 'outgoing',
        name: msg.role === 'user' ? 'Me' : (msg.agent_name || agentName.value),
        timestamp: msg.timestamp,
        duration: '2:30',
        blockchain_tx_hash: msg.blockchain_tx_hash,
        ipfs_hash: msg.ipfs_hash,
        on_chain_timestamp: msg.on_chain_timestamp
        })).reverse();
        
        // Populate chatHistory for the messaging screen if empty
        if (chatHistory.value.length === 0) {
          chatHistory.value = res.history.map((msg: any) => ({
            role: msg.role === 'user' ? 'user' : 'agent',
            content: msg.role === 'user' ? msg.user : msg.agent
          }));
        }
    }
  } catch (e) {
    console.error('Failed to fetch history', e);
  }
}

function startSimulation() {
  callStatus.value = 'incoming';
}

function answerCall() {
  callStatus.value = 'connected';
  startTimer();
  console.log('📞 Call answered - waiting for manual recording');
  console.log('🎤 Voice ID:', appStore.voiceId);
  console.log('👤 Agent name:', appStore.agentName);
  // Manual recording mode: start from toggleRecording instead of immediately
  // Simulate battery drain during call
  simulateBatteryDrain();
}

function rejectCall() {
  callStatus.value = 'idle';
}

function backToIdle() {
  if (callStatus.value === 'connected') {
    endCall();
  } else {
    callStatus.value = 'idle';
  }
}

function endCall() {
  callStatus.value = 'idle';
  stopTimer();
  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }
  recordingDurationSeconds.value = 0;
  stopRecording();
  lastMessage.value = '';
  batteryPercentage.value = 100; // Reset battery
}

function toggleRecording() {
  if (isRecording.value) {
    // Stop recording and send
    if (recordingTimer) {
      clearInterval(recordingTimer);
      recordingTimer = null;
    }
    sendAudioMessage();
  } else {
    // Start recording
    recordingStartTime.value = Date.now();
    recordingDurationSeconds.value = 0;
    recordingTimer = setInterval(() => {
      recordingDurationSeconds.value = Math.floor((Date.now() - recordingStartTime.value) / 1000);
    }, 1000);
    startRecording();
  }
}

function startTimer() {
  callDuration.value = 0;
  timer.value = setInterval(() => {
    callDuration.value++;
  }, 1000);
}

function stopTimer() {
  if (timer.value) {
    clearInterval(timer.value);
    timer.value = null;
  }
}

function formatTime(isoString: string) {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getBarHeight(index: number) {
  return 10 + Math.random() * 30;
}

// Audio recording implementation
async function startRecording() {
  try {
    isRecording.value = true;
    audioChunks = [];
    console.log('🎙️ Requesting microphone access...');
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('✅ Microphone access granted');
    
    // Setup media recorder
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    mediaRecorder.start();
    console.log('⏺️ MediaRecorder started');
    console.log('🎤 Manual recording mode - click button to stop and send');
    
  } catch (e) {
    console.error('❌ Microphone access error:', e);
    ElMessage.error('Failed to access microphone - please check permissions');
    isRecording.value = false;
  }
}

function stopRecording() {
  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  if (audioContext) {
    audioContext.close();
  }
  isRecording.value = false;
}

async function sendAudioMessage() {
  if (!mediaRecorder) return;
  
  isProcessing.value = true;
  isRecording.value = false; // Reset the recording state immediately so UI updates
  console.log('📤 Preparing to send audio message...');
  
  // Create a promise that resolves when data is available after stopping
  const waitForData = new Promise<Blob>((resolve) => {
    mediaRecorder!.ondataavailable = (event) => {
      resolve(event.data);
    };
  });

  // Stop recorder to trigger ondataavailable
  if (mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  
  try {
    const audioBlob = await waitForData;
    console.log('🎵 Audio blob received, size:', audioBlob.size, 'bytes');
    
    if (audioBlob.size < 100) {
      console.warn('⚠️ Audio blob too small, likely empty.');
      ElMessage.warning('录音太短，请重新录制。');
      isProcessing.value = false;
      return;
    }
    
    // Send to backend
    try {
      console.log('🌐 Sending to backend...');
      const response = await sendVoiceMessage(audioBlob);
      
      console.log('✅ Backend response received:', response);
      
      // 保存IPFS和区块链信息
      if (response.ipfs_hash) {
        lastIPFSHash.value = response.ipfs_hash;
        console.log('📦 IPFS Hash:', response.ipfs_hash);
      }
      if (response.blockchain_tx_hash) {
        lastBlockchainTxHash.value = response.blockchain_tx_hash;
        console.log('⛓️ Blockchain TX Hash:', response.blockchain_tx_hash);
        blockchainVerificationVisible.value = true;
      }
      
      if (response.agent_response) {
        lastMessage.value = response.agent_response;
        console.log('💬 Agent says:', response.agent_response);
        
        // Add to local chat history
        chatHistory.value.push({ role: 'user', content: response.user_message });
        chatHistory.value.push({ role: 'agent', content: response.agent_response });
        
        // Play audio if available
        if (response.audio_url) {
          try {
            console.log('🔊 Playing audio response...');
            const audio = new Audio(response.audio_url);
            audio.onended = () => {
              console.log('✅ Audio playback finished - ready for manual recording');
            };
            audio.onerror = (err) => {
              console.error('❌ Audio playback error:', err);
              ElMessage.warning('Unable to play agent response audio');
            };
            await audio.play();
          } catch (audioErr) {
            console.error('❌ Failed to play audio:', audioErr);
            ElMessage.warning('Unable to play agent response audio');
          }
        } else {
          console.log('📝 No audio URL, fallback to text-only mode.');
        }
      } else {
        console.error('❌ No agent response in backend response');
        ElMessage.error('No response from agent');
      }
    } catch (apiErr: any) {
      console.error('❌ API error:', apiErr);
      console.error('Error details:', apiErr.response?.data || apiErr.message);
      ElMessage.error(`Failed to get response: ${apiErr.message || 'Unknown error'}`);
    }
    
  } catch (e: any) {
    console.error('❌ Unexpected error:', e);
    ElMessage.error(`Message processing failed: ${e.message}`);
  } finally {
    isProcessing.value = false;
  }
}

function openMessaging() {
  if (!isAgentSelected.value) {
    ElMessage.warning('Please select an agent first');
    return;
  }
  callStatus.value = 'messaging';
}

async function sendTextReply() {
  if (!textMessage.value.trim() || isProcessing.value) return;
  
  const userContent = textMessage.value;
  textMessage.value = '';
  isProcessing.value = true;
  
  // Optimistic UI update
  chatHistory.value.push({ role: 'user', content: userContent });
  
  try {
    const response = await sendTextMessage(userContent, useVoiceInMessage.value);
    
    if (response.agent_response) {
      chatHistory.value.push({ role: 'agent', content: response.agent_response });
      
      // If we got an audio response, play it
      if (response.has_audio && response.audio_data) {
        try {
          const binaryString = atob(response.audio_data);
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          await audio.play();
        } catch (audioErr) {
          console.error('Failed to play audio response:', audioErr);
        }
      }
      
      // Update blockchain/IPFS status if available
      if (response.ipfs_hash) lastIPFSHash.value = response.ipfs_hash;
      if (response.blockchain_tx_hash) {
        lastBlockchainTxHash.value = response.blockchain_tx_hash;
        blockchainVerificationVisible.value = true;
      }
      
      // Refresh global history
      await fetchHistory();
    }
  } catch (e: any) {
    console.error('Failed to send text message:', e);
    ElMessage.error(`Failed to send message: ${e.message}`);
  } finally {
    isProcessing.value = false;
  }
}

function simulateBatteryDrain() {
  // Drain battery 1% every 30 seconds during call
  const batteryTimer = setInterval(() => {
    if (callStatus.value === 'connected' && batteryPercentage.value > 0) {
      batteryPercentage.value = Math.max(0, batteryPercentage.value - 1);
    } else {
      clearInterval(batteryTimer);
    }
  }, 30000);
}

</script>

<style scoped lang="scss">
.phone-call-container {
  display: flex;
  height: 100%;
  gap: 40px;
  position: relative;
}

.back-nav {
  position: absolute;
  top: 45px;
  left: 20px;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  backdrop-filter: blur(5px);
  
  &:hover {
    background: white;
  }
}

.agent-selection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(5px);

  .selection-card {
    width: 500px;
    background: white;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;

    h2 { margin-top: 0; color: #303133; }
    p { color: #909399; margin-bottom: 30px; }

    .agent-grid {
      display: flex;
      flex-direction: column;
      gap: 15px;
      max-height: 400px;
      overflow-y: auto;
      padding: 5px;
    }

    .agent-select-item {
      display: flex;
      align-items: center;
      padding: 15px 20px;
      background: #f9fafc;
      border: 1px solid #ebeef5;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #409eff;
        background: #f0f7ff;
        transform: translateX(5px);
      }

      .agent-avatar {
        width: 45px;
        height: 45px;
        background: #409eff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 18px;
        margin-right: 15px;
      }

      .agent-info {
        flex: 1;
        text-align: left;
        display: flex;
        flex-direction: column;

        .name { font-weight: 600; color: #303133; font-size: 16px; }
        .relation { font-size: 13px; color: #909399; }
      }

      .arrow-icon { color: #c0c4cc; }
    }
  }
}

.call-history-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;

    .header-title {
      display: flex;
      align-items: center;
      gap: 10px;
      h3 { margin: 0; color: #333; }
    }
    
    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .history-item {
    display: flex;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #f5f7fa;
    transition: background 0.2s;

    &:hover { background-color: #f9fafc; }
    
    &.on-chain {
      background: linear-gradient(to right, #f0f9ff 0%, #ffffff 100%);
      border-left: 3px solid #67c23a;
    }

    .call-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #f0f2f5;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      
      .incoming { color: #67c23a; transform: rotate(135deg); }
      .outgoing { color: #409eff; transform: rotate(45deg); }
    }

    .call-info {
      flex: 1;
      
      .caller-name { 
        font-weight: 600; 
        color: #303133;
        display: flex;
        align-items: center;
      }
      
      .call-time { 
        font-size: 12px; 
        color: #909399; 
        margin-top: 4px; 
      }
      
      .blockchain-proof {
        margin-top: 8px;
        padding: 8px;
        background: #f0f9ff;
        border-radius: 4px;
        font-size: 11px;
        
        .proof-item {
          display: flex;
          align-items: center;
          margin-bottom: 4px;
          
          &:last-child { margin-bottom: 0; }
          
          .proof-label {
            font-weight: 600;
            color: #67c23a;
            margin-right: 6px;
            min-width: 40px;
          }
          
          .proof-link {
            color: #409eff;
            text-decoration: none;
            font-family: monospace;
            
            &:hover {
              text-decoration: underline;
            }
          }
          
          .proof-value {
            color: #606266;
            font-family: monospace;
          }
        }
      }
    }
  }
}

.phone-simulator {
  flex: 0 0 380px;
  display: flex;
  justify-content: center;
  align-items: center;

  .phone-frame {
    width: 320px;
    height: 650px;
    background: #000;
    border-radius: 40px;
    padding: 12px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.2);
    position: relative;

    .notch {
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 120px;
      height: 25px;
      background: #000;
      border-bottom-left-radius: 15px;
      border-bottom-right-radius: 15px;
      z-index: 10;
    }

    .screen {
      width: 100%;
      height: 100%;
      background: #fff;
      border-radius: 30px;
      overflow: hidden;
      position: relative;
      
      &.connected, &.incoming {
        background: linear-gradient(180deg, #2b3245 0%, #141619 100%);
        color: white;
      }
    }
  }
}

.screen-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  padding-top: 50px;
  position: relative;

  .status-bar {
    position: absolute;
    top: 15px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    font-weight: 600;
    color: #333;
    &.white { color: white; }

    .status-icons {
      display: flex;
      align-items: center;
      gap: 8px;

      .battery-indicator {
        display: flex;
        align-items: center;
      }
    }
  }

  &.idle {
    align-items: center;
    justify-content: center;
    
    .contact-info {
      text-align: center;
      margin-bottom: 60px;
      
      .avatar-placeholder {
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        color: white;
        margin: 0 auto 20px;
      }
      
      h2 { margin: 0; font-size: 28px; font-weight: 500; }
      p { margin: 5px 0 0; color: #909399; }
    }
  }

  &.connected, &.incoming {
    justify-content: space-between;
    align-items: center;
    padding-bottom: 60px;

    .caller-info {
      text-align: center;
      margin-top: 60px;
      h2 { font-size: 32px; font-weight: 400; margin: 0; }
      p { color: rgba(255,255,255,0.7); margin-top: 10px; font-size: 18px; }
    }
  }

  &.messaging {
    padding: 0;
    display: flex;
    flex-direction: column;
    background: #f5f5f5;

    .chat-header {
      padding: 50px 15px 10px;
      background: #f5f5f5;
      border-bottom: 1px solid #e0e0e0;
      text-align: center;

      .header-info {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;

        .mini-avatar {
          width: 30px;
          height: 30px;
          background: #409eff;
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 600;
        }

        .chat-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }
      }
    }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 15px;
      display: flex;
      flex-direction: column;
      gap: 15px;
      scrollbar-width: none;
      &::-webkit-scrollbar { display: none; }

      .chat-bubble-wrapper {
        display: flex;
        width: 100%;

        &.user {
          justify-content: flex-end;
          .chat-bubble {
            background: #95ec69;
            color: #000;
            border-radius: 6px 2px 6px 6px;
            &::after {
              content: '';
              position: absolute;
              right: -5px;
              top: 8px;
              border-width: 5px 0 5px 5px;
              border-style: solid;
              border-color: transparent transparent transparent #95ec69;
            }
          }
        }

        &.agent {
          justify-content: flex-start;
          .chat-bubble {
            background: #fff;
            color: #000;
            border-radius: 2px 6px 6px 6px;
            &::after {
              content: '';
              position: absolute;
              left: -5px;
              top: 8px;
              border-width: 5px 5px 5px 0;
              border-style: solid;
              border-color: transparent #fff transparent transparent;
            }
          }
        }

        .chat-bubble {
          max-width: 80%;
          padding: 8px 12px;
          font-size: 14px;
          position: relative;
          word-break: break-word;
          box-shadow: 0 1px 2px rgba(0,0,0,0.05);

          &.typing {
            padding: 8px 15px;
            .dot {
              animation: blink 1s infinite;
              &:nth-child(2) { animation-delay: 0.2s; }
              &:nth-child(3) { animation-delay: 0.4s; }
            }
          }
        }
      }
    }

    .chat-input-wrapper {
      padding: 10px 15px 30px;
      background: #f7f7f7;
      border-top: 1px solid #e0e0e0;
      display: flex;
      align-items: center;
      gap: 10px;

      .voice-toggle {
        font-size: 20px;
        color: #666;
        cursor: pointer;
        display: flex;
        
        .active { color: #409eff; }
      }

      input {
        flex: 1;
        border: none;
        background: #fff;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        outline: none;
      }

      .send-icon {
        font-size: 20px;
        color: #07c160;
        cursor: pointer;
        &.disabled { color: #ccc; cursor: not-allowed; }
      }
    }
  }
}

@keyframes blink {
  0% { opacity: 0.2; }
  50% { opacity: 1; }
  100% { opacity: 0.2; }
}

.actions, .call-actions {
  display: flex;
  gap: 40px;
  
  .action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    
    span { font-size: 12px; font-weight: 500; }
    
    .btn-circle {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      transition: transform 0.1s;
      
      &:active { transform: scale(0.95); }
      &.green { background: #4cd964; color: white; }
      &.red { background: #ff3b30; color: white; }
      &.blue { background: #007aff; color: white; }
      &.grey { background: #e5e5ea; color: #007aff; }
      
      &.big { width: 70px; height: 70px; font-size: 30px; }
    }
  }
}

.waveform-viz {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 60px;
  
  .bar {
    width: 6px;
    background: rgba(255,255,255,0.6);
    border-radius: 3px;
    animation: bounce 1s infinite ease-in-out;
  }
}

.transcript-preview {
  background: rgba(255,255,255,0.1);
  padding: 15px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
  text-align: center;
  margin: 0 20px;
  backdrop-filter: blur(10px);
}

.blockchain-verification {
  background: rgba(76, 175, 80, 0.15);
  border-left: 3px solid #4cd964;
  padding: 12px 15px;
  border-radius: 8px;
  font-size: 12px;
  margin: 10px 20px 0;
  backdrop-filter: blur(10px);

  .verification-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 5px 0;
    color: rgba(255,255,255,0.85);

    &:first-child {
      margin-top: 0;
    }

    .label {
      font-weight: 600;
      width: 40px;
      flex-shrink: 0;
    }

    .hash {
      font-family: monospace;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      color: #4cd964;
    }

    .chain-link {
      font-family: monospace;
      color: #4cd964;
      text-decoration: none;
      cursor: pointer;

      &:hover {
        text-decoration: underline;
        color: #67de6d;
      }
    }
  }
}

.call-controls {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 30px;
  
  .control-row {
    display: flex;
    justify-content: center;
    gap: 30px;
    
    &.end-call { margin-top: 10px; }
  }
  
  .control-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    cursor: pointer;
    backdrop-filter: blur(5px);
    
    &:hover { background: rgba(255,255,255,0.3); }
  }
}

@keyframes bounce {
  0%, 100% { transform: scaleY(0.4); }
  50% { transform: scaleY(1); }
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(255, 59, 48, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }
}

.recording-pulse {
  animation: pulse-ring 1.5s infinite;
}
</style>
