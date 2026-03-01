<template>
  <div v-if="route.path === '/login'">
    <Login @login-success="handleLoginSuccess" />
  </div>
  <el-container v-else class="main-layout">
    <el-aside width="250px" class="aside">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="BeWithMe Logo" />
        <h1>BeWithMe</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        @select="handleSelect"
      >
        <el-menu-item index="verification">
          <el-icon><User /></el-icon>
          <span>Family Verification</span>
        </el-menu-item>
        <el-menu-item index="voice-clone">
          <el-icon><Microphone /></el-icon>
          <span>Voice Cloning</span>
        </el-menu-item>
        <el-menu-item index="create-agent">
          <el-icon><Cpu /></el-icon>
          <span>Create Agent</span>
        </el-menu-item>
        <el-menu-item index="phone-call">
          <el-icon><Phone /></el-icon>
          <span>Phone Call</span>
        </el-menu-item>
        <el-menu-item index="user-profile">
          <el-icon><Setting /></el-icon>
          <span>User Profile</span>
        </el-menu-item>
        <el-menu-item index="trust-security">
          <el-icon><Lock /></el-icon>
          <span>Trust & Security</span>
        </el-menu-item>
        <el-menu-item v-if="appStore.isAdmin" index="admin-review">
          <el-icon><UserFilled /></el-icon>
          <span>Admin Review</span>
        </el-menu-item>
      </el-menu>
      
      <div class="user-info-bottom">
        <div v-if="appStore.walletAddress" class="wallet-info">
          <el-icon><Wallet /></el-icon> 
          {{ appStore.walletAddress.substring(0, 6) }}...{{ appStore.walletAddress.substring(38) }}
        </div>
        <el-button type="warning" plain @click="handleLogout" :icon="SwitchButton" size="small" style="width: 100%; margin-top: 10px;">
          Logout
        </el-button>
        <el-button type="danger" plain @click="handleReset" :icon="Refresh" size="small" style="width: 100%; margin-top: 10px;">
          Reset All
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <h2>{{ currentTitle }}</h2>
        <div class="progress-bar">
          <span class="progress-label">Setup Progress:</span>
          <el-progress :percentage="appStore.setupProgress" :stroke-width="10" striped style="width: 200px" />
        </div>
      </el-header>

      <el-main class="main-content">
        <FamilyVerification 
          v-if="activeMenu === 'verification'"
          @verification-complete="handleSelect('voice-clone')"
        />
        <VoiceClone 
          v-if="activeMenu === 'voice-clone'"
          @clone-success="handleCloneSuccess"
          @next-step="handleSelect('create-agent')"
        />
        <AgentCreation 
          v-if="activeMenu === 'create-agent'"
          @creation-success="handleAgentCreation"
          @next-step="handleSelect('phone-call')"
        />
        <PhoneCall 
          v-if="activeMenu === 'phone-call'"
        />
        <UserProfile 
          v-if="activeMenu === 'user-profile'"
        />
        <TrustAndSecurity
          v-if="activeMenu === 'trust-security'"
        />
        <AdminReview
          v-if="activeMenu === 'admin-review'"
        />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { useRoute, useRouter } from 'vue-router';
import Login from './components/Login.vue';
import FamilyVerification from './components/FamilyVerification.vue';
import VoiceClone from './components/VoiceClone.vue';
import AgentCreation from './components/AgentCreation.vue';
import PhoneCall from './components/PhoneCall.vue';
import UserProfile from './components/UserProfile.vue';
import TrustAndSecurity from './components/TrustAndSecurity.vue';
import AdminReview from './components/AdminReview.vue';
import { User, Microphone, Cpu, Phone, Refresh, Wallet, Setting, UserFilled, SwitchButton, Lock } from '@element-plus/icons-vue';

const appStore = useAppStore();
const route = useRoute();
const router = useRouter();

const SESSION_KEY = 'app_session';

const menuToPath: Record<string, string> = {
  'verification': '/verification',
  'voice-clone': '/voice-clone',
  'create-agent': '/create-agent',
  'phone-call': '/phone-call',
  'user-profile': '/user-profile',
  'trust-security': '/trust-security',
  'admin-review': '/admin-review'
};

const pathToMenu: Record<string, string> = {
  '/verification': 'verification',
  '/voice-clone': 'voice-clone',
  '/create-agent': 'create-agent',
  '/phone-call': 'phone-call',
  '/user-profile': 'user-profile',
  '/trust-security': 'trust-security',
  '/admin-review': 'admin-review'
};

const titles: Record<string, string> = {
  'verification': 'Family Verification',
  'voice-clone': 'Voice Cloning',
  'create-agent': 'Create Agent',
  'phone-call': 'Phone Call Simulation',
  'user-profile': 'User Profile',
  'trust-security': 'Trust & Security',
  'admin-review': 'Admin Review'
};

const activeMenu = computed(() => pathToMenu[route.path] || 'verification');
const currentTitle = computed(() => titles[activeMenu.value]);

function persistSession() {
  localStorage.setItem(SESSION_KEY, JSON.stringify({
    isLoggedIn: appStore.isLoggedIn,
    isAdmin: appStore.isAdmin,
    userId: appStore.currentUserId,
    walletAddress: appStore.walletAddress,
  }));
}

function restoreSession() {
  const rawSession = localStorage.getItem(SESSION_KEY);
  if (!rawSession) return;

  try {
    const session = JSON.parse(rawSession) as {
      isLoggedIn?: boolean;
      isAdmin?: boolean;
      userId?: number;
      walletAddress?: string | null;
    };

    if (session.isLoggedIn) {
      appStore.setLoggedIn(true, session.walletAddress || undefined, !!session.isAdmin);
      if (typeof session.userId === 'number') {
        appStore.setCurrentUserId(session.userId);
      }
    }
  } catch {
    localStorage.removeItem(SESSION_KEY);
  }
}

onMounted(async () => {
  restoreSession();
  if (appStore.isLoggedIn) {
    await appStore.fetchSystemStatus();
  }
});

watch(
  () => appStore.isLoggedIn,
  async (loggedIn) => {
    if (loggedIn && route.path === '/login') {
      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/verification';
      await router.replace(redirect);
    }
    if (loggedIn) {
      persistSession();
    }
  }
);

function handleLoginSuccess(data: any) {
  if (data.type === 'wallet') {
    appStore.setLoggedIn(true, data.address, !!data.isAdmin);
  } else {
    appStore.setLoggedIn(true, undefined, !!data.isAdmin);
    if (typeof data.userId === 'number') {
      appStore.setCurrentUserId(data.userId);
    }
  }
  persistSession();

  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/verification';
  router.replace(redirect);
}

function handleSelect(index: string) {
  if (index === 'admin-review' && !appStore.isAdmin) {
    ElMessage.warning('Admin access required');
    return;
  }
  const path = menuToPath[index] || '/verification';
  router.push(path);
}

function handleLogout() {
  ElMessageBox.confirm(
    'Are you sure you want to logout?',
    'Confirm Logout',
    {
      confirmButtonText: 'Logout',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem(SESSION_KEY);
    appStore.logout();
    router.replace('/login');
    ElMessage.success('Logged out successfully');
  }).catch(() => {});
}

function handleCloneSuccess(voiceId: string, voiceName: string) {
  appStore.setVoiceCloned(voiceId, voiceName);
  handleSelect('create-agent');
}

function handleAgentCreation(agentName: string) {
  appStore.setAgentCreated(agentName);
  handleSelect('phone-call');
}

function handleReset() {
  ElMessageBox.confirm(
    'This will reset all agent and voice settings, and clear chat history. This action cannot be undone. Continue?',
    'Warning',
    {
      confirmButtonText: 'Reset',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    appStore.reset();
    router.replace('/verification');
    ElMessage.success('All settings reset.');
  }).catch(() => {});
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  background-color: #f0f2f5;
}

.aside {
  background-color: #ffffff;
  border-right: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  
  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 20px;
    border-bottom: 1px solid #f0f0f0;
    
    img {
      height: 32px;
    }
    h1 {
      font-size: 20px;
      margin: 0;
      color: #303133;
    }
  }

  .el-menu-vertical {
    border-right: none;
    flex: 1;
  }
  
  .user-info-bottom {
    padding: 20px;
    border-top: 1px solid #f0f0f0;
    background-color: #fafafa;
    
    .wallet-info {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: #67c23a;
      justify-content: center;
    }
  }
}

.header {
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  
  h2 {
    font-size: 18px;
    margin: 0;
    font-weight: 500;
  }
  
  .progress-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .progress-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}
</style>

