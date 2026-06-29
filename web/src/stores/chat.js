import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const models = ref([])
  const currentModel = ref('deepseek-chat')
  const currentConversationId = ref(null)
  const messages = ref([])
  const isLoading = ref(false)

  async function loadModels() {
    try {
      const response = await chatApi.getModels()
      models.value = response.models
      currentModel.value = response.default || 'deepseek-chat'
    } catch (error) {
      console.error('Load models failed:', error)
    }
  }

  function addMessage(role, content) {
    messages.value.push({ role, content })
  }

  function clearMessages() {
    messages.value = []
  }

  function setConversationId(id) {
    currentConversationId.value = id
  }

  return {
    models,
    currentModel,
    currentConversationId,
    messages,
    isLoading,
    loadModels,
    addMessage,
    clearMessages,
    setConversationId
  }
})
