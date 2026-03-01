<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="BeWithMe Logo" />
        <h1>BeWithMe</h1>
        <p class="subtitle">Connecting hearts, eternally.</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="Wallet Login" name="wallet">
          <div class="wallet-login">
            <p class="info-text">Connect your Web3 wallet to access your memories on the blockchain.</p>
            <el-button 
              type="primary" 
              size="large" 
              class="wallet-btn" 
              @click="handleWalletLogin"
              :loading="loading"
            >
              <el-icon class="el-icon--left"><Wallet /></el-icon>
              Connect Wallet
            </el-button>
            <p v-if="error" class="error-text">{{ error }}</p>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Email Login" name="email">
          <el-form label-position="top" :model="form" @submit.prevent="isRegisterMode ? handleEmailRegister() : handleEmailLogin()">
            <el-form-item v-if="isRegisterMode" label="Username">
              <el-input v-model="form.username" placeholder="Your name" />
            </el-form-item>
            <el-form-item label="Email">
              <el-input v-model="form.email" placeholder="name@example.com" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="form.password" type="password" placeholder="********" />
            </el-form-item>
            <el-button type="primary" native-type="submit" class="full-width" :loading="loading">
              {{ isRegisterMode ? 'Register' : 'Login' }}
            </el-button>
            <div class="switch-mode">
              <el-button text link @click="toggleMode">
                {{ isRegisterMode ? 'Already have an account? Login' : "Don't have an account? Register" }}
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Wallet } from '@element-plus/icons-vue';
import { connectWallet } from '@/services/contract';
import { loginWithEmail, registerUser } from '@/services/api';
import { useAppStore } from '@/stores/app';

const emit = defineEmits(['login-success']);
const appStore = useAppStore();

const activeTab = ref('wallet');
const loading = ref(false);
const error = ref('');
const isRegisterMode = ref(false);

const form = reactive({
  username: '',
  email: '',
  password: ''
});

function toggleMode() {
  isRegisterMode.value = !isRegisterMode.value;
  form.username = '';
  form.email = '';
  form.password = '';
}

async function handleWalletLogin() {
  loading.value = true;
  error.value = '';
  try {
    const { address, signer } = await connectWallet();
    ElMessage.success(`Wallet connected: ${address.substring(0, 6)}...${address.substring(38)}`);
    // Store wallet info in app store if needed
    // appStore.setWalletAddress(address);
    emit('login-success', { type: 'wallet', address });
  } catch (err: any) {
    console.error(err);
    error.value = err.message || 'Failed to connect wallet';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function handleEmailLogin() {
  loading.value = true;
  (async () => {
    try {
      if (!form.email || !form.password) {
        ElMessage.error('Please enter email and password');
        return;
      }

      const result = await loginWithEmail(form.email, form.password);
      localStorage.setItem('auth_token', result.access_token);
      ElMessage.success('Login successful');
      emit('login-success', {
        type: 'email',
        email: form.email,
        isAdmin: result.user.is_admin,
        userId: result.user.id,
      });
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || 'Login failed');
    } finally {
      loading.value = false;
    }
  })();
}

async function handleEmailRegister() {
  loading.value = true;
  (async () => {
    try {
      if (!form.username || !form.email || !form.password) {
        ElMessage.error('Please fill in all fields');
        return;
      }

      const result = await registerUser(form.username, form.email, form.password);
      localStorage.setItem('auth_token', result.access_token);
      ElMessage.success('Registration successful');
      emit('login-success', {
        type: 'email',
        email: form.email,
        isAdmin: result.user.is_admin,
        userId: result.user.id,
      });
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      loading.value = false;
    }
  })();
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-box {
  width: 400px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);

  .logo {
    text-align: center;
    margin-bottom: 30px;

    img {
      height: 60px;
      margin-bottom: 10px;
    }

    h1 {
      margin: 0;
      font-size: 28px;
      color: #303133;
    }

    .subtitle {
      color: #909399;
      margin-top: 5px;
    }
  }
}

.wallet-login {
  text-align: center;
  padding: 20px 0;

  .info-text {
    color: #606266;
    margin-bottom: 20px;
    line-height: 1.5;
  }

  .wallet-btn {
    width: 100%;
    font-weight: bold;
  }
  
  .error-text {
    color: #f56c6c;
    margin-top: 10px;
    font-size: 14px;
  }
}

.full-width {
  width: 100%;
}

.switch-mode {
  text-align: center;
  margin-top: 15px;
  
  .el-button--text {
    color: #409eff;
    font-size: 14px;
  }
}
</style>
