<template>
  <div class="family-verification">
    <div class="header">
      <h2>Family Relationship Verification</h2>
      <p class="subtitle">Ethical Protection: Please declare your relationship and upload verification documents.</p>
    </div>

    <el-alert
      type="info"
      title="Why is verification required?"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    >
      <div class="alert-content">
        <p>To prevent misuse of technology, we require users to:</p>
        <ol>
          <li><strong>Declare Relationship</strong> - Clarify your relationship with the person whose voice is being cloned.</li>
          <li><strong>Upload Documents</strong> - Provide official documents such as household registration or death certificates. Not mandatory, but if not uploaded, the system will not be able to verify your relationship.</li>
          <li><strong>Wait for Review</strong> - Administrators will review your application within 24 hours.</li>
          <li><strong>Use After Approval</strong> - Only verified relationships can proceed to voice cloning.</li>
        </ol>
        <p class="italic-note">
          This is a responsible AI system designed to protect privacy and respect family relationships.
        </p>
      </div>
    </el-alert>

    <!-- Main Action Button -->
    <div style="text-align: center; margin: 30px 0;">
      <el-button type="primary" size="large" @click="showDialog = true">
        Start Verification Process
      </el-button>
    </div>

    <!-- Verification Modal -->
    <el-dialog 
      v-model="showDialog" 
      title="Family Relationship Verification"
      width="600px"
      @close="handleDialogClose"
    >
      <!-- Step 1: Register Relationship -->
      <div v-if="dialogStep === 1">
        <h3 style="margin-bottom: 20px; color: #303133;">Step 1: Declare Your Relationship</h3>
        
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules" 
          label-width="120px"
        >
          <el-form-item label="User ID" prop="user_id">
            <el-input-number 
              v-model="form.user_id" 
              :min="1" 
              disabled
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item label="Your Full Name" prop="guardian_name">
            <el-input v-model="form.guardian_name" placeholder="Enter your real name" />
          </el-form-item>
          
          <el-form-item label="Relative's Name" prop="relative_name">
            <el-input v-model="form.relative_name" placeholder="Name of the deceased relative" />
          </el-form-item>
          
          <el-form-item label="Relationship Type" prop="relationship_type">
            <el-select v-model="form.relationship_type" placeholder="Select relationship" style="width: 100%">
              <el-option label="Parent" value="parent" />
              <el-option label="Child" value="child" />
              <el-option label="Spouse" value="spouse" />
              <el-option label="Sibling" value="sibling" />
              <el-option label="Other" value="other" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: Upload Documents -->
      <div v-else-if="dialogStep === 2">
        <h3 style="margin-bottom: 20px; color: #303133;">Step 2: Upload Verification Documents</h3>
        <p style="color: #606266; margin-bottom: 15px;">📄 Uploading documents for: <strong>{{ currentRelationship?.relative_name }}</strong></p>
        
        <!-- Already uploaded documents -->
        <div v-if="uploadedDocuments.length > 0" style="margin-bottom: 20px;">
          <h4 style="margin-bottom: 10px; color: #606266;">📎 Uploaded Documents ({{ uploadedDocuments.length }})</h4>
          <el-table :data="uploadedDocuments" border style="width: 100%" size="small">
            <el-table-column label="File Name" prop="filename" min-width="120" />
            <el-table-column label="Type" prop="document_type" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="row.document_type === 'household_register' ? 'primary' : row.document_type === 'death_certificate' ? 'warning' : 'info'">
                  {{ row.document_type || 'other' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Size" width="80">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="60" align="center">
              <template #default="{ row }">
                <el-button 
                  type="danger" 
                  :icon="Delete" 
                  size="small" 
                  link
                  @click="handleDeleteDocument(row.id)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- File upload section -->
        <div class="upload-section">
          <div style="margin-bottom: 15px;">
            <el-button type="primary" @click="handleFileSelect">
              Browse and Select Files
            </el-button>
            <el-button @click="clearFileSelection">Clear</el-button>
          </div>
          
          <!-- Selected files -->
          <div v-if="selectedFiles.length > 0" style="margin-bottom: 15px;">
            <h4 style="margin-bottom: 10px; color: #606266;">📋 Selected Files ({{ selectedFiles.length }}):</h4>
            <div v-for="(file, index) in selectedFiles" :key="index" style="margin-bottom: 8px; display: flex; align-items: center; gap: 10px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
              <el-icon><Document /></el-icon>
              <span style="flex: 1; font-size: 13px; color: #303133; overflow: hidden; text-overflow: ellipsis;">{{ file.name }} ({{ formatFileSize(file.size) }})</span>
              <el-select 
                v-model="documentTypes[index]" 
                placeholder="Type" 
                size="small"
                style="width: 140px;"
              >
                <el-option label="Household Register" value="household_register" />
                <el-option label="Death Certificate" value="death_certificate" />
                <el-option label="ID Card" value="id_card" />
                <el-option label="Other" value="other" />
              </el-select>
            </div>
          </div>

          <!-- Hidden file input -->
          <input 
            ref="fileInput"
            type="file" 
            multiple 
            accept=".pdf,.jpg,.png,.jpeg"
            style="display: none;"
            @change="handleFileInputChange"
          />
        </div>
      </div>

      <!-- Dialog Footer -->
      <template #footer>
        <div style="text-align: right;">
          <el-button @click="showDialog = false">Cancel</el-button>
          <el-button v-if="dialogStep === 1" type="primary" @click="submitRelationship" :loading="loading">
            Next Step →
          </el-button>
          <el-button v-else type="primary" @click="handleMultipleUpload" :loading="loading" :disabled="selectedFiles.length === 0">
            Upload Documents
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-row :gutter="20">
      <!-- Relationships List -->
      <el-col :md="16" :sm="24">
        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>Your Relationship Records</span>
            </div>
          </template>
          
          <div v-if="relationships.length === 0" style="text-align: center; padding: 40px;">
            <el-empty description="No relationships yet. Click the button above to start.">
            </el-empty>
          </div>
          
          <div v-else>
            <div v-for="item in relationships" :key="item.id" style="margin-bottom: 15px; padding: 15px; background: #f5f7fa; border-radius: 8px; border-left: 4px solid #409eff;">
              <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                  <p style="margin: 0 0 5px 0; font-weight: 600; color: #303133;">
                    {{ item.relative_name }}
                    <el-tag :type="getStatusType(item.verification_status)" size="small" style="margin-left: 8px;">
                      {{ item.verification_status }}
                    </el-tag>
                  </p>
                  <p style="margin: 0 0 5px 0; font-size: 12px; color: #606266;">
                    Relationship: {{ item.relationship_type }}
                  </p>
                  <p style="margin: 0; font-size: 12px; color: #909399;">
                    Declared by: {{ item.guardian_name }}
                  </p>
                </div>
                <el-button 
                  v-if="item.verification_status === 'pending' || item.verification_status === 'rejected'"
                  type="primary" 
                  size="small"
                  @click="editRelationship(item)"
                >
                  Upload Docs
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- Quick Info -->
      <el-col :md="8" :sm="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Process Info</span>
            </div>
          </template>
          <div class="info-content">
            <el-alert type="info" :closable="false" show-icon>
              <p><strong>Process Steps:</strong></p>
              <ol style="margin: 10px 0; padding-left: 20px;">
                <li>Fill in the form</li>
                <li>Upload documents</li>
                <li>Wait for review</li>
                <li>Use after approval</li>
              </ol>
            </el-alert>
            
            <el-divider />
            
            <div v-if="relationships.length > 0" style="margin-top: 15px;">
              <p style="color: #606266; margin-bottom: 10px;">
                <strong>Status Summary:</strong>
              </p>
              <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <el-tag 
                  v-for="status in ['pending', 'approved', 'rejected']"
                  :key="status"
                  :type="getStatusType(status)"
                  size="small"
                >
                  {{ status }}: {{ relationships.filter(r => r.verification_status === status).length }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { UploadFilled, Refresh, Delete, Document } from '@element-plus/icons-vue';
import { useAppStore } from '@/stores/app';
import { registerRelationship, listRelationships, uploadMultipleVerificationDocuments, getRelationshipDocuments, deleteVerificationDocument } from '@/services/api';
import type { RelationshipData } from '@/types/api';

const emit = defineEmits(['verification-complete']);
const appStore = useAppStore();

// Dialog state
const showDialog = ref(false);
const dialogStep = ref(1);

// Form state
const loading = ref(false);
const relationships = ref<RelationshipData[]>([]);
const currentRelationship = ref<RelationshipData | null>(null);
const uploadedDocuments = ref<any[]>([]);

// File upload state
const selectedFiles = ref<File[]>([]);
const documentTypes = ref<string[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);

const form = reactive({
  user_id: appStore.currentUserId,
  guardian_name: '',
  relative_name: '',
  relationship_type: '',
  purpose: 'voice_cloning',
});

const rules = {
  guardian_name: [{ required: true, message: 'Please enter your name', trigger: 'blur' }],
  relative_name: [{ required: true, message: 'Please enter relative name', trigger: 'blur' }],
  relationship_type: [{ required: true, message: 'Please select relationship', trigger: 'change' }],
};

onMounted(() => {
  loadRelationships();
});

watch(currentRelationship, (newVal) => {
  if (newVal) {
    loadDocuments();
  } else {
    uploadedDocuments.value = [];
  }
});

async function loadRelationships() {
  if (!appStore.currentUserId) return;
  
  try {
    const data = await listRelationships(appStore.currentUserId);
    relationships.value = data;
    appStore.setRelationships(data);
  } catch (error) {
    console.error('Failed to load relationships:', error);
  }
}

async function submitRelationship() {
  loading.value = true;
  try {
    if (!form.guardian_name || !form.relative_name || !form.relationship_type) {
      ElMessage.warning('Please fill in all fields');
      loading.value = false;
      return;
    }

    const data: any = { ...form };
    await registerRelationship(data);
    ElMessage.success('Relationship declared successfully!');
    await loadRelationships();
    
    const found = relationships.value.find(r => r.relative_name === form.relative_name && r.relationship_type === form.relationship_type);
    if (found) currentRelationship.value = found;
    
    // Move to next step
    dialogStep.value = 2;
    
  } catch (error: any) {
    console.error(error);
    const detail = error.response?.data?.detail;
    const errorMessage = Array.isArray(detail)
      ? detail.map((item: any) => item?.msg || 'Validation error').join('; ')
      : detail || 'Submission failed';
    ElMessage.error(errorMessage);
  } finally {
    loading.value = false;
  }
}

function handleFileSelect() {
  fileInput.value?.click();
}

function handleFileInputChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files) {
    const files = Array.from(input.files);
    selectedFiles.value = files;
    
    // Ensure documentTypes array is long enough
    while (documentTypes.value.length < files.length) {
      documentTypes.value.push('other');
    }
  }
}

function clearFileSelection() {
  selectedFiles.value = [];
  documentTypes.value = [];
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function handleMultipleUpload() {
  if (!currentRelationship.value || !currentRelationship.value.id) {
    ElMessage.warning('Please select a relationship first');
    return;
  }
  
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('Please select at least one file');
    return;
  }
  
  loading.value = true;
  try {
    const result = await uploadMultipleVerificationDocuments(
      currentRelationship.value.id,
      appStore.currentUserId,
      selectedFiles.value,
      documentTypes.value
    );
    
    if (result.uploaded_count > 0) {
      ElMessage.success(`${result.message}`);
      clearFileSelection();
      await loadDocuments();
      await loadRelationships();
      showDialog.value = false;
      emit('verification-complete');
    } else {
      ElMessage.error('All files failed to upload');
    }
    
  } catch (error: any) {
    console.error(error);
    ElMessage.error(error.response?.data?.detail || 'Upload failed');
  } finally {
    loading.value = false;
  }
}

async function loadDocuments() {
  if (!currentRelationship.value?.id) return;
  
  try {
    const result = await getRelationshipDocuments(
      currentRelationship.value.id,
      appStore.currentUserId
    );
    uploadedDocuments.value = result.documents;
  } catch (error) {
    console.error('Failed to load documents:', error);
  }
}

async function handleDeleteDocument(documentId: number) {
  if (!currentRelationship.value?.id) return;
  
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this document?',
      'Confirm Deletion',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    );
    
    await deleteVerificationDocument(
      currentRelationship.value.id,
      documentId,
      appStore.currentUserId
    );
    
    ElMessage.success('Document deleted successfully');
    await loadDocuments();
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error(error);
      ElMessage.error('Failed to delete document');
    }
  }
}

function editRelationship(item: RelationshipData) {
  currentRelationship.value = item;
  dialogStep.value = 2;
  showDialog.value = true;
}

function handleDialogClose() {
  dialogStep.value = 1;
  form.guardian_name = '';
  form.relative_name = '';
  form.relationship_type = '';
  clearFileSelection();
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function getStatusType(status?: string) {
  switch (status) {
    case 'approved': return 'success';
    case 'rejected': return 'danger';
    case 'pending': return 'warning';
    default: return 'info';
  }
}
</script>

<style scoped lang="scss">
.family-verification {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 25px;
  h2 {
    margin: 0;
    color: #303133;
    font-size: 24px;
  }
  .subtitle {
    margin: 8px 0 0;
    color: #606266;
    font-size: 14px;
  }
}

.alert-content {
  ol {
    padding-left: 20px;
    margin: 10px 0;
  }
  .italic-note {
    font-style: italic;
    color: #409eff;
    margin-top: 10px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.upload-section {
  h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
  }
  
  h5 {
    margin: 0 0 10px 0;
    font-size: 13px;
    font-weight: 600;
  }
}

.info-content {
  p {
    margin: 0 0 10px;
  }
  
  ol {
    margin: 10px 0;
    padding-left: 20px;
    color: #606266;
    
    li {
      margin-bottom: 5px;
      font-size: 14px;
    }
  }
}
</style>
