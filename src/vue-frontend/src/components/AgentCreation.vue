<template>
  <div class="agent-creation">
    <div class="header">
      <h2>🧠 Step 2: Create Digital Agent</h2>
      <p class="subtitle">根据您所爱之人的信息，创建一个数字代理</p>
    </div>

    <el-alert
      v-if="!appStore.voiceCloned"
      type="warning"
      title="⚠️ 需要先完成声音克隆"
      description="请先在 Step 1 完成声音克隆"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />

    <el-row :gutter="20">
      <!-- Agent Form -->
      <el-col :md="14" :sm="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🤖 创建新的代理</span>
            </div>
          </template>

          <el-form
            ref="agentFormRef"
            :model="agentForm"
            :rules="agentRules"
            label-position="top"
            :disabled="!appStore.voiceCloned"
            @submit.prevent="submitAgent"
          >
            <el-form-item label="代理名称" prop="name">
              <el-input 
                v-model="agentForm.name" 
                placeholder="例如：慈祥的父亲"
              />
            </el-form-item>

            <el-form-item label="与您的关系" prop="relationship">
              <el-input 
                v-model="agentForm.relationship" 
                placeholder="例如：父亲"
              />
            </el-form-item>

            <el-form-item label="性格特点" prop="personality_traits">
              <el-input
                v-model="agentForm.personality_traits"
                type="textarea"
                :rows="3"
                placeholder="描述性格，例如：善良、有耐心、幽默、喜欢讲道理"
              />
            </el-form-item>

            <el-form-item label="说话习惯" prop="speech_patterns">
              <el-select
                v-model="agentForm.speech_patterns"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="输入口头禅或常用语，按回车确认"
                style="width: 100%;"
              >
              </el-select>
              <el-text size="small" type="info" style="margin-top: 5px; display: block;">
                例如：“你这个小家伙”、“要注意身体啊”
              </el-text>
            </el-form-item>

            <el-form-item label="背景故事" prop="background_story">
              <el-input
                v-model="agentForm.background_story"
                type="textarea"
                :rows="5"
                placeholder="描述其生平、重要经历、职业等"
              />
            </el-form-item>
            
            <el-form-item label="共同回忆" prop="memories">
              <el-input
                v-model="memoriesInput"
                type="textarea"
                :rows="4"
                placeholder="输入你们之间的共同回忆，每条回忆占一行"
                @change="updateMemories"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                @click="submitAgent"
                :loading="creating"
                :disabled="!appStore.voiceCloned"
                :icon="Cpu"
              >
                创建代理
              </el-button>
              <el-button @click="resetForm" :disabled="creating">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Info & Status -->
      <el-col :md="10" :sm="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>ℹ️ 代理信息</span>
            </div>
          </template>
          <div v-if="appStore.agentCreated">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="代理名称">{{ appStore.agentName }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag type="success">已创建</el-tag>
              </el-descriptions-item>
            </el-descriptions>
            <el-button
              type="success"
              style="margin-top: 20px; width: 100%;"
              @click="proceedToNextStep"
              :icon="ChatDotRound"
            >
              开始对话 →
            </el-button>
            <el-button
              type="danger"
              style="margin-top: 10px; width: 100%;"
              @click="handleResetAgent"
              :loading="reseting"
              :icon="RefreshLeft"
            >
              重置代理
            </el-button>
          </div>
          <el-empty v-else description="尚未创建代理" />
        </el-card>

        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span>💡 提示</span>
          </template>
          <div class="tips-content">
            <h4>如何创建更真实的代理？</h4>
            <ul>
              <li><strong>细节是关键</strong>: 提供越详细、越具体的信息，代理的行为就越真实。</li>
              <li><strong>多样的口头禅</strong>: 添加多个说话习惯，能让对话更自然。</li>
              <li><strong>丰富的故事</strong>: 背景故事和共同回忆是塑造代理长期记忆和个性的核心。</li>
              <li><strong>持续迭代</strong>: 您可以随时重置并使用更新的信息重新创建代理。</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Cpu, ChatDotRound, RefreshLeft } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { createAgent, resetAgent } from '@/services/api';
import type { AgentProfile } from '@/types/api';

const emit = defineEmits<{
  'creation-success': [agentName: string],
  'next-step': []
}>();

const appStore = useAppStore();
const agentFormRef = ref<FormInstance>();

const agentForm = reactive<AgentProfile>({
  name: '',
  relationship: '',
  personality_traits: '',
  speech_patterns: [],
  background_story: '',
  memories: [],
});

const memoriesInput = ref('');

const agentRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入代理名称', trigger: 'blur' }],
  relationship: [{ required: true, message: '请输入与您的关系', trigger: 'blur' }],
  personality_traits: [{ required: true, message: '请描述性格特点', trigger: 'blur' }],
});

const creating = ref(false);
const reseting = ref(false);

onMounted(() => {
  // Pre-fill from relationship if possible
  if (appStore.approvedRelationships.length > 0) {
    const rel = appStore.approvedRelationships[0];
    agentForm.name = `数字化的${rel.relative_name}`;
    agentForm.relationship = rel.relative_name;
  }
});

function updateMemories() {
  agentForm.memories = memoriesInput.value.split('\n').filter(line => line.trim() !== '');
}

async function submitAgent() {
  if (!agentFormRef.value) return;
  await agentFormRef.value.validate(async (valid) => {
    if (!valid) return;

    creating.value = true;
    try {
      const result = await createAgent(agentForm);
      if (result.success) {
        ElMessage.success('代理创建成功！');
        appStore.setAgentCreated(result.agent_name);
        emit('creation-success', result.agent_name);
      } else {
        throw new Error(result.message);
      }
    } catch (error: any) {
      ElMessage.error(`创建失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      creating.value = false;
    }
  });
}

function resetForm() {
  agentFormRef.value?.resetFields();
  memoriesInput.value = '';
  agentForm.memories = [];
}

async function handleResetAgent() {
  reseting.value = true;
  try {
    await resetAgent();
    ElMessage.success('代理已重置');
    appStore.reset(); // Full reset
  } catch (error: any) {
    ElMessage.error(`重置失败: ${error.message}`);
  } finally {
    reseting.value = false;
  }
}

function proceedToNextStep() {
  emit('next-step');
}
</script>

<style scoped lang="scss">
.agent-creation {
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

  .tips-content {
    ul {
      padding-left: 20px;
      line-height: 1.8;
    }
  }
}
</style>
