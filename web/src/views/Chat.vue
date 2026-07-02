<template>
  <div class="chat-container">
    <el-container class="chat-el-container">
      <!-- Sidebar -->
      <el-aside width="260px" class="sidebar">
        <div class="sidebar-header">
          <el-button class="new-chat-btn" @click="handleNewChat">
            <el-icon><Plus /></el-icon>
            <span>开启新对话</span>
          </el-button>
        </div>
        
        <div class="sidebar-content">
          <div v-for="group in groupedConversations" :key="group.label" class="conversation-group">
            <div class="group-label">{{ group.label }}</div>
            <div
              v-for="conv in group.conversations"
              :key="conv.id"
              :class="['conversation-item', { active: conv.id === chatStore.currentConversationId }]"
              @click="handleSelectConversation(conv.id)"
            >
              <el-icon><ChatDotRound /></el-icon>
              <span class="conversation-title">{{ conv.title }}</span>
            </div>
          </div>
        </div>
        
        <div class="sidebar-footer">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ authStore.username || 'User' }}</span>
              <el-icon class="more-icon"><MoreFilled /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="conversations">会话管理</el-dropdown-item>
                <el-dropdown-item v-if="authStore.isAdmin" command="knowledge">知识库</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-aside>
      
      <!-- Main Content -->
      <el-container class="main-container">
        <!-- Top Navigation -->
        <el-header class="top-header" height="60px">
          <div class="header-left">
            <div class="logo">
              <el-icon class="logo-icon"><Service /></el-icon>
              <span class="logo-text">AI Assistant</span>
            </div>
            <el-icon class="header-icon"><Search /></el-icon>
            <el-icon class="header-icon"><Setting /></el-icon>
          </div>
          <div class="header-center">
            <span class="conversation-title-main">{{ currentConversationTitle }}</span>
            <el-tag size="small" type="info" class="mode-tag">
              <el-icon><Lightning /></el-icon>
              快速模式
            </el-tag>
          </div>
          <div class="header-right">
            <el-icon class="header-icon"><Share /></el-icon>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <div class="chat-messages" ref="messagesContainer">
            <div
              v-for="(message, index) in chatStore.messages"
              :key="index"
              :class="['message', message.role]"
            >
              <div v-if="message.role === 'user'" class="user-message">
                <MessageAttachments 
                  v-if="message.attachments && message.attachments.length > 0"
                  :attachments="message.attachments"
                />
                <div class="message-content">
                  {{ message.content }}
                </div>
              </div>
              <div v-else class="assistant-message">
                <MarkdownRenderer :content="message.content" />
              </div>
            </div>
            
            <div v-if="chatStore.isLoading" class="message assistant">
              <div class="assistant-message">
                <div class="loading-indicator">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>正在思考...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Input -->
          <el-footer class="chat-footer" height="auto">
            <div class="model-selector-wrapper">
              <el-select
                v-model="chatStore.currentModel"
                placeholder="选择模型"
                @change="handleModelChange"
                size="small"
                class="model-selector"
              >
                <el-option
                  v-for="(model, key) in chatStore.models"
                  :key="key"
                  :label="model.name"
                  :value="key"
                />
              </el-select>
            </div>
            <div class="input-container">
              <div class="input-wrapper">
                
                <div class="input-main">
                  <div v-if="attachments.length > 0" class="attachments-preview">
                    <div 
                      v-for="(attachment, index) in attachments" 
                      :key="index"
                      class="attachment-item"
                    >
                      <el-icon><Document /></el-icon>
                      <span class="attachment-name">{{ attachment.filename }}</span>
                      <el-icon class="remove-attachment" @click="removeAttachment(index)">
                        <Close />
                      </el-icon>
                    </div>
                  </div>
                  <el-input
                    v-model="inputMessage"
                    type="textarea"
                    :rows="2"
                    :autosize="{ minRows: 2, maxRows: 6 }"
                    placeholder="给 AI Assistant 发送消息"
                    @keydown.enter.ctrl="handleSend"
                    :disabled="chatStore.isLoading"
                    class="message-input"
                  />
                  
                </div>
                <div class="input-top">
                  <el-button 
                    :class="['feature-btn', { active: deepThinking }]"
                    @click="deepThinking = !deepThinking"
                    size="small"
                  >
                    <el-icon><Cpu /></el-icon>
                    深度思考
                  </el-button>
                  <el-button 
                    :class="['feature-btn', { active: smartSearch }]"
                    @click="smartSearch = !smartSearch"
                    size="small"
                  >
                    <el-icon><Search /></el-icon>
                    智能搜索
                  </el-button>

                  <div class="input-actions">
                    <input 
                      ref="fileInput"
                      type="file"
                      style="display: none"
                      @change="handleFileSelect"
                      accept=".pdf,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp"
                    />
                    <el-button class="action-btn" circle @click="triggerFileUpload">
                      <el-icon><Paperclip /></el-icon>
                    </el-button>
                    <el-button 
                      class="send-btn" 
                      circle
                      @click="handleSend"
                      :disabled="(!inputMessage.trim() && attachments.length === 0) || chatStore.isLoading"
                    >
                      <el-icon><Top /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            
          </el-footer>
        </el-main>
        
        
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  ChatDotRound,
  User,
  Service,
  Loading,
  Search,
  Setting,
  Share,
  Lightning,
  Cpu,
  Paperclip,
  Top,
  MoreFilled,
  Document,
  Close
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { chatApi } from '@/api/chat'
import { conversationApi } from '@/api/conversation'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import MessageAttachments from '@/components/MessageAttachments.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const inputMessage = ref('')
const messagesContainer = ref(null)
const conversations = ref([])
const deepThinking = ref(false)
const smartSearch = ref(false)
const attachments = ref([])
const fileInput = ref(null)

const groupedConversations = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
  const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
  
  const groups = {
    today: { label: '今天', conversations: [] },
    yesterday: { label: '昨天', conversations: [] },
    sevenDays: { label: '7天内', conversations: [] },
    thirtyDays: { label: '30天内', conversations: [] },
    older: { label: '更早', conversations: [] }
  }
  
  conversations.value.forEach(conv => {
    const convDate = new Date(conv.created_at || conv.updated_at || Date.now())
    if (convDate >= today) {
      groups.today.conversations.push(conv)
    } else if (convDate >= yesterday) {
      groups.yesterday.conversations.push(conv)
    } else if (convDate >= sevenDaysAgo) {
      groups.sevenDays.conversations.push(conv)
    } else if (convDate >= thirtyDaysAgo) {
      groups.thirtyDays.conversations.push(conv)
    } else {
      groups.older.conversations.push(conv)
    }
  })
  
  return Object.values(groups).filter(g => g.conversations.length > 0)
})

const currentConversationTitle = computed(() => {
  const current = conversations.value.find(c => c.id === chatStore.currentConversationId)
  return current?.title || '新对话'
})

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    ElMessage.info(`正在上传 ${file.name}...`)
    const response = await chatApi.uploadAttachment(file)
    
    if (response.success) {
      attachments.value.push(response.attachment)
      ElMessage.success(`${file.name} 上传成功`)
    }
  } catch (error) {
    console.error('File upload error:', error)
    ElMessage.error(`文件上传失败: ${error.message}`)
  }
  
  event.target.value = ''
}

function removeAttachment(index) {
  attachments.value.splice(index, 1)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function loadConversations() {
  try {
    const response = await conversationApi.list({ limit: 20 })
    conversations.value = response.conversations
  } catch (error) {
    console.error('Load conversations failed:', error)
  }
}

async function handleNewChat() {
  try {
    const response = await conversationApi.create({
      model: chatStore.currentModel
    })
    chatStore.setConversationId(response.id)
    chatStore.clearMessages()
    await loadConversations()
    ElMessage.success('新对话已创建')
  } catch (error) {
    ElMessage.error('创建对话失败')
  }
}

async function handleSelectConversation(id) {
  try {
    const response = await conversationApi.getMessages(id)
    chatStore.setConversationId(id)
    chatStore.messages = response.messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      attachments: msg.attachments || undefined
    }))
    scrollToBottom()
  } catch (error) {
    ElMessage.error('加载对话失败')
  }
}

function handleModelChange(model) {
  // Update conversation model if exists
  if (chatStore.currentConversationId) {
    conversationApi.update(chatStore.currentConversationId, { model })
  }
}

async function handleSend() {
  if ((!inputMessage.value.trim() && attachments.value.length === 0) || chatStore.isLoading) return
  
  const message = inputMessage.value.trim()
  const currentAttachments = [...attachments.value]
  
  inputMessage.value = ''
  attachments.value = []
  
  // Add user message with attachments
  chatStore.addMessage('user', message)
  if (currentAttachments.length > 0) {
    chatStore.messages[chatStore.messages.length - 1].attachments = currentAttachments
  }
  scrollToBottom()
  
  chatStore.isLoading = true
  
  try {
    let conversationId = chatStore.currentConversationId
    
    // Create conversation if not exists
    if (!conversationId) {
      const newConv = await conversationApi.create({
        model: chatStore.currentModel
      })
      conversationId = newConv.id
      chatStore.setConversationId(conversationId)
      await loadConversations()
    }
    
    let assistantMessage = ''
    
    // Prepare messages with attachments for API
    const messagesWithAttachments = chatStore.messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      attachments: msg.attachments || undefined
    }))
    
    await chatApi.chatStream(
      {
        messages: messagesWithAttachments,
        stream: true,
        model: chatStore.currentModel,
        conversation_id: conversationId,
        use_knowledge: true,
        use_mcp: true
      },
      (data) => {
        // Handle SSE message
        if (data.type === 'start') {
          chatStore.addMessage('assistant', '')
          scrollToBottom()
        } else if (data.type === 'content') {
          assistantMessage += data.content
          chatStore.messages[chatStore.messages.length - 1].content = assistantMessage
          scrollToBottom()
        }
      },
      (error) => {
        console.error('Stream error:', error)
        ElMessage.error('发送消息失败')
      },
      (data) => {
        // Handle stream end
        chatStore.isLoading = false
        if (data.conversation_id) {
          chatStore.setConversationId(data.conversation_id)
        }
        scrollToBottom()
      }
    )
  } catch (error) {
    console.error('Send message failed:', error)
    ElMessage.error('发送消息失败')
    chatStore.isLoading = false
  }
}

function handleCommand(command) {
  if (command === 'conversations') {
    router.push('/conversations')
  } else if (command === 'knowledge') {
    router.push('/knowledge')
  } else if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(async () => {
  try {
    await chatStore.loadModels()
  } catch (error) {
    console.error('Failed to load models:', error)
    ElMessage.warning('加载模型列表失败，使用默认模型')
  }
  
  try {
    await loadConversations()
  } catch (error) {
    console.error('Failed to load conversations:', error)
    ElMessage.warning('加载会话列表失败')
  }
  
  if (conversations.value.length === 0) {
    try {
      await handleNewChat()
    } catch (error) {
      console.error('Failed to create initial conversation:', error)
      ElMessage.error('创建初始对话失败，请刷新页面重试')
    }
  }
})

watch(() => chatStore.messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
.chat-container {
  height: 100%;
  background-color: #F8F9FA;
}
.chat-el-container {
  height: 100%;
}

.sidebar {
  background-color: #F5F6F8;
  border-right: 1px solid #E8EAED;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
}

.new-chat-btn {
  width: 100%;
  background-color: #E6F2FF;
  color: #1A73E8;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background-color: #D4E8FF;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.conversation-group {
  margin-bottom: 24px;
}

.group-label {
  font-size: 12px;
  color: #999;
  padding: 8px 12px;
  font-weight: 500;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #333;
}

.conversation-item:hover {
  background-color: #E8EAED;
}

.conversation-item.active {
  background-color: #E6F2FF;
  color: #1A73E8;
}

.conversation-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  font-size: 14px;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #E8EAED;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.user-info:hover {
  background-color: #E8EAED;
}

.more-icon {
  margin-left: auto;
  font-size: 16px;
  color: #999;
}

.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.top-header {
  background-color: #FFFFFF;
  border-bottom: 1px solid #E8EAED;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
  color: #1A73E8;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1A73E8;
}

.header-icon {
  font-size: 20px;
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
}

.header-icon:hover {
  color: #1A73E8;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.conversation-title-main {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.mode-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: #FFF3E0;
  color: #F57C00;
  border: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  background-color: #fff;
  position: relative;
}

.chat-messages {
  max-width: 900px;
  margin: 0 auto;
  min-height: calc(50% - 100px);
}

.message {
  margin-bottom: 24px;
}

.user-message {
  display: flex;
  justify-content: flex-end;
}

.user-message .message-content {
  background-color: #1A73E8;
  color: white;
  border-radius: 20px 20px 4px 20px;
  padding: 12px 20px;
  max-width: 70%;
  font-size: 15px;
  line-height: 1.6;
}

.assistant-message {
  background-color: transparent;
  padding: 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.chat-footer {
  background-color: #FFFFFF;
  padding: 16px 24px 20px;
  bottom: 0;
  position: sticky;
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
}

.input-wrapper {
  background-color: #FFFFFF;
  border: 1px solid #E8EAED;
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.input-top {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.feature-btn {
  background-color: #E6F2FF;
  color: #1A73E8;
  border: none;
  border-radius: 16px;
  font-size: 13px;
  height: 32px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.feature-btn:hover {
  background-color: #D4E8FF;
}

.feature-btn.active {
  background-color: #1A73E8;
  color: white;
}

.attachments-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #F5F6F8;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #333;
}

.attachment-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-attachment {
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
}

.remove-attachment:hover {
  color: #F44336;
}

.input-main {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  padding: 0;
  background-color: transparent;
  box-shadow: none !important;
}

.message-input :deep(.el-textarea__inner):focus {
  box-shadow: none !important;
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  background-color: transparent;
  border: none;
  color: #999;
  width: 36px;
  height: 36px;
}

.action-btn:hover {
  background-color: #F5F6F8;
  color: #1A73E8;
}

.send-btn {
  background-color: #1A73E8;
  border: none;
  color: white;
  width: 36px;
  height: 36px;
}

.send-btn:hover {
  background-color: #1557B0;
}

.send-btn:disabled {
  background-color: #E8EAED;
  color: #999;
}

.input-notice {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 12px;
}

.model-selector-wrapper {
  max-width: 900px;
  margin: 10px auto;
  display: flex;
}

.model-selector {
  width: 200px;
}

.model-selector :deep(.el-input__wrapper) {
  background-color: #F5F6F8;
  border: none;
  box-shadow: none;
}
</style>
