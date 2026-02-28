<template>
  <div class="voice-clone">
    <div class="header">
      <h2>🎙️ Step 1: Voice Cloning</h2>
      <p class="subtitle">上传音频样本来克隆您所爱之人的声音</p>
    </div>

    <el-alert
      v-if="!appStore.hasApprovedRelationship"
      type="warning"
      title="⚠️ 需要先通过家庭关系验证"
      description="请先在 Step 0 完成家庭关系验证并获得批准，然后刷新页面。"
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
              <span>🎤 克隆新声音</span>
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
            <el-form-item label="选择关系" prop="relationship_id">
              <el-select 
                v-model="cloneForm.relationship_id" 
                placeholder="选择已验证的关系"
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
                只能使用已通过验证的关系
              </el-text>
            </el-form-item>

            <el-form-item label="声音名称" prop="voice_name">
              <el-input 
                v-model="cloneForm.voice_name" 
                placeholder="例如：爸爸的声音"
                clearable
              />
            </el-form-item>

            <el-form-item label="描述" prop="description">
              <el-input
                v-model="cloneForm.description"
                type="textarea"
                :rows="3"
                placeholder="描述这个声音的特点，例如：温暖、低沉、有磁性"
                clearable
              />
            </el-form-item>

            <el-form-item label="音频文件" prop="audio_file">
              <el-upload
                ref="audioUploadRef"
                class="audio-uploader"
                drag
                :auto-upload="false"
                :limit="1"
                :on-change="handleAudioChange"
                :on-remove="handleAudioRemove"
                accept="audio/wav,audio/mpeg,audio/mp4,audio/flac"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到这里 或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    <p>📋 <strong>音频要求：</strong></p>
                    <ul>
                      <li>格式: WAV, MP3, M4A, FLAC</li>
                      <li>时长: 10秒 - 5分钟</li>
                      <li>质量: 清晰、无噪音、单人声</li>
                    </ul>
                  </div>
                </template>
              </el-upload>

              <!-- Audio Preview -->
              <div v-if="audioPreviewUrl" class="audio-preview">
                <el-divider content-position="left">音频预览</el-divider>
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
                开始克隆声音
              </el-button>
              <el-button 
                @click="resetForm"
                :disabled="cloning"
              >
                重置
              </el-button>
            </el-form-item>

            <!-- Progress -->
            <el-collapse-transition>
              <div v-if="cloning" style="margin-top: 20px;">
                <el-divider>🔄 克隆进度</el-divider>
                <el-steps :active="cloneStep" finish-status="success" align-center>
                  <el-step title="上传音频" />
                  <el-step title="分析音频" />
                  <el-step title="训练模型" />
                  <el-step title="生成声音" />
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
              :title="cloneResult.success ? '✅ 声音克隆成功！' : '❌ 克隆失败'"
              :closable="false"
              show-icon
              style="margin-top: 20px;"
            >
              <div v-if="cloneResult.success">
                <p><strong>Voice ID:</strong> {{ cloneResult.voice_id }}</p>
                <p><strong>Voice Name:</strong> {{ cloneResult.voice_name }}</p>
                <p>{{ cloneResult.message }}</p>
                
                <div v-if="cloneResult.analysis" style="margin-top: 10px;">
                  <el-divider content-position="left">音频分析</el-divider>
                  <ul>
                    <li><strong>时长:</strong> {{ cloneResult.analysis.duration?.toFixed(2) }}秒</li>
                    <li><strong>采样率:</strong> {{ cloneResult.analysis.sample_rate }} Hz</li>
                    <li><strong>声道数:</strong> {{ cloneResult.analysis.channels }}</li>
                    <li><strong>质量评分:</strong> {{ cloneResult.analysis.quality_score }}/100</li>
                  </ul>
                </div>

                <el-button 
                  type="success" 
                  style="margin-top: 15px;"
                  @click="proceedToNextStep"
                >
                  继续下一步: 创建对话代理 →
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
              <span>🎵 已克隆的声音</span>
              <el-button 
                size="small" 
                text
                @click="loadVoices"
                :loading="loadingVoices"
                :icon="Refresh"
              >
                刷新
              </el-button>
            </div>
          </template>

          <div v-if="voices.length > 0" class="voice-list">
            <div 
              v-for="voice in voices" 
              :key="voice.voice_id"
              class="voice-item"
              :class="{ active: voice.voice_id === appStore.voiceId }"
            >
              <div class="voice-header">
                <el-icon><Avatar /></el-icon>
                <span class="voice-name">{{ voice.name }}</span>
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
                  测试
                </el-button>
                <el-popconfirm
                  title="确定删除这个声音吗？"
                  @confirm="handleDeleteVoice(voice.voice_id)"
                >
                  <template #reference>
                    <el-button size="small" type="danger" :loading="deletingVoice === voice.voice_id" :icon="Delete">
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>

          <el-empty v-else description="还没有克隆任何声音" />
        </el-card>

        <!-- Test Output -->
        <el-card v-if="testAudioUrl" style="margin-top: 20px;" shadow="hover">
          <template #header>
            <span>🔊 测试输出</span>
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
  Avatar
} from '@element-plus/icons-vue';
import type { FormInstance, FormRules, UploadFile, UploadInstance } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { cloneVoice, listVoices, deleteVoice as deleteVoiceAPI, quickTTS } from '@/services/api';
import type { VoiceCloneRequest, VoiceCloneResponse, Voice } from '@/types/api';
import { getRelationshipLabel } from '@/utils/format';
import { validateAudioFile } from '@/utils/audio';

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
  relationship_id: [{ required: true, message: '请选择一个已验证的关系', trigger: 'change' }],
  voice_name: [{ required: true, message: '请输入声音名称', trigger: 'blur' }],
  audio_file: [{ required: true, message: '请上传音频文件' }],
});

const cloning = ref(false);
const cloneStep = ref(0);
const cloneProgress = ref('');
const cloneResult = ref<VoiceCloneResponse | null>(null);
const audioPreviewUrl = ref<string | null>(null);

const voices = ref<Voice[]>([]);
const loadingVoices = ref(false);
const deletingVoice = ref<string | null>(null);
const testingVoice = ref<string | null>(null);
const testAudioUrl = ref<string | null>(null);

onMounted(async () => {
  await loadVoices();
});

function handleRelationshipChange(id: number) {
  const rel = appStore.approvedRelationships.find(r => r.id === id);
  if (rel) {
    cloneForm.voice_name = `${rel.relative_name}的声音`;
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
      cloneProgress.value = '正在上传音频文件...';
      await new Promise(res => setTimeout(res, 1000));

      cloneStep.value = 2;
      cloneProgress.value = '服务器正在分析音频特征... (这可能需要几分钟)';
      
      const result = await cloneVoice(request);
      cloneResult.value = result;

      if (result.success) {
        cloneStep.value = 4;
        cloneProgress.value = '克隆成功！';
        ElMessage.success('声音克隆成功！');
        appStore.setVoiceCloned(result.voice_id, result.voice_name);
        emit('clone-success', result.voice_id, result.voice_name);
        await loadVoices();
      } else {
        throw new Error(result.message);
      }
    } catch (error: any) {
      cloneStep.value = 0;
      ElMessage.error(`克隆失败: ${error.response?.data?.detail || error.message}`);
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
    }
  } catch (error: any) {
    ElMessage.error(`加载声音列表失败: ${error.message}`);
  } finally {
    loadingVoices.value = false;
  }
}

async function handleDeleteVoice(voiceId: string) {
  try {
    deletingVoice.value = voiceId;
    await deleteVoiceAPI(voiceId);
    ElMessage.success('声音已删除');
    await loadVoices();
    if (appStore.voiceId === voiceId) {
      appStore.reset(); // Or just reset voice part
    }
  } catch (error: any) {
    ElMessage.error(`删除失败: ${error.message}`);
  } finally {
    deletingVoice.value = null;
  }
}

async function testVoice(voiceId: string) {
  try {
    testingVoice.value = voiceId;
    testAudioUrl.value = null;
    const text = '你好，这是一个声音测试。';
    const audioBlob = await quickTTS(text, voiceId);
    testAudioUrl.value = URL.createObjectURL(audioBlob);
  } catch (error: any) {
    ElMessage.error(`测试失败: ${error.message}`);
  } finally {
    testingVoice.value = null;
  }
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
