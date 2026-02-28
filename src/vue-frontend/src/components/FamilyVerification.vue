<template>
  <div class="family-verification">
    <div class="header">
      <h2>👪 Step 0: Family Relationship Verification</h2>
      <p class="subtitle">🛡️ 伦理保护：请声明您的亲属关系并上传验证文件</p>
    </div>

    <el-alert
      type="info"
      title="为什么需要验证？"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    >
      <p>为防止技术滥用，我们要求用户：</p>
      <ol style="margin: 10px 0; padding-left: 20px;">
        <li><strong>声明亲属关系</strong> - 说明您与被克隆声音者的关系</li>
        <li><strong>上传证明文件</strong> - 提供户口本、死亡证明等官方文件</li>
        <li><strong>等待审核</strong> - 管理员会在 24 小时内审核您的申请</li>
        <li><strong>通过后使用</strong> - 只有审核通过的关系才能进行声音克隆</li>
      </ol>
      <p style="color: #409eff; font-style: italic; margin-top: 10px;">
        这是一个负责任的 AI 系统，旨在保护个人隐私和尊重家庭关系。
      </p>
    </el-alert>

    <el-row :gutter="20">
      <!-- Left Column: Forms -->
      <el-col :md="14" :sm="24">
        <!-- Registration Form -->
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📝 注册亲属关系</span>
            </div>
          </template>
          
          <el-form 
            ref="formRef"
            :model="form" 
            :rules="rules" 
            label-width="120px"
            @submit.prevent="submitRelationship"
          >
            <el-form-item label="用户 ID" prop="user_id">
              <el-input-number 
                v-model="form.user_id" 
                :min="1" 
                disabled
                style="width: 150px;"
              />
              <el-text size="small" type="info" style="margin-left: 10px;">
                实际应用中从登录会话获取
              </el-text>
            </el-form-item>

            <el-form-item label="亲属姓名" prop="relative_name">
              <el-input 
                v-model="form.relative_name" 
                placeholder="例如：张明"
                clearable
              />
            </el-form-item>

            <el-form-item label="关系类型" prop="relationship_type">
              <el-select 
                v-model="form.relationship_type" 
                placeholder="请选择"
                style="width: 100%;"
              >
                <el-option label="父母" value="parent" />
                <el-option label="祖父母/外祖父母" value="grandparent" />
                <el-option label="兄弟姐妹" value="sibling" />
                <el-option label="子女" value="child" />
                <el-option label="配偶" value="spouse" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>

            <el-form-item label="使用目的" prop="purpose">
              <el-input
                v-model="form.purpose"
                type="textarea"
                :rows="3"
                placeholder="例如：怀念逝去的父亲，希望能听到他的声音"
                clearable
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="出生日期">
                  <el-date-picker
                    v-model="form.birth_date"
                    type="date"
                    placeholder="选择日期"
                    style="width: 100%;"
                    :disabled-date="(time) => time.getTime() > Date.now()"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="已故">
                  <el-checkbox v-model="form.is_deceased" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="去世日期" v-if="form.is_deceased">
              <el-date-picker
                v-model="form.death_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%;"
                :disabled-date="(time) => time.getTime() > Date.now()"
              />
            </el-form-item>

            <el-form-item label="其他信息">
              <el-input
                v-model="form.additional_info"
                type="textarea"
                :rows="2"
                placeholder="任何您想补充的信息"
                clearable
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="submitRelationship"
                :loading="submitting"
                :icon="Upload"
              >
                提交关系申请
              </el-button>
              <el-button @click="resetForm" :disabled="submitting">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Document Upload -->
        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📄 上传验证文件</span>
            </div>
          </template>

          <div v-if="pendingRelationships.length > 0">
            <el-form label-width="100px">
              <el-form-item label="选择关系">
                <el-select 
                  v-model="selectedRelationshipId" 
                  placeholder="请选择"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="rel in pendingRelationships"
                    :key="rel.id"
                    :label="`${rel.relative_name} (${getRelationshipLabel(rel.relationship_type)}) - ID: ${rel.id}`"
                    :value="rel.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="验证文件">
                <el-upload
                  ref="uploadRef"
                  class="upload-demo"
                  drag
                  :auto-upload="false"
                  :limit="1"
                  :on-change="handleFileChange"
                  :on-remove="handleFileRemove"
                  accept=".pdf,.jpg,.jpeg,.png"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽文件到这里 或 <em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、JPG、PNG 格式，文件大小不超过 10MB
                    </div>
                  </template>
                </el-upload>
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="uploadDocument"
                  :disabled="!selectedRelationshipId || !uploadFile"
                  :loading="uploading"
                  :icon="Upload"
                >
                  上传文件
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-empty 
            v-else 
            description="没有待上传文件的关系。请先注册关系。" 
          />
        </el-card>
      </el-col>

      <!-- Right Column: List & Info -->
      <el-col :md="10" :sm="24">
        <!-- Relationship List -->
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 我的关系列表</span>
              <el-button 
                size="small" 
                text
                @click="loadRelationships"
                :loading="loadingList"
                :icon="Refresh"
              >
                刷新
              </el-button>
            </div>
          </template>

          <div v-if="appStore.relationships.length > 0" class="relationship-list">
            <div 
              v-for="rel in appStore.relationships" 
              :key="rel.id"
              class="relationship-item"
              :class="`status-${rel.verification_status}`"
            >
              <div class="item-header">
                <span class="status-badge">{{ getStatusEmoji(rel.verification_status!) }}</span>
                <h4>{{ rel.relative_name }}</h4>
              </div>
              <div class="item-content">
                <p><strong>关系:</strong> {{ getRelationshipLabel(rel.relationship_type) }}</p>
                <p><strong>状态:</strong> {{ getStatusLabel(rel.verification_status!) }}</p>
                <p><strong>申请时间:</strong> {{ formatDate(rel.created_at!) }}</p>
                
                <el-tag 
                  v-if="rel.verification_status === 'approved'" 
                  type="success"
                  size="small"
                  style="margin-top: 10px;"
                >
                  ✅ 可用于声音克隆 - ID: {{ rel.id }}
                </el-tag>
                
                <el-alert
                  v-if="rel.verification_status === 'rejected' && rel.reviewer_notes"
                  type="error"
                  :title="`拒绝原因: ${rel.reviewer_notes}`"
                  :closable="false"
                  style="margin-top: 10px;"
                />

                <el-alert
                  v-if="rel.verification_status === 'pending'"
                  type="warning"
                  title="请上传验证文件以完成审核"
                  :closable="false"
                  style="margin-top: 10px;"
                />
              </div>
            </div>
          </div>

          <el-empty v-else description="还没有注册任何关系" />
        </el-card>

        <!-- Admin Review Info -->
        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🔒 管理员审核</span>
            </div>
          </template>
          <div class="info-content">
            <p><strong>审核流程:</strong></p>
            <el-steps direction="vertical" :space="60" :active="1">
              <el-step title="用户提交关系申请" />
              <el-step title="用户上传验证文件" />
              <el-step title="管理员审核文件真实性" />
              <el-step title="审核通过后可进行声音克隆" />
            </el-steps>
            <el-divider />
            <p class="highlight">
              <el-icon><InfoFilled /></el-icon>
              通常在 24 小时内完成审核
            </p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { 
  Upload, 
  UploadFilled, 
  Refresh, 
  InfoFilled 
} from '@element-plus/icons-vue';
import type { FormInstance, FormRules, UploadFile, UploadInstance } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { 
  registerRelationship, 
  listRelationships, 
  uploadVerificationDocument 
} from '@/services/api';
import type { RelationshipData } from '@/types/api';
import { formatDate, getRelationshipLabel, getStatusLabel, getStatusEmoji } from '@/utils/format';

const emit = defineEmits<{
  'verification-complete': []
}>();

const appStore = useAppStore();
const formRef = ref<FormInstance>();
const uploadRef = ref<UploadInstance>();
const submitting = ref(false);
const uploading = ref(false);
const loadingList = ref(false);
const selectedRelationshipId = ref<number>();
const uploadFile = ref<File | null>(null);

interface FormData extends Omit<RelationshipData, 'birth_date' | 'death_date'> {
  birth_date?: Date;
  death_date?: Date;
  is_deceased: boolean;
}

const form = reactive<FormData>({
  user_id: appStore.currentUserId,
  relative_name: '',
  relationship_type: 'parent',
  purpose: '',
  birth_date: undefined,
  death_date: undefined,
  additional_info: '',
  is_deceased: false
});

const rules = reactive<FormRules>({
  relative_name: [
    { required: true, message: '请输入亲属姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度应在 2-50 个字符之间', trigger: 'blur' }
  ],
  relationship_type: [
    { required: true, message: '请选择关系类型', trigger: 'change' }
  ],
  purpose: [
    { required: true, message: '请说明使用目的', trigger: 'blur' },
    { min: 10, max: 500, message: '请输入 10-500 个字符', trigger: 'blur' }
  ]
});

const pendingRelationships = computed(() => 
  appStore.relationships.filter(r => r.verification_status === 'pending')
);

onMounted(async () => {
  await loadRelationships();
});

async function loadRelationships() {
  try {
    loadingList.value = true;
    const data = await listRelationships(appStore.currentUserId);
    appStore.setRelationships(data);
  } catch (error: any) {
    ElMessage.error(`获取关系列表失败: ${error.message}`);
  } finally {
    loadingList.value = false;
  }
}

async function submitRelationship() {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    try {
      submitting.value = true;
      
      const data: RelationshipData = {
        ...form,
        birth_date: form.birth_date?.toISOString().split('T')[0],
        death_date: form.is_deceased && form.death_date 
          ? form.death_date.toISOString().split('T')[0] 
          : undefined
      };
      
      delete (data as any).is_deceased;
      
      const result = await registerRelationship(data);
      
      ElMessage.success({
        message: `✅ 关系申请提交成功！关系 ID: ${result.id}`,
        duration: 5000
      });
      
      appStore.addRelationship(result);
      resetForm();
      
    } catch (error: any) {
      ElMessage.error(`提交失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      submitting.value = false;
    }
  });
}

function resetForm() {
  formRef.value?.resetFields();
  form.is_deceased = false;
  form.birth_date = undefined;
  form.death_date = undefined;
}

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    // Validate file size (10MB)
    if (file.size! > 10 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过 10MB');
      uploadRef.value?.clearFiles();
      return;
    }
    uploadFile.value = file.raw;
  }
}

function handleFileRemove() {
  uploadFile.value = null;
}

async function uploadDocument() {
  if (!selectedRelationshipId.value || !uploadFile.value) {
    ElMessage.warning('请选择关系和文件');
    return;
  }
  
  try {
    uploading.value = true;
    
    await uploadVerificationDocument(
      selectedRelationshipId.value,
      appStore.currentUserId,
      uploadFile.value
    );
    
    ElMessage.success({
      message: '✅ 文件上传成功！等待管理员审核',
      duration: 5000
    });
    
    // Clear upload
    uploadRef.value?.clearFiles();
    uploadFile.value = null;
    selectedRelationshipId.value = undefined;
    
    // Reload relationships
    await loadRelationships();
    
    // If any relationship is approved, emit event
    if (appStore.hasApprovedRelationship) {
      emit('verification-complete');
    }
    
  } catch (error: any) {
    ElMessage.error(`上传失败: ${error.response?.data?.detail || error.message}`);
  } finally {
    uploading.value = false;
  }
}
</script>

<style scoped lang="scss">
.family-verification {
  padding: 20px;

  .header {
    margin-bottom: 20px;
    
    h2 {
      font-size: 28px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #303133;
    }
    
    .subtitle {
      color: #909399;
      font-size: 15px;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .relationship-list {
    max-height: 500px;
    overflow-y: auto;

    .relationship-item {
      padding: 16px;
      margin-bottom: 12px;
      border-radius: 8px;
      border-left: 4px solid;
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }
      
      &.status-pending {
        background: #fff7e6;
        border-left-color: #faad14;
      }
      
      &.status-approved {
        background: #f6ffed;
        border-left-color: #52c41a;
      }
      
      &.status-rejected {
        background: #fff1f0;
        border-left-color: #ff4d4f;
      }
      
      .item-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        
        .status-badge {
          font-size: 22px;
        }
        
        h4 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }
      }
      
      .item-content {
        p {
          margin: 6px 0;
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }

  .info-content {
    p {
      margin: 10px 0;
      line-height: 1.8;
    }

    .highlight {
      margin-top: 15px;
      padding: 10px;
      background: #ecf5ff;
      border-radius: 4px;
      color: #409eff;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  :deep(.el-upload-dragger) {
    padding: 30px;
  }
}
</style>
