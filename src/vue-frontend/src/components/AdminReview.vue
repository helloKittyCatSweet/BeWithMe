<template>
  <div class="admin-review">
    <div class="header">
      <h2>Admin Review</h2>
      <p class="subtitle">Review pending relationship verification requests.</p>
    </div>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Pending Requests</span>
          <el-button size="small" @click="loadPending" :loading="loading">Refresh</el-button>
        </div>
      </template>

      <el-table :data="pendingList" v-loading="loading" empty-text="No pending requests">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="User" width="90" />
        <el-table-column prop="relative_name" label="Relative" min-width="140" />
        <el-table-column prop="relationship_type" label="Type" width="140" />
        <el-table-column prop="purpose" label="Purpose" min-width="220" show-overflow-tooltip />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              type="success"
              :loading="processingId === scope.row.id && actionType === 'approve'"
              @click="handleApprove(scope.row.id)"
            >
              Approve
            </el-button>
            <el-button
              size="small"
              type="danger"
              :loading="processingId === scope.row.id && actionType === 'reject'"
              @click="openRejectDialog(scope.row.id)"
            >
              Reject
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="rejectVisible" title="Reject Request" width="460px">
      <el-form label-position="top">
        <el-form-item label="Reason">
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="Please provide reject reason"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">Cancel</el-button>
        <el-button type="danger" @click="handleReject" :loading="actionType === 'reject' && processingId !== null">
          Confirm Reject
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { getPendingRelationships, verifyRelationshipByAdmin } from '@/services/api';
import type { RelationshipData } from '@/types/api';
import { useAppStore } from '@/stores/app';

const appStore = useAppStore();

const loading = ref(false);
const pendingList = ref<RelationshipData[]>([]);
const processingId = ref<number | null>(null);
const actionType = ref<'approve' | 'reject' | null>(null);

const rejectVisible = ref(false);
const rejectReason = ref('');
const rejectTargetId = ref<number | null>(null);

const reviewerName = 'admin';

onMounted(async () => {
  await loadPending();
});

async function loadPending() {
  loading.value = true;
  try {
    pendingList.value = await getPendingRelationships(appStore.currentUserId);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || 'Failed to load pending list');
  } finally {
    loading.value = false;
  }
}

async function handleApprove(id: number) {
  processingId.value = id;
  actionType.value = 'approve';
  try {
    await verifyRelationshipByAdmin(
      id,
      { action: 'approve', reviewer: reviewerName },
      appStore.currentUserId
    );
    ElMessage.success('Approved successfully');
    await loadPending();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || 'Approve failed');
  } finally {
    processingId.value = null;
    actionType.value = null;
  }
}

function openRejectDialog(id: number) {
  rejectTargetId.value = id;
  rejectReason.value = '';
  rejectVisible.value = true;
}

async function handleReject() {
  if (!rejectTargetId.value) return;
  if (!rejectReason.value.trim()) {
    ElMessage.warning('Reject reason is required');
    return;
  }

  processingId.value = rejectTargetId.value;
  actionType.value = 'reject';
  try {
    await verifyRelationshipByAdmin(
      rejectTargetId.value,
      { action: 'reject', reviewer: reviewerName, notes: rejectReason.value.trim() },
      appStore.currentUserId
    );
    ElMessage.success('Rejected successfully');
    rejectVisible.value = false;
    await loadPending();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || 'Reject failed');
  } finally {
    processingId.value = null;
    actionType.value = null;
  }
}
</script>

<style scoped lang="scss">
.admin-review {
  .header {
    margin-bottom: 18px;
    h2 {
      margin: 0;
      font-size: 24px;
    }
    .subtitle {
      margin-top: 6px;
      color: #909399;
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }
}
</style>
