<template>
  <div class="trust-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="hero-card">
          <div class="hero-content">
            <el-icon class="hero-icon"><Lock /></el-icon>
            <h1>Our Commitment to Your Memories</h1>
            <p class="hero-subtitle">
              At BeWithMe, we understand that your memories are your most precious assets. 
              We leverage cutting-edge technology to ensure they remain yours, forever.
            </p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-row">
      <!-- Blockchain Card -->
      <el-col :xs="24" :sm="12">
        <el-card class="feature-card h-100" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>Blockchain: Your Digital Legacy</span>
            </div>
          </template>
          <div class="card-body">
            <h3>Immutable Ownership</h3>
            <p>
              By anchoring your emotional assets on the <strong>Ethereum Sepolia</strong> blockchain, we guarantee that the ownership of your loved one's digital persona belongs to <strong>you and only you</strong>.
            </p>
            <el-divider />
            <ul class="benefit-list">
              <li><el-icon><Check /></el-icon> <strong>Permanence:</strong> Blockchain records can never be deleted or tampered with by any central authority.</li>
              <li><el-icon><Check /></el-icon> <strong>Decentralization:</strong> Your data is not stored in a single "company vault" but distributed across the globe.</li>
              <li><el-icon><Check /></el-icon> <strong>Verifiable Proof:</strong> You hold the cryptographic key to "awaken" and manage your digital heritage.</li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <!-- IPFS Card -->
      <el-col :xs="24" :sm="12">
        <el-card class="feature-card h-100" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Cloudy /></el-icon>
              <span>IPFS: Distributed Storage</span>
            </div>
          </template>
          <div class="card-body">
            <h3>Content-Addressable Storage</h3>
            <p>
              We use <strong>IPFS (InterPlanetary File System)</strong> to store your raw audio materials and model weights. This ensures that your data is not dependent on our servers.
            </p>
            <el-divider />
            <ul class="benefit-list">
              <li><el-icon><Check /></el-icon> <strong>Zero Data Loss:</strong> Files are stored on a global peer-to-peer network, making them immune to server failures.</li>
              <li><el-icon><Check /></el-icon> <strong>Content Integrity:</strong> Every piece of data is identified by its unique hash, ensuring what you uploaded is exactly what you get back.</li>
              <li><el-icon><Check /></el-icon> <strong>Resilience:</strong> Your memories stay online as long as the network exists, outliving any single application or provider.</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="promise-row">
      <el-col :span="24">
        <el-card class="promise-card">
          <div class="promise-header">
            <el-icon><Service /></el-icon>
            <h2>The BeWithMe Promise</h2>
          </div>
          <el-steps direction="vertical" :active="3">
            <el-step title="Privacy First" description="Your data is encrypted and used only for the purpose of creating your personalized AI agent." />
            <el-step title="You Own the Soul" description="We provide the tools, but you own the cryptographic keys to your family's digital legacy." />
            <el-step title="Technological Immortality" description="By combining AI with Web3, we ensure that your loved ones' voices and personalities can be passed down through generations." />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Lock, Connection, Cloudy, Check, Service } from '@element-plus/icons-vue';
</script>

<style scoped>
.trust-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-card {
  background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
  color: white;
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  border: none;
}

.hero-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.hero-content h1 {
  font-size: 36px;
  margin-bottom: 15px;
}

.hero-subtitle {
  font-size: 18px;
  opacity: 0.9;
  max-width: 800px;
  margin: 0 auto;
}

.feature-row {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #1a237e;
}

.card-header .el-icon {
  margin-right: 10px;
  font-size: 24px;
}

.benefit-list {
  list-style: none;
  padding: 0;
}

.benefit-list li {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  line-height: 1.6;
}

.benefit-list li .el-icon {
  color: #4caf50;
  margin-right: 10px;
  margin-top: 4px;
  font-weight: bold;
}

.h-100 {
  height: 100%;
}

.promise-card {
  padding: 30px;
  background-color: #f5f7fa;
}

.promise-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  color: #1a237e;
}

.promise-header .el-icon {
  font-size: 32px;
  margin-right: 15px;
}

.promise-header h2 {
  margin: 0;
}

:deep(.el-step__title) {
  font-weight: bold;
  color: #1a237e !important;
}

:deep(.el-step__description) {
  font-size: 16px;
  color: #606266 !important;
}
</style>
