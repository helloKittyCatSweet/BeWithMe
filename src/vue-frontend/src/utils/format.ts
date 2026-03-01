export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function getRelationshipLabel(type: string): string {
  const map: Record<string, string> = {
    parent: 'Parent',
    grandparent: 'Grandparent',
    sibling: 'Sibling',
    child: 'Child',
    spouse: 'Spouse',
    other: 'Other'
  };
  return map[type] || type;
}

export function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected'
  };
  return map[status] || status;
}

export function getStatusEmoji(status: string): string {
  const map: Record<string, string> = {
    pending: '⏳',
    approved: '✅',
    rejected: '❌'
  };
  return map[status] || '❓';
}
