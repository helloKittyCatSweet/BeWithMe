<template>
  <div class="agent-creation">
    <div class="header">
      <h2>🧠 Step 2: Create Digital Agent</h2>
      <p class="subtitle">Create a digital agent based on your loved one's information.</p>
    </div>

    <el-alert
      v-if="!appStore.voiceCloned"
      type="warning"
      title="⚠️ Voice Cloning Required"
      description="Please complete Voice Cloning in Step 1 first."
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
              <span>🤖 Create New Agent</span>
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
            <el-form-item label="Agent Name" prop="name">
              <el-input 
                v-model="agentForm.name" 
                placeholder="e.g. Kind Father"
              />
            </el-form-item>

            <el-form-item label="Relationship" prop="relationship">
              <el-input 
                v-model="agentForm.relationship" 
                placeholder="e.g. Father"
              />
            </el-form-item>

            <el-form-item label="Personality Traits" prop="personality_traits">
              <el-input
                v-model="agentForm.personality_traits"
                type="textarea"
                :rows="3"
                placeholder="Describe traits, e.g. kind, patient, humorous, wise"
              />
            </el-form-item>

            <el-form-item label="Speech Patterns" prop="speech_patterns">
              <el-select
                v-model="agentForm.speech_patterns"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="Enter catchphrases or common sayings, press Enter"
                style="width: 100%;"
              >
              </el-select>
              <el-text size="small" type="info" style="margin-top: 5px; display: block;">
                e.g., 'You little rascal', 'Take care of yourself'
              </el-text>
            </el-form-item>

            <el-form-item label="Background Story" prop="background_story">
              <el-input
                v-model="agentForm.background_story"
                type="textarea"
                :rows="5"
                placeholder="Describe life events, important experiences, career, etc."
              />
            </el-form-item>
            
            <el-form-item label="Shared Memories" prop="memories">
              <el-input
                v-model="memoriesInput"
                type="textarea"
                :rows="4"
                placeholder="Enter shared memories, one per line"
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
                Create Agent
              </el-button>
              <el-button @click="resetForm" :disabled="creating">
                Reset
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
              <span>ℹ️ Agent Info</span>
            </div>
          </template>
          <div v-if="appStore.agentCreated">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Agent Name">{{ appStore.agentName }}</el-descriptions-item>
              <el-descriptions-item label="Status">
                <el-tag type="success">Created</el-tag>
              </el-descriptions-item>
            </el-descriptions>
            <el-button
              type="success"
              style="margin-top: 20px; width: 100%;"
              @click="proceedToNextStep"
              :icon="ChatDotRound"
            >
              Start Chat →
            </el-button>
            <el-button
              v-if="enableAgentChainProof && appStore.walletAddress && !agentBlockchainSaved"
              type="warning"
              style="margin-top: 10px; width: 100%;"
              @click="saveAgentBlockchain"
              :loading="savingBlockchain"
            >
              🔗 Save Hash Proof On-chain
            </el-button>
            <div v-if="agentBlockchainSaved" style="margin-top: 15px; padding: 15px; background: #f0f9ff; border-radius: 4px; border-left: 4px solid #67c23a;">
              <p style="margin: 0 0 8px 0; font-size: 14px; color: #67c23a; font-weight: 600;">✅ Saved to Blockchain</p>
              <p style="margin: 0; font-size: 12px; color: #606266; word-break: break-all;">
                TX: <span style="font-family: monospace;">{{ agentTxHash.substring(0, 10) }}...{{ agentTxHash.substring(agentTxHash.length - 8) }}</span>
              </p>
            </div>
            <el-button
              type="danger"
              style="margin-top: 10px; width: 100%;"
              @click="handleResetAgent"
              :loading="reseting"
              :icon="RefreshLeft"
            >
              Reset Agent
            </el-button>
          </div>
          <el-empty v-else description="No agent created yet" />
        </el-card>

        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span>💡 Tips</span>
          </template>
          <div class="tips-content">
            <h4>How to create a more realistic agent?</h4>
            <ul>
              <li><strong>Detail is key</strong>: The more specific information you provide, the more realistic the agent will behave.</li>
              <li><strong>Diverse catchphrases</strong>: Adding multiple speech habits makes conversations more natural.</li>
              <li><strong>Rich stories</strong>: Background stories and shared memories are core to shaping the agent's long-term memory and personality.</li>
              <li><strong>Iterate</strong>: You can reset and recreate the agent with updated information at any time.</li>
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
import { createAgent, resetAgent, saveAgentToBlockchain } from '@/services/api';
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
  name: [{ required: true, message: 'Please enter agent name', trigger: 'blur' }],
  relationship: [{ required: true, message: 'Please enter relationship', trigger: 'blur' }],
  personality_traits: [{ required: true, message: 'Please describe personality traits', trigger: 'blur' }],
});

const creating = ref(false);
const reseting = ref(false);
const savingBlockchain = ref(false);
const agentBlockchainSaved = ref(false);
const agentTxHash = ref('');
const enableAgentChainProof = false;

onMounted(() => {
  // Pre-fill from relationship if possible
  if (appStore.approvedRelationships.length > 0) {
    const rel = appStore.approvedRelationships[0];
    agentForm.name = `Digital ${rel.relative_name}`;
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
        ElMessage.success('Agent Created Successfully!');
        appStore.setAgentCreated(result.agent_name);
        emit('creation-success', result.agent_name);
      } else {
        throw new Error(result.message);
      }
    } catch (error: any) {
      ElMessage.error(`Creation Failed: ${error.response?.data?.detail || error.message}`);
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
    ElMessage.success('Agent Reset');
    appStore.reset(); // Full reset
  } catch (error: any) {
    ElMessage.error(`Reset Failed: ${error.message}`);
  } finally {
    reseting.value = false;
  }
}

function proceedToNextStep() {
  emit('next-step');
}

async function saveAgentBlockchain() {
  if (!appStore.walletAddress) {
    ElMessage.error('Please connect wallet first');
    return;
  }
  
  savingBlockchain.value = true;
  try {
    const proofInput = JSON.stringify({
      agent_name: agentForm.name,
      relationship: agentForm.relationship,
      personality_traits: agentForm.personality_traits,
      speech_patterns: agentForm.speech_patterns,
    });

    let ipfsHash = `sha256:${Date.now()}`;
    if (window?.crypto?.subtle) {
      const encoder = new TextEncoder();
      const digest = await crypto.subtle.digest('SHA-256', encoder.encode(proofInput));
      const hex = Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, '0')).join('');
      ipfsHash = `sha256:${hex}`;
    }
    
    const response = await saveAgentToBlockchain({
      agent_name: agentForm.name,
      ipfs_hash: ipfsHash,
      wallet_address: appStore.walletAddress,
      agent_data: {
        proof_type: 'hash_only',
      }
    });
    
    if (response.success && response.tx_hash) {
      agentTxHash.value = response.tx_hash;
      agentBlockchainSaved.value = true;
      ElMessage.success(`Agent hash proof saved on-chain! Tx: ${response.tx_hash}`);
    } else {
      throw new Error('Failed to save agent proof');
    }
  } catch (error: any) {
    ElMessage.error(`Blockchain save failed: ${error.response?.data?.detail || error.message}`);
  } finally {
    savingBlockchain.value = false;
  }
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
