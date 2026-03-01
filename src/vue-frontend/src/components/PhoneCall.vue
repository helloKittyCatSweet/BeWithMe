<template>
  <div class="phone-call-container">
    <!-- Call History Section -->
    <div class="call-history-section">
      <div class="history-header">
        <h3>Call History</h3>
        <el-button text link @click="fetchHistory">Refresh</el-button>
      </div>
      <el-scrollbar height="600px">
        <div v-if="history.length === 0" class="empty-history">
          <el-empty description="No calls yet" :image-size="100" />
        </div>
        <div v-else class="history-list">
          <div v-for="(call, index) in history" :key="index" class="history-item" :class="{ 'on-chain': call.blockchain_tx_hash }">
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
              <h2>{{ agentName || 'Loved One' }}</h2>
              <p>Mobile</p>
            </div>
            <div class="actions">
              <div class="action-btn" @click="startSimulation">
                <div class="btn-circle green">
                  <el-icon><PhoneFilled /></el-icon>
                </div>
                <span>Call</span>
              </div>
              <div class="action-btn">
                <div class="btn-circle grey">
                  <el-icon><Message /></el-icon>
                </div>
                <span>Message</span>
              </div>
            </div>
          </div>

          <!-- Incoming Call Screen -->
          <div v-if="callStatus === 'incoming'" class="screen-content incoming">
            <div class="caller-info">
              <h2>{{ agentName || 'Loved One' }}</h2>
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
              <h2>{{ agentName || 'Loved One' }}</h2>
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
                <span class="label">📦 IPFS:</span>
                <span class="hash">{{ lastIPFSHash.substring(0, 16) }}...</span>
              </div>
              <div class="verification-item" v-if="lastBlockchainTxHash">
                <span class="label">⛓️ Chain:</span>
                <a :href="`https://sepolia.etherscan.io/tx/${lastBlockchainTxHash}`" target="_blank" class="chain-link">
                  {{ lastBlockchainTxHash.substring(0, 10) }}...
                </a>
              </div>
            </div>

            <div class="call-controls">
              <div class="control-row">
                <div class="control-btn" title="静音"><el-icon><Mute /></el-icon></div>
                <div class="btn-circle blue big" @click="manualSend" :disabled="!isRecording || isProcessing" title="说完了，点击发送">
                  <el-icon><PhoneFilled /></el-icon>
                </div>
                <div class="control-btn" title="扬声器"><el-icon><VideoCamera /></el-icon></div>
              </div>
              <div class="control-row end-call">
                <div class="btn-circle red big" @click="endCall" title="挂断电话">
                  <el-icon><PhoneFilled /></el-icon>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAppStore } from '@/stores/app';
import { getChatHistory, sendVoiceMessage } from '@/services/api';
import { Phone, PhoneFilled, Connection, Message, Microphone, VideoCamera, Mute } from '@element-plus/icons-vue';
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
const callStatus = ref<'idle' | 'incoming' | 'connected'>('idle');
const callDuration = ref(0);
const timer = ref<any>(null);
const lastMessage = ref('');
const isRecording = ref(false);
const isProcessing = ref(false);
const batteryPercentage = ref(100);
const lastIPFSHash = ref('');
const lastBlockchainTxHash = ref('');
const blockchainVerificationVisible = ref(false);

// Audio recording variables
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let silenceTimeout: NodeJS.Timeout | null = null;
const SILENCE_DURATION = 1000; // 1 second of silence to trigger send
const SILENCE_THRESHOLD = 30; // Noise level threshold
let hasSpokenInCurrentMessage = false;

const agentName = computed(() => appStore.agentName || 'Father');
const agentInitial = computed(() => agentName.value.charAt(0).toUpperCase());
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

onMounted(() => {
  fetchHistory();
});

onUnmounted(() => {
  stopTimer();
  stopRecording();
});

async function fetchHistory() {
  try {
    const res = await getChatHistory();
    if(res.history) {
        history.value = res.history.map((msg: any) => ({
        type: (msg.role === 'user' ? 'outgoing' : 'incoming') as 'incoming' | 'outgoing',
        name: msg.role === 'user' ? 'Me' : agentName.value,
        timestamp: msg.timestamp,
        duration: '2:30',
        blockchain_tx_hash: msg.blockchain_tx_hash,
        ipfs_hash: msg.ipfs_hash,
        on_chain_timestamp: msg.on_chain_timestamp
        })).reverse();
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
  hasSpokenInCurrentMessage = false;
  console.log('📞 Call answered - starting recording');
  console.log('🎤 Voice ID:', appStore.voiceId);
  console.log('👤 Agent name:', appStore.agentName);
  startRecording();
  // Simulate battery drain during call
  simulateBatteryDrain();
}

function rejectCall() {
  callStatus.value = 'idle';
}

function endCall() {
  callStatus.value = 'idle';
  stopTimer();
  stopRecording();
  lastMessage.value = '';
  batteryPercentage.value = 100; // Reset battery
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
    
    // Setup audio context for silence detection
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 2048;
    
    console.log('🎚️ Audio analyser setup complete');
    
    // Setup media recorder
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    mediaRecorder.start();
    console.log('⏺️ MediaRecorder started');
    
    // Start silence detection
    monitorSilence();
    console.log('🔍 Silence monitoring started');
    
  } catch (e) {
    console.error('❌ Microphone access error:', e);
    ElMessage.error('Failed to access microphone - please check permissions');
    isRecording.value = false;
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  if (audioContext) {
    audioContext.close();
  }
  isRecording.value = false;
  
  if (silenceTimeout) {
    clearTimeout(silenceTimeout);
    silenceTimeout = null;
  }
}

function monitorSilence() {
  if (!analyser || !mediaRecorder) return;
  
  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  analyser.getByteFrequencyData(dataArray);
  
  // Calculate average noise level
  let sum = 0;
  for (let i = 0; i < dataArray.length; i++) {
    sum += dataArray[i];
  }
  const average = sum / dataArray.length;
  
  // Clear previous silence timeout if there's sound
  if (average > SILENCE_THRESHOLD) {
    hasSpokenInCurrentMessage = true;
    if (silenceTimeout) {
      clearTimeout(silenceTimeout);
      silenceTimeout = null;
      console.log('🔊 Audio detected (level:', Math.round(average), '), reset silence timer');
    }
  } else {
    // Start silence timer if not already started
    if (!silenceTimeout && hasSpokenInCurrentMessage) {
      console.log('🔇 Silence threshold reached (level:', Math.round(average), '), starting timer for', SILENCE_DURATION, 'ms');
      silenceTimeout = setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording' && hasSpokenInCurrentMessage) {
          console.log('⏱️ Silence duration exceeded, sending message...');
          hasSpokenInCurrentMessage = false;
          sendAudioMessage();
        }
      }, SILENCE_DURATION);
    }
  }
  
  // Continue monitoring
  if (isRecording.value) {
    requestAnimationFrame(monitorSilence);
  }
}

function manualSend() {
  console.log('👆 用户点击发送按钮');
  if (silenceTimeout) {
    clearTimeout(silenceTimeout);
    silenceTimeout = null;
  }
  sendAudioMessage();
}

async function sendAudioMessage() {
  if (!mediaRecorder) return;
  
  isProcessing.value = true;
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
      console.warn('⚠️ Audio blob too small, likely empty. Resuming...');
      if (callStatus.value === 'connected') {
        startRecording();
      }
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
        
        // Play audio if available
        if (response.audio_url) {
          try {
            console.log('🔊 Playing audio response...');
            const audio = new Audio(response.audio_url);
            audio.onended = () => {
              console.log('✅ Audio playback finished');
              // Resume recording after audio playback ends
              if (callStatus.value === 'connected') {
                console.log('🎙️ Resuming recording...');
                startRecording();
              }
            };
            audio.onerror = (err) => {
              console.error('❌ Audio playback error:', err);
              ElMessage.warning('Unable to play agent response audio');
              // Resume recording anyway
              if (callStatus.value === 'connected') {
                startRecording();
              }
            };
            await audio.play();
          } catch (audioErr) {
            console.error('❌ Failed to play audio:', audioErr);
            ElMessage.warning('Unable to play agent response audio');
            // Resume recording anyway
            if (callStatus.value === 'connected') {
              startRecording();
            }
          }
        } else {
          console.log('📝 No audio URL, resuming recording for text-only mode');
          // No audio, resume recording immediately
          if (callStatus.value === 'connected') {
            startRecording();
          }
        }
      } else {
        console.error('❌ No agent response in backend response');
        ElMessage.error('No response from agent');
      }
    } catch (apiErr: any) {
      console.error('❌ API error:', apiErr);
      console.error('Error details:', apiErr.response?.data || apiErr.message);
      ElMessage.error(`Failed to get response: ${apiErr.message || 'Unknown error'}`);
      // Resume recording on error
      if (callStatus.value === 'connected' && mediaRecorder) {
        mediaRecorder.start();
        monitorSilence();
      }
    }
    
  } catch (e: any) {
    console.error('❌ Unexpected error:', e);
    ElMessage.error(`Message processing failed: ${e.message}`);
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

    h3 { margin: 0; color: #333; }
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
</style>
