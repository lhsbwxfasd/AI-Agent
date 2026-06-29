<template>
  <div class="knowledge-container">
    <el-container>
      <el-aside width="280px" class="sidebar">
        <div class="sidebar-header">
          <h2>知识库管理</h2>
        </div>
        <div class="sidebar-content">
          <el-menu :default-active="'knowledge'">
            <el-menu-item index="knowledge">
              <el-icon><Document /></el-icon>
              <span>知识库</span>
            </el-menu-item>
            <el-menu-item index="chat" @click="goToChat">
              <el-icon><ChatLineRound /></el-icon>
              <span>返回聊天</span>
            </el-menu-item>
            <el-menu-item index="conversations" @click="goToConversations">
              <el-icon><ChatDotRound /></el-icon>
              <span>会话管理</span>
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
          <h2>知识库管理</h2>
          <div class="header-actions">
            <el-button @click="handleAddText" :icon="Edit">添加文本</el-button>
            <el-button @click="handleUpload" :icon="Upload">上传文件</el-button>
            <el-button @click="loadInfo" :icon="Refresh">刷新</el-button>
          </div>
        </div>
        
        <el-card class="info-card">
          <el-descriptions :column="4" border>
            <el-descriptions-item label="文档数量">
              {{ info.count || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="集合名称">
              {{ info.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="向量维度">
              {{ info.dimension || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="元数据字段">
              {{ info.metadata_fields || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card class="add-card">
          <template #header>
            <span>添加文档</span>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="添加文本" name="text">
              <el-form :model="textForm" label-width="100px">
                <el-form-item label="文档内容">
                  <el-input
                    v-model="textForm.content"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入文档内容"
                  />
                </el-form-item>
                <el-form-item label="元数据">
                  <el-input
                    v-model="textForm.metadata"
                    placeholder='JSON格式，如: {"source": "internal", "category": "faq"}'
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleAddTextSubmit" :loading="loading">
                    添加
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="上传文件" name="file">
              <el-upload
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                accept=".pdf,.docx,.txt"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 PDF、DOCX、TXT 格式
                  </div>
                </template>
              </el-upload>
              
              <el-form :model="fileForm" label-width="100px" style="margin-top: 20px">
                <el-form-item label="元数据">
                  <el-input
                    v-model="fileForm.metadata"
                    placeholder='JSON格式，如: {"source": "file", "category": "doc"}'
                  />
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleFileUpload"
                    :loading="loading"
                    :disabled="!selectedFile"
                  >
                    上传
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document,
  ChatLineRound,
  ChatDotRound,
  User,
  Edit,
  Upload,
  Refresh,
  UploadFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { knowledgeApi } from '@/api/knowledge'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const info = ref({})
const activeTab = ref('text')
const selectedFile = ref(null)

const textForm = ref({
  content: '',
  metadata: ''
})

const fileForm = ref({
  metadata: ''
})

async function loadInfo() {
  loading.value = true
  try {
    const response = await knowledgeApi.getInfo()
    info.value = response
  } catch (error) {
    ElMessage.error('加载知识库信息失败')
  } finally {
    loading.value = false
  }
}

async function handleAddText() {
  activeTab.value = 'text'
}

async function handleAddTextSubmit() {
  if (!textForm.value.content.trim()) {
    ElMessage.warning('请输入文档内容')
    return
  }
  
  loading.value = true
  try {
    let metadata = {}
    if (textForm.value.metadata) {
      try {
        metadata = JSON.parse(textForm.value.metadata)
      } catch (e) {
        ElMessage.error('元数据格式错误，请使用JSON格式')
        loading.value = false
        return
      }
    }
    
    await knowledgeApi.addDocument({
      content: textForm.value.content,
      metadata
    })
    
    ElMessage.success('添加成功')
    textForm.value.content = ''
    textForm.value.metadata = ''
    loadInfo()
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    loading.value = false
  }
}

function handleUpload() {
  activeTab.value = 'file'
}

function handleFileChange(file) {
  selectedFile.value = file.raw
}

async function handleFileUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  loading.value = true
  try {
    let metadata = {}
    if (fileForm.value.metadata) {
      try {
        metadata = JSON.parse(fileForm.value.metadata)
      } catch (e) {
        ElMessage.error('元数据格式错误，请使用JSON格式')
        loading.value = false
        return
      }
    }
    
    await knowledgeApi.uploadFile(selectedFile.value, metadata)
    
    ElMessage.success('上传成功')
    selectedFile.value = null
    fileForm.value.metadata = ''
    loadInfo()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    loading.value = false
  }
}

function goToChat() {
  router.push('/')
}

function goToConversations() {
  router.push('/conversations')
}

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadInfo()
})
</script>

<style scoped>
.knowledge-container {
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

.header-actions {
  display: flex;
  gap: 8px;
}

.info-card {
  margin-bottom: 24px;
}

.add-card {
  margin-bottom: 24px;
}

.el-icon--upload {
  font-size: 67px;
  color: #c0c4cc;
  margin: 40px 0 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.el-upload__tip {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
}
</style>
