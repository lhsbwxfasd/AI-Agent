<template>
  <div class="conversations-container">
    <el-container>
      <el-aside width="280px" class="sidebar">
        <div class="sidebar-header">
          <h2>会话管理</h2>
        </div>
        <div class="sidebar-content">
          <el-menu :default-active="'conversations'">
            <el-menu-item index="conversations">
              <el-icon><ChatDotRound /></el-icon>
              <span>会话列表</span>
            </el-menu-item>
            <el-menu-item index="chat" @click="goToChat">
              <el-icon><ChatLineRound /></el-icon>
              <span>返回聊天</span>
            </el-menu-item>
            <el-menu-item index="knowledge" @click="goToKnowledge">
              <el-icon><Document /></el-icon>
              <span>知识库</span>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="sidebar-footer">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-icon><User /></el-icon>
              <span>Admin</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-aside>
      
      <el-main class="main-content">
        <div class="content-header">
          <h2>会话列表</h2>
          <el-button type="primary" @click="handleNewConversation" :icon="Plus">
            新建会话
          </el-button>
        </div>
        
        <el-table :data="conversations" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="model" label="模型" width="150" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="handleView(row)"
                :icon="View"
              >
                查看
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDelete(row)"
                :icon="Delete"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-if="total > 0"
          class="pagination"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </el-main>
    </el-container>
    
    <!-- View Dialog -->
    <el-dialog
      v-model="viewDialogVisible"
      title="会话详情"
      width="800px"
    >
      <div v-if="currentConversation">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题">
            {{ currentConversation.title }}
          </el-descriptions-item>
          <el-descriptions-item label="模型">
            {{ currentConversation.model }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentConversation.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentConversation.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="摘要" :span="2">
            {{ currentConversation.summary || '无' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="messages-section">
          <h3>消息历史</h3>
          <div class="messages-list">
            <div
              v-for="(msg, index) in currentConversation.messages"
              :key="index"
              :class="['message-item', msg.role]"
            >
              <div class="message-role">{{ msg.role === 'user' ? '用户' : '助手' }}</div>
              <div class="message-content">{{ msg.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  ChatLineRound,
  Document,
  User,
  Plus,
  View,
  Delete
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { conversationApi } from '@/api/conversation'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const conversations = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const viewDialogVisible = ref(false)
const currentConversation = ref(null)

async function loadConversations() {
  loading.value = true
  try {
    const response = await conversationApi.list({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    })
    conversations.value = response.conversations
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载会话列表失败')
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  currentPage.value = page
  loadConversations()
}

async function handleNewConversation() {
  try {
    await conversationApi.create({ model: 'gpt-4' })
    ElMessage.success('会话创建成功')
    loadConversations()
  } catch (error) {
    ElMessage.error('创建会话失败')
  }
}

async function handleView(row) {
  try {
    const response = await conversationApi.getMessages(row.id)
    currentConversation.value = {
      ...row,
      messages: response.messages
    }
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载会话详情失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await conversationApi.delete(row.id)
    ElMessage.success('删除成功')
    loadConversations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

function goToChat() {
  router.push('/')
}

function goToKnowledge() {
  router.push('/knowledge')
}

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
.conversations-container {
  height: 100vh;
}

.sidebar {
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-header h2 {
  margin: 0;
  color: #303133;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}

.user-info:hover {
  background-color: #e0e0e0;
}

.main-content {
  padding: 24px;
  background-color: #fafafa;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h2 {
  margin: 0;
  color: #303133;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.messages-section {
  margin-top: 24px;
}

.messages-section h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

.messages-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 16px;
  background-color: #fafafa;
}

.message-item {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 4px;
  background-color: white;
}

.message-item.user {
  border-left: 3px solid #409eff;
}

.message-item.assistant {
  border-left: 3px solid #67c23a;
}

.message-role {
  font-weight: bold;
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.message-content {
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
