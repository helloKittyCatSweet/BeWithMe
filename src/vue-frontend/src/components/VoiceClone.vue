<template>
  <div class="voice-clone">
    <div class="header">
      <h2>Voice Cloning</h2>
      <p class="subtitle">Upload audio samples to clone your loved one's voice.</p>
    </div>

    <el-alert
      v-if="!appStore.hasApprovedRelationship"
      type="warning"
      title="Family Verification Required"
      description="Please complete and get approval for the Family Verification step first, then refresh the page."
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />

    <el-row :gutter="20">
      <!-- Clone Form -->
      <el-col :md="14" :sm="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Clone New Voice</span>
            </div>
          </template>

          <el-form 
            ref="cloneFormRef"
            :model="cloneForm" 
            :rules="cloneRules" 
            label-width="120px"
            :disabled="!appStore.hasApprovedRelationship"
            @submit.prevent="submitClone"
          >
            <el-form-item label="Relationship" prop="relationship_id">
              <el-select 
                v-model="cloneForm.relationship_id" 
                placeholder="Select verified relationship"
                style="width: 100%;"
                @change="handleRelationshipChange"
              >
                <el-option
                  v-for="rel in appStore.approvedRelationships"
                  :key="rel.id"
                  :label="`${rel.relative_name} (${getRelationshipLabel(rel.relationship_type)})`"
                  :value="rel.id"
                />
              </el-select>
              <el-text size="small" type="info" style="margin-top: 5px; display: block;">
                Only verified relationships can be used.
              </el-text>
            </el-form-item>

            <el-form-item label="Voice Name" prop="voice_name">
              <el-input 
                v-model="cloneForm.voice_name" 
                placeholder="e.g. Dad's Voice"
                clearable
              />
            </el-form-item>

            <el-form-item label="Description" prop="description">
              <el-input
                v-model="cloneForm.description"
                type="textarea"
                :rows="3"
                placeholder="Describe voice characteristics, e.g. Warm, Deep, Calm"
                clearable
              />
            </el-form-item>

            <el-form-item label="Audio File" prop="audio_file">
              <el-upload
                ref="audioUploadRef"
                class="audio-uploader"
                drag
                :auto-upload="false"
                :limit="1"
                :on-change="handleAudioChange"
                :on-remove="handleAudioRemove"
                accept="audio/wav,audio/mpeg,audio/mp4,audio/flac,video/mp4,.mp4"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  Drop file here or <em>click to upload</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    <p><strong>Audio Requirements:</strong></p>
                    <ul>
                      <li>Format: WAV, MP3, M4A, FLAC, MP4 (MP4 will use audio track only)</li>
                      <li>Duration: 10s - 30s</li>
                      <li>Quality: Clear, no noise, single speaker</li>
                    </ul>
                  </div>
                </template>
              </el-upload>

              <!-- Audio Preview -->
              <div v-if="audioPreviewUrl" class="audio-preview">
                <el-divider content-position="left">Audio Preview</el-divider>
                <audio :src="audioPreviewUrl" controls style="width: 100%;"></audio>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                size="large"
                @click="submitClone"
                :loading="cloning"
                :disabled="!cloneForm.audio_file || !appStore.hasApprovedRelationship"
                :icon="Microphone"
              >
                Start Voice Cloning
              </el-button>
              <el-button 
                @click="resetForm"
                :disabled="cloning"
              >
                Reset
              </el-button>
            </el-form-item>

            <!-- Progress -->
            <el-collapse-transition>
              <div v-if="cloning" style="margin-top: 20px;">
                <el-divider>Cloning Progress</el-divider>
                <el-steps :active="cloneStep" finish-status="success" align-center>
                  <el-step title="Uploading" />
                  <el-step title="Analyzing" />
                  <el-step title="Training" />
                  <el-step title="Generating" />
                </el-steps>
                <div style="text-align: center; margin-top: 20px;">
                  <el-text type="info">{{ cloneProgress }}</el-text>
                </div>
              </div>
            </el-collapse-transition>

            <!-- Result -->
            <el-alert
              v-if="cloneResult"
              :type="cloneResult.success ? 'success' : 'error'"
              :title="cloneResult.success ? 'Voice Cloned Successfully!' : '❌ Cloning Failed'"
              :closable="false"
              show-icon
              style="margin-top: 20px;"
            >
              <div v-if="cloneResult.success">
                <p><strong>Voice ID:</strong> {{ cloneResult.voice_id }}</p>
                <p><strong>Voice Name:</strong> {{ cloneResult.voice_name }}</p>
                <p>{{ cloneResult.message }}</p>
                
                <!-- IPFS Information -->
                <div v-if="cloneResult.ipfs_hash" style="margin-top: 15px; padding: 12px; background: #f0f9ff; border-left: 4px solid #409eff; border-radius: 4px;">
                  <el-divider content-position="left">
                    <el-icon style="color: #409eff;"><Link /></el-icon>
                    IPFS Storage
                  </el-divider>
                  <p style="margin: 5px 0;">
                    <strong>IPFS Hash:</strong> 
                    <el-tag size="small" type="info" style="margin-left: 8px; font-family: monospace;">
                      {{ shortenIPFSHash(cloneResult.ipfs_hash) }}
                    </el-tag>
                    <el-button 
                      size="small" 
                      text
                      :icon="CopyDocument"
                      @click="copyIPFSHash(cloneResult.ipfs_hash)"
                      style="margin-left: 5px;"
                    >
                      Copy
                    </el-button>
                  </p>
                  <p style="margin: 5px 0;">
                    <el-button 
                      size="small" 
                      type="primary" 
                      link
                      :icon="View"
                      @click="openIPFSGateway(cloneResult.ipfs_hash)"
                    >
                      View on IPFS Gateway
                    </el-button>
                  </p>
                  <el-text size="small" type="info" style="margin-top: 5px; display: block;">
                    Your audio is permanently stored on IPFS (Decentralized Storage)
                  </el-text>
                </div>
                
                <div v-if="cloneResult.analysis" style="margin-top: 10px;">
                  <el-divider content-position="left">Audio Analysis</el-divider>
                  <ul>
                    <li><strong>Duration:</strong> {{ cloneResult.analysis.duration?.toFixed(2) }}s</li>
                    <li><strong>Sample Rate:</strong> {{ cloneResult.analysis.sample_rate }} Hz</li>
                    <li><strong>Channels:</strong> {{ cloneResult.analysis.channels }}</li>
                    <li><strong>Quality Score:</strong> {{ cloneResult.analysis.quality_score }}/100</li>
                  </ul>
                </div>

                <el-button 
                  type="success" 
                  style="margin-top: 15px;"
                  @click="proceedToNextStep"
                >
                  Next Step: Create Digital Agent →
                </el-button>
                <el-button 
                  v-if="appStore.walletAddress && !cloneResult.blockchain_saved"
                  type="warning"
                  style="margin-top: 15px; margin-left: 10px;"
                  @click="saveToBlockchain"
                  :loading="savingToBlockchain"
                  :disabled="!cloneResult.voice_id"
                  icon="DataAnalysis"
                >
                  Save to Blockchain
                </el-button>
              </div>
              <p v-else>{{ cloneResult.message }}</p>
            </el-alert>
          </el-form>
        </el-card>
      </el-col>

      <!-- Voice List & Tips -->
      <el-col :md="10" :sm="24">
        <!-- Existing Voices -->
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Cloned Voices</span>
              <el-button 
                size="small" 
                text
                @click="loadVoices"
                :loading="loadingVoices"
                :icon="Refresh"
              >
                Refresh
              </el-button>
            </div>
          </template>

          <el-tabs v-model="voiceListTab" style="margin-bottom: 10px;">
            <el-tab-pane :label="`Your Voices (${customVoices.length})`" name="custom" />
            <el-tab-pane :label="`System Voices (${systemVoices.length})`" name="system" />
          </el-tabs>

          <div v-if="displayedVoices.length > 0" class="voice-list">
            <div 
              v-for="voice in displayedVoices"
              :key="voice.voice_id"
              class="voice-item"
              :class="{ active: voice.voice_id === appStore.voiceId }"
            >
              <div class="voice-header">
                <el-icon><Avatar /></el-icon>
                <span class="voice-name">{{ voice.name }}</span>
                <el-tag
                  size="small"
                  :type="isUserDefinedVoice(voice) ? 'success' : 'info'"
                >
                  {{ isUserDefinedVoice(voice) ? 'Custom' : 'System' }}
                </el-tag>
              </div>
              <div class="voice-info">
                <el-tag size="small" type="info">ID: {{ voice.voice_id.slice(0, 8) }}...</el-tag>
                <el-text size="small" type="info">{{ voice.labels?.description || 'No description' }}</el-text>
              </div>
              <div class="voice-actions">
                <el-button 
                  size="small" 
                  type="primary"
                  @click="testVoice(voice.voice_id)"
                  :loading="testingVoice === voice.voice_id"
                  :icon="VideoPlay"
                >
                  Test
                </el-button>
                <el-popconfirm
                  title="Are you sure you want to delete this voice?"
                  @confirm="handleDeleteVoice(voice.voice_id)"
                  confirm-button-text="Yes"
                  cancel-button-text="No"
                  width="200"
                >
                  <template #reference>
                    <el-button size="small" type="danger" :loading="deletingVoice === voice.voice_id" :icon="Delete">
                      Delete
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>

          <el-empty v-else :description="voiceListTab === 'custom' ? 'No custom voices yet' : 'No system voices available'" />
        </el-card>

        <!-- Test Output -->
        <el-card v-if="testAudioUrl" style="margin-top: 20px;" shadow="hover">
          <template #header>
            <span>Test Output</span>
          </template>
          <audio :src="testAudioUrl" controls style="width: 100%;"></audio>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { 
  UploadFilled, 
  Microphone, 
  Refresh, 
  VideoPlay, 
  Delete,
  Avatar,
  Link,
  CopyDocument,
  View
} from '@element-plus/icons-vue';
import type { FormInstance, FormRules, UploadFile, UploadInstance } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { cloneVoice, listVoices, deleteVoice as deleteVoiceAPI, quickTTS, saveVoiceToBlockchain } from '@/services/api';
import type { VoiceCloneRequest, VoiceCloneResponse, Voice } from '@/types/api';
import { getRelationshipLabel } from '@/utils/format';
import { validateAudioFile } from '@/utils/audio';
import { shortenIPFSHash as shortenHash, copyIPFSHash as copyHash, getIPFSExplorerUrl } from '@/utils/ipfs';

const emit = defineEmits<{
  'clone-success': [voiceId: string, voiceName: string],
  'next-step': []
}>();

const appStore = useAppStore();
const cloneFormRef = ref<FormInstance>();
const audioUploadRef = ref<UploadInstance>();

const cloneForm = reactive<Omit<VoiceCloneRequest, 'audio_file' | 'user_id'> & { audio_file: File | null }>({
  relationship_id: undefined,
  voice_name: '',
  description: '',
  audio_file: null,
});

const cloneRules = reactive<FormRules>({
  relationship_id: [{ required: true, message: 'Please select a verified relationship', trigger: 'change' }],
  voice_name: [{ required: true, message: 'Please enter a voice name', trigger: 'blur' }],
  audio_file: [{ required: true, message: 'Please upload an audio file' }],
});

const cloning = ref(false);
const cloneStep = ref(0);
const cloneProgress = ref('');
const cloneResult = ref<VoiceCloneResponse | null>(null);
const audioPreviewUrl = ref<string | null>(null);

const voices = ref<Voice[]>([]);
const voiceListTab = ref<'custom' | 'system'>('custom');
const loadingVoices = ref(false);
const deletingVoice = ref<string | null>(null);
const testingVoice = ref<string | null>(null);
const testAudioUrl = ref<string | null>(null);
const savingToBlockchain = ref(false);

const customVoices = computed(() => voices.value.filter(v => isUserDefinedVoice(v)));
const systemVoices = computed(() => voices.value.filter(v => !isUserDefinedVoice(v)));
const displayedVoices = computed(() => voiceListTab.value === 'custom' ? customVoices.value : systemVoices.value);

onMounted(async () => {
  await loadVoices();
});

function handleRelationshipChange(id: number) {
  const rel = appStore.approvedRelationships.find(r => r.id === id);
  if (rel) {
    cloneForm.voice_name = `${rel.relative_name}'s Voice`;
  }
}

async function handleAudioChange(file: UploadFile) {
  if (file.raw) {
    const validation = await validateAudioFile(file.raw);
    if (!validation.valid) {
      ElMessage.error(validation.error);
      audioUploadRef.value?.clearFiles();
      cloneForm.audio_file = null;
      return;
    }
    cloneForm.audio_file = file.raw;
    audioPreviewUrl.value = URL.createObjectURL(file.raw);
  }
}

function handleAudioRemove() {
  cloneForm.audio_file = null;
  if (audioPreviewUrl.value) {
    URL.revokeObjectURL(audioPreviewUrl.value);
    audioPreviewUrl.value = null;
  }
}

async function submitClone() {
  if (!cloneFormRef.value) return;
  await cloneFormRef.value.validate(async (valid) => {
    if (!valid || !cloneForm.audio_file) return;

    cloning.value = true;
    cloneResult.value = null;
    
    const request: VoiceCloneRequest = {
      ...cloneForm,
      audio_file: cloneForm.audio_file,
      user_id: appStore.currentUserId,
    };

    try {
      // Simulate progress
      cloneStep.value = 1;
      cloneProgress.value = 'Uploading audio file...';
      await new Promise(res => setTimeout(res, 1000));

      cloneStep.value = 2;
      cloneProgress.value = 'Analyzing audio features... (This may take a few minutes)';
      
      const result = await cloneVoice(request);
      cloneResult.value = result;

      if (result.success) {
        cloneStep.value = 4;
        cloneProgress.value = 'Voice Cloned Successfully!';
        ElMessage.success('Voice Cloned Successfully!');
        appStore.setVoiceCloned(result.voice_id, result.voice_name);
        emit('clone-success', result.voice_id, result.voice_name);
        await loadVoices();
      } else {
        throw new Error(result.message);
      }
    } catch (error: any) {
      cloneStep.value = 0;
      ElMessage.error(`Cloning Failed: ${error.response?.data?.detail || error.message}`);
      cloneResult.value = { success: false, message: error.message } as any;
    } finally {
      cloning.value = false;
      cloneProgress.value = '';
    }
  });
}

function resetForm() {
  cloneFormRef.value?.resetFields();
  audioUploadRef.value?.clearFiles();
  handleAudioRemove();
}

async function loadVoices() {
  try {
    loadingVoices.value = true;
    const data = await listVoices();
    if (data.success) {
      voices.value = data.voices;
      if (voiceListTab.value === 'custom' && customVoices.value.length === 0 && systemVoices.value.length > 0) {
        voiceListTab.value = 'system';
      }
    }
  } catch (error: any) {
    ElMessage.error(`Failed to load voices: ${error.message}`);
  } finally {
    loadingVoices.value = false;
  }
}

function isUserDefinedVoice(voice: Voice) {
  const voiceData = voice as Voice & {
    category?: string;
    labels?: {
      description?: string;
      source?: string;
    };
  };
  const category = (voiceData.category || '').toLowerCase();
  const source = (voiceData.labels?.source || '').toLowerCase();

  return voice.voice_id.startsWith('xtts_') || category === 'cloned' || category === 'generated' || source === 'user';
}

async function handleDeleteVoice(voiceId: string) {
  try {
    deletingVoice.value = voiceId;
    await deleteVoiceAPI(voiceId);
    ElMessage.success('Voice deleted');
    await loadVoices();
    if (appStore.voiceId === voiceId) {
      appStore.reset(); // Or just reset voice part
    }
  } catch (error: any) {
    ElMessage.error(`Delete failed: ${error.message}`);
  } finally {
    deletingVoice.value = null;
  }
}

async function testVoice(voiceId: string) {
  try {
    testingVoice.value = voiceId;
    testAudioUrl.value = null;
    const text = 'Hello, this is a voice test.';
    const audioBlob = await quickTTS(text, voiceId);
    testAudioUrl.value = URL.createObjectURL(audioBlob);
  } catch (error: any) {
    ElMessage.error(`Test failed: ${error.message}`);
  } finally {
    testingVoice.value = null;
  }
}

async function saveToBlockchain() {
  if (!cloneResult.value || !cloneResult.value.voice_id || !appStore.walletAddress) {
    ElMessage.error('Missing voice ID or wallet address');
    return;
  }
  
  savingToBlockchain.value = true;
  try {
    // Mock IPFS hash for demo
    const ipfsHash = `QmVxPwNP` + cloneResult.value.voice_id.slice(0, 24);
    
    const result = await saveVoiceToBlockchain(
      cloneResult.value.voice_id,
      cloneResult.value.voice_name,
      ipfsHash,
      appStore.walletAddress
    );
    
    if (result.success) {
      cloneResult.value.blockchain_saved = true;
      ElMessage.success(`Voice saved to blockchain! Tx: ${result.tx_hash?.slice(0, 10)}...`);
    } else {
      ElMessage.error(`Failed to save: ${result.error}`);
    }
  } catch (error: any) {
    ElMessage.error(`Blockchain save failed: ${error.message}`);
  } finally {
    savingToBlockchain.value = false;
  }
}

// IPFS 工具函数
function shortenIPFSHash(hash: string): string {
  return shortenHash(hash, 8, 6);
}

async function copyIPFSHash(hash: string) {
  const success = await copyHash(hash);
  if (success) {
    ElMessage.success('IPFS hash copied to clipboard!');
  } else {
    ElMessage.error('Failed to copy IPFS hash');
  }
}

function openIPFSGateway(hash: string) {
  const url = getIPFSExplorerUrl(hash);
  window.open(url, '_blank');
}

function proceedToNextStep() {
  emit('next-step');
}
</script>

<style scoped lang="scss">
.voice-clone {
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

  .audio-uploader {
    width: 100%;
    :deep(.el-upload-dragger) {
      padding: 30px;
    }
    .el-upload__tip {
      margin-top: 10px;
      line-height: 1.6;
      ul {
        padding-left: 20px;
        margin: 5px 0;
      }
    }
  }

  .audio-preview {
    margin-top: 20px;
  }

  .voice-list {
    max-height: 400px;
    overflow-y: auto;
    .voice-item {
      display: flex;
      align-items: center;
      padding: 12px;
      margin-bottom: 10px;
      border-radius: 8px;
      border: 1px solid #e4e7ed;
      transition: all 0.3s ease;

      &.active {
        border-color: #409eff;
        box-shadow: 0 0 5px rgba(64, 158, 255, 0.5);
      }

      .voice-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        flex-grow: 1;
      }
      .voice-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex-grow: 2;
        font-size: 12px;
      }
      .voice-actions {
        display: flex;
        gap: 8px;
      }
    }
  }
}
</style>
