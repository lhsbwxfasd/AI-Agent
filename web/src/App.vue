<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // 如果有token但没有用户信息，重新获取用户信息
  if (authStore.token && !authStore.user) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('Failed to get user info:', error)
      // 如果获取失败（token过期等），清除token
      authStore.logout()
    }
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>
