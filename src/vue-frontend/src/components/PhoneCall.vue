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
                  ⛓️ On-Chain
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
                <el-icon><Battery /></el-icon>
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

            <div class="call-controls">
              <div class="control-row">
                <div class="control-btn"><el-icon><Microphone /></el-icon></div>
                <div class="control-btn"><el-icon><VideoCamera /></el-icon></div>
                <div class="control-btn"><el-icon><Mute /></el-icon></div>
              </div>
              <div class="control-row end-call">
                <div class="btn-circle red big" @click="endCall">
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
import { getChatHistory } from '@/services/api'; // Using chat history as call logs for now
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

const agentName = computed(() => appStore.agentName || 'Father');
const agentInitial = computed(() => agentName.value.charAt(0).toUpperCase());

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
});

async function fetchHistory() {
  try {
    const res = await getChatHistory();
    // Assuming history structure, mapping it to display format
    // In a real app, you might have a dedicated /calls endpoint
    if(res.history) {
        history.value = res.history.map((msg: any) => ({
        type: (msg.role === 'user' ? 'outgoing' : 'incoming') as 'incoming' | 'outgoing',
        name: msg.role === 'user' ? 'Me' : agentName.value,
        timestamp: msg.timestamp,
        duration: '2:30', // Mock duration
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
  // Simulate outgoing call connecting immediately for demo
  // Or simulate incoming call for "Pick up" experience requested by user
  callStatus.value = 'incoming';
}

function answerCall() {
  callStatus.value = 'connected';
  startTimer();
  simulateConversation();
}

function rejectCall() {
  callStatus.value = 'idle';
}

function endCall() {
  callStatus.value = 'idle';
  stopTimer();
  lastMessage.value = '';
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
  return 10 + Math.random() * 30; // Mock visualization
}

// Mock conversation flow
function simulateConversation() {
  setTimeout(() => {
    lastMessage.value = "Hello? Is that you?";
  }, 1500);
  
  setTimeout(() => {
    lastMessage.value = "I've missed you so much...";
  }, 4000);
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
