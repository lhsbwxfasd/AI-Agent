<template>
  <div class="message-attachments">
    <div 
      v-for="(attachment, index) in attachments" 
      :key="index"
      class="attachment-item"
    >
      <div class="attachment-icon">
        <el-icon v-if="isImage(attachment.content_type)">
          <Picture />
        </el-icon>
        <el-icon v-else-if="isPDF(attachment.content_type)">
          <Document />
        </el-icon>
        <el-icon v-else>
          <Folder />
        </el-icon>
      </div>
      <div class="attachment-info">
        <div class="attachment-name">{{ attachment.filename }}</div>
        <div class="attachment-size">{{ formatSize(attachment.size) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Picture, Document, Folder } from '@element-plus/icons-vue'

const props = defineProps({
  attachments: {
    type: Array,
    default: () => []
  }
})

function isImage(contentType) {
  return contentType?.startsWith('image/')
}

function isPDF(contentType) {
  return contentType === 'application/pdf'
}

function formatSize(bytes) {
  if (bytes < 1024) {
    return bytes + ' B'
  } else if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(1) + ' KB'
  } else {
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }
}
</script>

<style scoped>
.message-attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  max-width: 200px;
}

.attachment-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  flex-shrink: 0;
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.attachment-size {
  font-size: 11px;
  opacity: 0.8;
  margin-top: 2px;
}
</style>
