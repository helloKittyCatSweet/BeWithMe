<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="BeWithMe Logo" />
        <h1>BeWithMe</h1>
      </div>
      <div class="progress-bar">
        <el-progress :percentage="appStore.setupProgress" :stroke-width="10" striped />
      </div>
      <div class="user-info">
        <span>用户ID: {{ appStore.currentUserId }}</span>
        <el-button type="danger" plain @click="handleReset" :icon="Refresh">
          重置所有
        </el-button>
      </div>
    </el-header>

    <el-main class="main-content">
      <el-steps :active="appStore.currentStep" finish-status="success" simple>
        <el-step title="家庭验证" :icon="User" />
        <el-step title="声音克隆" :icon="Microphone" />
        <el-step title="创建代理" :icon="Cpu" />
        <el-step title="开始对话" :icon="ChatDotRound" />
      </el-steps>

      <div class="step-content">
        <FamilyVerification 
          v-if="appStore.currentStep === 0"
          @verification-complete="goToStep(1)"
        />
        <VoiceClone 
          v-if="appStore.currentStep === 1"
          @clone-success="handleCloneSuccess"
          @next-step="goToStep(2)"
        />
        <AgentCreation 
          v-if="appStore.currentStep === 2"
          @creation-success="handleAgentCreation"
          @next-step="goToStep(3)"
        />
        <Chat 
          v-if="appStore.currentStep === 3"
        />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useAppStore } from '@/stores/app';
import FamilyVerification from './components/FamilyVerification.vue';
import VoiceClone from './components/VoiceClone.vue';
import AgentCreation from './components/AgentCreation.vue';
import Chat from './components/Chat.vue';
import { User, Microphone, Cpu, ChatDotRound, Refresh } from '@element-plus/icons-vue';

const appStore = useAppStore();

onMounted(async () => {
  await appStore.fetchSystemStatus();
});

function goToStep(step: number) {
  appStore.setCurrentStep(step);
}

function handleCloneSuccess(voiceId: string, voiceName: string) {
  appStore.setVoiceCloned(voiceId, voiceName);
  goToStep(2);
}

function handleAgentCreation(agentName: string) {
  appStore.setAgentCreated(agentName);
  goToStep(3);
}

function handleReset() {
  ElMessageBox.confirm(
    '这将重置所有代理和声音设置，并清空聊天记录。此操作不可逆，确定要继续吗？',
    '警告',
    {
      confirmButtonText: '确定重置',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    appStore.reset();
    ElMessage.success('所有设置已重置');
    // You might want to call a backend endpoint to clear server-side data as well
  }).catch(() => {
    // Cancelled
  });
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  background-color: #f0f2f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    img {
      height: 40px;
    }
    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }

  .progress-bar {
    width: 300px;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 15px;
  }
}

.main-content {
  padding: 20px;
}

.step-content {
  margin-top: 20px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
</style>

