<template>
  <div class="chat-container">
    <el-container>
      <!-- Sidebar -->
      <el-aside width="280px" class="sidebar">
        <div class="sidebar-header">
          <el-button type="primary" @click="handleNewChat" :icon="Plus">
            新对话
          </el-button>
        </div>
        
        <div class="sidebar-content">
          <el-menu
            :default-active="currentConversationId"
            @select="handleSelectConversation"
          >
            <el-menu-item
              v-for="conv in conversations"
              :key="conv.id"
              :index="conv.id"
            >
              <el-icon><ChatDotRound /></el-icon>
              <span class="conversation-title">{{ conv.title }}</span>
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
                <el-dropdown-item command="conversations">会话管理</el-dropdown-item>
                <el-dropdown-item command="knowledge">知识库</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-aside>
      
      <!-- Main Content -->
      <el-main class="main-content">
        <div class="chat-header">
          <div class="model-selector">
            <el-select
              v-model="chatStore.currentModel"
              placeholder="选择模型"
              @change="handleModelChange"
            >
              <el-option
                v-for="(model, key) in chatStore.models"
                :key="key"
                :label="model.name"
                :value="key"
              />
            </el-select>
          </div>
        </div>
        
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="(message, index) in chatStore.messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-avatar">
              <el-icon v-if="message.role === 'user'"><User /></el-icon>
              <el-icon v-else><Service /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
            </div>
          </div>
          
          <div v-if="chatStore.isLoading" class="message assistant">
            <div class="message-avatar">
              <el-icon><Service /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在思考...</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            @keydown.enter.ctrl="handleSend"
            :disabled="chatStore.isLoading"
          />
          <div class="input-actions">
            <el-button
              type="primary"
              @click="handleSend"
              :loading="chatStore.isLoading"
              :disabled="!inputMessage.trim()"
            >
              发送 (Ctrl+Enter)
            </el-button>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  ChatDotRound,
  User,
  Service,
  Loading
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { chatApi } from '@/api/chat'
import { conversationApi } from '@/api/conversation'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const inputMessage = ref('')
const messagesContainer = ref(null)
const conversations = ref([])

// Configure marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  }
})

function formatMessage(content) {
  return marked(content || '')
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
      content: msg.content
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
  if (!inputMessage.value.trim() || chatStore.isLoading) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  // Add user message
  chatStore.addMessage('user', message)
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
    
    await chatApi.chatStream(
      {
        messages: chatStore.messages,
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

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.conversation-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  display: flex;
  flex-direction: column;
  padding: 0;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-selector {
  width: 200px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #fafafa;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background-color: #67c23a;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  background-color: #409eff;
  color: white;
  border-radius: 12px 12px 0 12px;
  padding: 12px 16px;
}

.message.assistant .message-content {
  background-color: white;
  border-radius: 12px 12px 12px 0;
  padding: 12px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-text :deep(pre) {
  background-color: #2d2d2d;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  font-family: 'Courier New', monospace;
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 3px;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.message-text :deep(p) {
  margin: 8px 0;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background-color: white;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
