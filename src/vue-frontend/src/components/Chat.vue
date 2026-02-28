<template>
  <div class="chat-interface">
    <div class="header">
      <h2>💬 Step 3: Chat</h2>
      <p class="subtitle">与您创建的数字代理进行实时对话</p>
    </div>

    <el-alert
      v-if="!appStore.isSystemReady"
      type="error"
      title="⚠️ 系统未就绪"
      description="请先完成声音克隆和代理创建"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />

    <el-row :gutter="20">
      <!-- Chat Window -->
      <el-col :md="16" :sm="24">
        <el-card shadow="hover" class="chat-card">
          <template #header>
            <div class="card-header">
              <span>与 {{ appStore.agentName || '代理' }} 的对话</span>
              <el-button 
                type="danger" 
                text 
                @click="clearHistory"
                :icon="Delete"
              >
                清空记录
              </el-button>
            </div>
          </template>

          <div class="chat-window" ref="chatWindowRef">
            <div v-if="chatMessages.length === 0" class="empty-chat">
              <el-empty description="还没有消息，开始对话吧！" />
            </div>
            <div v-else>
              <div 
                v-for="(msg, index) in chatMessages" 
                :key="index"
                class="message-row"
                :class="msg.role"
              >
                <div class="message-bubble">
                  <div class="message-content">{{ msg.content }}</div>
                  <div class="message-timestamp">{{ formatTimestamp(msg.timestamp) }}</div>
                  <audio v-if="msg.audioUrl" :src="msg.audioUrl" controls class="message-audio"></audio>
                </div>
              </div>
            </div>
            <div v-if="isThinking" class="message-row agent">
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <el-input
              ref="inputRef"
              v-model="userInput"
              placeholder="输入消息..."
              size="large"
              @keyup.enter="sendTextMessage"
              :disabled="!appStore.isSystemReady || isThinking"
            >
              <template #append>
                <el-button 
                  @click="sendTextMessage" 
                  :disabled="!userInput.trim()"
                  :loading="isThinking"
                  :icon="Promotion"
                />
              </template>
            </el-input>
            <el-button
              class="voice-button"
              :type="isRecording ? 'danger' : 'primary'"
              @click="toggleRecording"
              :disabled="!appStore.isSystemReady || isThinking"
              circle
              size="large"
              :icon="Microphone"
            />
          </div>
          <div v-if="isRecording" class="recording-status">
            正在录音... {{ recordingTime }}s
          </div>
        </el-card>
      </el-col>

      <!-- Control Panel -->
      <el-col :md="8" :sm="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>⚙️ 控制面板</span>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="语音回复">
              <el-switch v-model="useVoice" />
              <el-text size="small" type="info" style="margin-left: 10px;">
                开启后，代理将用克隆的声音回复
              </el-text>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import { ElMessage, ElInput } from 'element-plus';
import { Promotion, Microphone, Delete } from '@element-plus/icons-vue';
import { useAppStore } from '@/stores/app';
import { sendTextMessage as sendTextAPI, sendVoiceMessage as sendVoiceAPI, clearChatHistory, getChatHistory } from '@/services/api';
import { AudioRecorder, blobToFile } from '@/utils/audio';

interface ChatMessageDisplay {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  audioUrl?: string;
}

const appStore = useAppStore();
const chatWindowRef = ref<HTMLElement | null>(null);
const inputRef = ref<InstanceType<typeof ElInput> | null>(null);

const userInput = ref('');
const chatMessages = ref<ChatMessageDisplay[]>([]);
const isThinking = ref(false);
const useVoice = ref(true);

const recorder = new AudioRecorder();
const isRecording = ref(false);
const recordingTime = ref(0);
let recordingTimer: any;

onMounted(async () => {
  await loadHistory();
  focusInput();
});

watch(chatMessages, () => {
  scrollToBottom();
}, { deep: true });

async function loadHistory() {
  try {
    const { history } = await getChatHistory();
    chatMessages.value = history.map(h => [
      { role: 'user' as const, content: h.user, timestamp: h.timestamp || new Date().toISOString() },
      { role: 'agent' as const, content: h.agent, timestamp: h.timestamp || new Date().toISOString() }
    ]).flat();
  } catch (error) {
    console.error("Failed to load chat history:", error);
  }
}

function addMessage(role: 'user' | 'agent', content: string, audioUrl?: string) {
  chatMessages.value.push({
    role,
    content,
    timestamp: new Date().toISOString(),
    audioUrl
  });
}

async function sendTextMessage() {
  if (!userInput.value.trim() || isThinking.value) return;

  const message = userInput.value;
  addMessage('user', message);
  userInput.value = '';
  isThinking.value = true;

  try {
    const response = await sendTextAPI(message, useVoice.value);
    let audioUrl;
    if (response.audio_url) {
      // Assuming backend returns a URL that can be played
      audioUrl = response.audio_url;
    }
    addMessage('agent', response.agent_response, audioUrl);
  } catch (error: any) {
    ElMessage.error(`发送失败: ${error.message}`);
    // Optionally remove the user's message if sending failed
    chatMessages.value.pop();
  } finally {
    isThinking.value = false;
    focusInput();
  }
}

async function toggleRecording() {
  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
}

async function startRecording() {
  try {
    await recorder.startRecording();
    isRecording.value = true;
    recordingTime.value = 0;
    recordingTimer = setInterval(() => {
      recordingTime.value++;
    }, 1000);
  } catch (error: any) {
    ElMessage.error(error.message);
  }
}

async function stopRecording() {
  try {
    const audioBlob = await recorder.stopRecording();
    clearInterval(recordingTimer);
    isRecording.value = false;
    
    if (recordingTime.value < 1) {
      ElMessage.warning('录音时间太短');
      return;
    }

    const audioFile = blobToFile(audioBlob, `recording-${Date.now()}.wav`);
    sendVoiceMessage(audioFile);

  } catch (error: any) {
    ElMessage.error(`录音失败: ${error.message}`);
  }
}

async function sendVoiceMessage(audioFile: File) {
  isThinking.value = true;
  const userAudioUrl = URL.createObjectURL(audioFile);
  addMessage('user', '[语音消息]', userAudioUrl);

  try {
    const responseBlob = await sendVoiceAPI(audioFile);
    const agentAudioUrl = URL.createObjectURL(responseBlob);
    // We don't have the transcribed text here, so we use a placeholder.
    // A more advanced implementation would involve another API call or WebSocket message
    // to get the transcribed text for both user and agent.
    addMessage('agent', '[语音回复]', agentAudioUrl);
  } catch (error: any) {
    ElMessage.error(`发送失败: ${error.message}`);
    chatMessages.value.pop();
  } finally {
    isThinking.value = false;
  }
}

async function clearHistory() {
  try {
    await clearChatHistory();
    chatMessages.value = [];
    ElMessage.success('聊天记录已清空');
  } catch (error: any) {
    ElMessage.error(`清空失败: ${error.message}`);
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatWindowRef.value) {
      chatWindowRef.value.scrollTop = chatWindowRef.value.scrollHeight;
    }
  });
}

function focusInput() {
  nextTick(() => {
    inputRef.value?.focus();
  });
}

function formatTimestamp(isoString: string): string {
  return new Date(isoString).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}
</script>

<style scoped lang="scss">
.chat-interface {
  padding: 20px;

  .header {
    margin-bottom: 20px;
    h2 { font-size: 28px; font-weight: 600; margin-bottom: 8px; color: #303133; }
    .subtitle { color: #909399; font-size: 15px; }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .chat-card {
    display: flex;
    flex-direction: column;
    height: 70vh;
  }

  .chat-window {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px 20px;
    background-color: #f5f7fa;
  }

  .message-row {
    display: flex;
    margin-bottom: 15px;

    &.user {
      justify-content: flex-end;
      .message-bubble {
        background-color: #409eff;
        color: white;
        border-radius: 15px 15px 0 15px;
      }
    }

    &.agent {
      justify-content: flex-start;
      .message-bubble {
        background-color: #ffffff;
        color: #303133;
        border-radius: 15px 15px 15px 0;
        border: 1px solid #e4e7ed;
      }
    }
  }

  .message-bubble {
    max-width: 70%;
    padding: 10px 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }

  .message-content {
    white-space: pre-wrap;
    word-break: break-word;
  }

  .message-timestamp {
    font-size: 10px;
    margin-top: 5px;
    text-align: right;
    opacity: 0.7;
  }
  
  .message-audio {
    margin-top: 10px;
    width: 100%;
    max-width: 250px;
  }

  .chat-input-area {
    display: flex;
    align-items: center;
    padding: 10px;
    border-top: 1px solid #e4e7ed;
    
    .voice-button {
      margin-left: 10px;
    }
  }
  
  .recording-status {
    text-align: center;
    color: #f56c6c;
    padding-bottom: 10px;
  }

  .typing-indicator {
    span {
      height: 8px;
      width: 8px;
      background-color: #909399;
      border-radius: 50%;
      display: inline-block;
      margin: 0 2px;
      animation: bounce 1.4s infinite ease-in-out both;
    }
    span:nth-child(1) { animation-delay: -0.32s; }
    span:nth-child(2) { animation-delay: -0.16s; }
  }

  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1.0); }
  }
}
</style>
