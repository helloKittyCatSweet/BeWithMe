<template>
  <div class="user-profile">
    <div class="header">
      <h2>My Data Dashboard</h2>
      <p class="subtitle">Manage your loved ones, voices, and blockchain-verified records.</p>
    </div>

    <!-- Family Members Section -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>👪 My Family Members</span>
              <div class="header-actions">
                <el-button type="primary" size="small" :icon="Plus" @click="goToVerification">Add Parents</el-button>
                <el-button text @click="loadData" :icon="Refresh">Refresh</el-button>
              </div>
            </div>
          </template>
          
          <div v-if="relationships.length === 0" class="empty-list">
            <el-empty description="No family members added yet">
              <el-button type="primary" @click="goToVerification">Add Parents</el-button>
            </el-empty>
          </div>
          
          <div v-else class="family-grid">
            <el-card 
              v-for="member in relationships" 
              :key="member.id" 
              class="member-card"
              :class="getMemberCardClass(member)"
              shadow="hover"
            >
              <div class="member-header">
                <div class="member-info">
                  <h3>{{ member.relative_name }}</h3>
                  <el-tag size="small" :type="getStatusType(member.verification_status)">
                    {{ member.verification_status?.toUpperCase() }}
                  </el-tag>
                </div>
                <div class="member-relationship">
                  <el-tag type="info" size="small">{{ member.relationship_type }}</el-tag>
                </div>
              </div>
              
              <el-divider />
              
              <div class="member-content">
                <div class="info-row">
                  <span class="label">Purpose:</span>
                  <span class="value">{{ member.purpose || 'N/A' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">Created:</span>
                  <span class="value">{{ formatDate(member.created_at) }}</span>
                </div>
                
                <!-- Voice Status -->
                <div class="info-row" style="margin-top: 10px;">
                  <span class="label">Voice:</span>
                  <span class="value">
                    <el-tag v-if="hasVoice(member)" type="success" size="small">Available</el-tag>
                    <el-tag v-else type="info" size="small">Not cloned yet</el-tag>
                  </span>
                </div>
                
                <!-- Blockchain Status -->
                <div class="info-row blockchain-row">
                  <span class="label">⛓️ Blockchain:</span>
                  <span class="value">
                    <el-tag v-if="isOnChain(member)" type="success" size="small" effect="dark">
                      <el-icon><Select /></el-icon> Verified On-Chain
                    </el-tag>
                    <el-tag v-else type="info" size="small">Not on blockchain</el-tag>
                  </span>
                </div>
                
                <!-- Blockchain Details (if on chain) -->
                <div v-if="isOnChain(member)" class="blockchain-details">
                  <el-alert type="success" :closable="false" style="margin-top: 10px;">
                    <template #title>
                      <div style="font-size: 12px;">
                        <strong>Immutable Proof</strong>
                      </div>
                    </template>
                    <div style="font-size: 11px; margin-top: 5px;">
                      <div>IPFS: <code style="font-size: 10px;">{{ member.on_chain_ipfs_hash?.slice(0, 20) }}...</code></div>
                      <div v-if="member.blockchain_tx_hash">
                        Tx: <code style="font-size: 10px;">{{ member.blockchain_tx_hash.slice(0, 15) }}...</code>
                      </div>
                      <div style="margin-top: 5px; color: #67c23a;">
                        ✓ Permanent record that cannot be altered or deleted
                      </div>
                    </div>
                  </el-alert>
                </div>
              </div>
              
              <el-divider />
              
              <div class="member-actions">
                <el-button 
                  v-if="hasVoice(member)" 
                  type="primary" 
                  size="small" 
                  @click="playVoice(member)"
                  :icon="VideoPlay"
                >
                  Play Voice
                </el-button>
                <el-button 
                  v-else-if="member.verification_status === 'approved'"
                  type="success" 
                  size="small"
                  @click="navigateToVoiceClone(member)"
                >
                  Clone Voice
                </el-button>
                <el-button 
                  v-if="isOnChain(member)" 
                  type="warning" 
                  size="small" 
                  @click="viewOnEtherscan(member)"
                  :icon="TopRight"
                >
                  View Proof
                </el-button>
                <el-button size="small" @click="viewDetails(member)" text>Details</el-button>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <!-- Account Settings Section -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :md="12" :sm="24">
        <el-card shadow="hover" class="profile-card">
          <template #header>
            <div class="card-header">
              <span>Account Settings</span>
            </div>
          </template>

          <el-form label-position="top">
            <el-form-item label="User ID">
              <el-input :model-value="appStore.currentUserId" disabled>
                <template #prefix>#</template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="Connected Wallet">
              <div v-if="appStore.walletAddress" class="wallet-display">
                <el-input :model-value="appStore.walletAddress" readonly>
                  <template #prefix><el-icon><Wallet /></el-icon></template>
                  <template #append>
                    <el-button @click="copyToClipboard(appStore.walletAddress)" :icon="CopyDocument" />
                  </template>
                </el-input>
              </div>
              <el-button v-else type="primary" @click="connectWalletAction" class="full-width">
                Connect Wallet
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :md="12" :sm="24">
        <el-card shadow="hover" class="profile-card">
          <template #header>
            <div class="card-header">
              <span>Statistics</span>
            </div>
          </template>
          
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ relationships.length }}</div>
              <div class="stat-label">Family Members</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ approvedCount }}</div>
              <div class="stat-label">Verified</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ voiceCount }}</div>
              <div class="stat-label">Voices Cloned</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ onChainCount }}</div>
              <div class="stat-label">On Blockchain</div>
            </div>
          </div>
          
          <el-divider />
          
          <el-alert 
            v-if="onChainCount > 0"
            type="success" 
            :closable="false" 
            show-icon
            title="Blockchain Protection Active"
          >
            <div style="font-size: 13px;">
              {{ onChainCount }} of your records are permanently stored on blockchain,
              providing immutable proof of ownership and authenticity.
            </div>
          </el-alert>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Wallet, CopyDocument, TopRight, Refresh, VideoPlay, Select, Plus } from '@element-plus/icons-vue';
import { listRelationships, listVoiceProfiles } from '@/services/api';
import { useAppStore } from '@/stores/app';
import { CONTRACT_ADDRESS, connectWallet } from '@/services/contract';

const router = useRouter();
const appStore = useAppStore();
const relationships = ref<any[]>([]);
const voiceProfiles = ref<any[]>([]);

// Computed statistics
const approvedCount = computed(() => 
  Array.isArray(relationships.value) ? relationships.value.filter(r => r.verification_status === 'approved').length : 0
);

const voiceCount = computed(() => 
  Array.isArray(voiceProfiles.value) ? voiceProfiles.value.length : 0
);

const onChainCount = computed(() => {
  if (!Array.isArray(relationships.value) || !Array.isArray(voiceProfiles.value)) return 0;
  return relationships.value.filter(r => isOnChain(r)).length + 
         voiceProfiles.value.filter(v => v.blockchain_minted).length;
});

onMounted(() => {
  if (appStore.currentUserId) {
    loadData();
  }
});

async function loadData() {
  if (!appStore.currentUserId) return;
  
  try {
    const [relData, voiceData] = await Promise.all([
      listRelationships(appStore.currentUserId),
      listVoiceProfiles(appStore.currentUserId)
    ]);
    relationships.value = relData;
    voiceProfiles.value = voiceData;
  } catch (error) {
    console.error('Failed to load user profile data:', error);
    ElMessage.error('Failed to load profile data');
  }
}

function goToVerification() {
  router.push('/verification');
}

function hasVoice(member: any) {
  return voiceProfiles.value.some(v => v.relationship_id === member.id);
}

function getVoiceForMember(member: any) {
  return voiceProfiles.value.find(v => v.relationship_id === member.id);
}

function isOnChain(member: any) {
  const voice = getVoiceForMember(member);
  return member.blockchain_minted || (voice && voice.blockchain_minted);
}

function getMemberCardClass(member: any): string {
  if (member.verification_status === 'approved' && isOnChain(member)) {
    return 'verified-on-chain';
  }
  if (member.verification_status === 'approved') {
    return 'verified';
  }
  return '';
}

async function playVoice(member: any) {
  ElMessage.info(`Playing voice for ${member.relative_name}...`);
  // TODO: Implement voice playback
}

function navigateToVoiceClone(member: any) {
  // Navigate to voice cloning page
  ElMessage.info(`Navigate to voice cloning for ${member.relative_name}`);
  // TODO: Implement navigation with member context
}

function viewOnEtherscan(member: any) {
  if (member.blockchain_tx_hash) {
    const url = `https://sepolia.etherscan.io/tx/${member.blockchain_tx_hash}`;
    window.open(url, '_blank');
  } else {
    ElMessage.warning('No blockchain transaction found');
  }
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  };
  return types[status] || 'info';
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
}

function viewDetails(relationship: any) {
  ElMessage.info(`Viewing details for ${relationship.relative_name}`);
}

async function connectWalletAction() {
  try {
    const { address } = await connectWallet();
    appStore.setWalletAddress(address);
    ElMessage.success('Wallet Connected!');
  } catch (e: any) {
    ElMessage.error(e.message);
  }
}

function copyToClipboard(text: string | null) {
  if (!text) return;
  navigator.clipboard.writeText(text);
  ElMessage.success('Copied to clipboard');
}
</script>

<style scoped lang="scss">
.user-profile {
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
    
    .header-actions {
      display: flex;
      gap: 10px;
      align-items: center;
    }
  }
  
  .empty-list {
    padding: 40px 0;
    text-align: center;
  }
  
  .family-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    
    .member-card {
      transition: all 0.3s ease;
      border: 2px solid transparent;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
      }
      
      &.verified {
        border-color: #67c23a;
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
      }
      
      &.verified-on-chain {
        border-color: #409eff;
        background: linear-gradient(135deg, #ffffff 0%, #ecf5ff 100%);
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
      }
      
      .member-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
        
        .member-info {
          h3 {
            margin: 0 0 5px 0;
            font-size: 18px;
            color: #303133;
          }
        }
      }
      
      .member-content {
        .info-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 14px;
          
          .label {
            color: #909399;
            font-weight: 500;
          }
          
          .value {
            color: #606266;
          }
          
          &.blockchain-row {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #f0f0f0;
          }
        }
        
        .blockchain-details {
          margin-top: 10px;
          
          code {
            background: #f5f7fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            color: #606266;
          }
        }
      }
      
      .member-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
    }
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-bottom: 15px;
    
    .stat-item {
      text-align: center;
      padding: 15px;
      background: #f5f7fa;
      border-radius: 8px;
      
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #409eff;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 13px;
        color: #909399;
      }
    }
  }
  
  .profile-card {
    margin-bottom: 20px;
  }
  
  .wallet-display {
    width: 100%;
  }
  
  .full-width {
    width: 100%;
  }
}
</style>
