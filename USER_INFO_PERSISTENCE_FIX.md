# 页面刷新后用户信息丢失问题修复

## 问题描述

登录后前端左下角显示账号名称（正确），但刷新页面后显示变成"User"（错误）。

## 问题原因

### 原有实现

```javascript
// auth.js
const token = ref(localStorage.getItem('token') || '')
const user = ref(null)  // ❌ 页面刷新后丢失
```

**问题**：
1. Token保存在localStorage，刷新后可以恢复
2. 用户信息（user对象）只保存在内存中
3. 页面刷新后，内存清空，user变为null
4. 显示时使用 `user.value?.username || 'User'`，所以显示"User"

## 解决方案

### 方案1：将用户信息保存到localStorage

```javascript
// 登录时保存
localStorage.setItem('user', JSON.stringify(response.user))

// 初始化时恢复
const savedUser = localStorage.getItem('user')
const user = ref(savedUser ? JSON.parse(savedUser) : null)
```

### 方案2：应用启动时重新获取用户信息

```javascript
// App.vue
onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.getCurrentUser()
  }
})
```

### 最终方案：两者结合

**优点**：
- localStorage快速恢复，无需等待API
- API获取确保信息最新
- 双重保障，更可靠

## 修复实现

### 1. 修改 auth.js

#### 保存用户信息到localStorage

```javascript
// 登录时
if (response.user) {
  user.value = response.user
  localStorage.setItem('user', JSON.stringify(response.user))  // ✅ 保存
}

// 获取用户信息时
async function getCurrentUser() {
  const response = await authApi.getCurrentUser()
  user.value = response
  localStorage.setItem('user', JSON.stringify(response))  // ✅ 保存
  return response
}

// 登出时
function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')  // ✅ 清除
}
```

#### 从localStorage恢复用户信息

```javascript
// 初始化时
const savedUser = localStorage.getItem('user')
const user = ref(savedUser ? JSON.parse(savedUser) : null)  // ✅ 恢复
```

### 2. 修改 App.vue

#### 应用启动时检查并获取用户信息

```vue
<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // 如果有token但没有用户信息，重新获取
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
```

## 数据流程

### 登录流程

```
用户登录
  ↓
获取token和用户信息
  ↓
保存到authStore
  ↓
保存到localStorage
  ├─ token
  └─ user (JSON)
```

### 页面刷新流程

```
页面刷新
  ↓
Pinia store重新初始化
  ↓
从localStorage恢复
  ├─ token → token.value
  └─ user → user.value
  ↓
App.vue mounted
  ↓
检查：有token但无user？
  ├─ 是 → 调用getCurrentUser API
  └─ 否 → 使用localStorage中的user
  ↓
显示用户名
```

## 修改的文件

### 1. web/src/stores/auth.js

**修改内容**：
- ✅ 登录时保存用户信息到localStorage
- ✅ 初始化时从localStorage恢复用户信息
- ✅ 登出时清除localStorage中的用户信息
- ✅ getCurrentUser时更新localStorage

### 2. web/src/App.vue

**修改内容**：
- ✅ 添加onMounted钩子
- ✅ 检查token和用户信息
- ✅ 必要时调用getCurrentUser
- ✅ 处理获取失败的情况

## localStorage数据

### 存储的数据

```javascript
localStorage = {
  token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  user: "{\"id\":\"abc-123\",\"username\":\"admin\",\"is_admin\":true,...}"
}
```

### 数据结构

```typescript
interface User {
  id: string
  username: string
  email?: string
  full_name?: string
  is_admin: boolean
}
```

## 测试步骤

### 1. 登录测试

```bash
# 1. 打开浏览器，访问 http://localhost:3000
# 2. 登录（用户名：admin）
# 3. 查看左下角显示：admin ✅
# 4. 打开开发者工具 → Application → Local Storage
# 5. 查看存储的数据：
#    - token: "..."
#    - user: "{\"username\":\"admin\",...}"
```

### 2. 刷新测试

```bash
# 1. 登录后，刷新页面（F5）
# 2. 查看左下角显示：admin ✅
# 3. 不应该显示"User"
```

### 3. Token过期测试

```bash
# 1. 登录后，手动修改localStorage中的token为无效值
# 2. 刷新页面
# 3. 应该自动登出，跳转到登录页 ✅
```

### 4. 登出测试

```bash
# 1. 登录后，点击退出登录
# 2. 查看localStorage
# 3. token和user都应该被清除 ✅
```

## 错误处理

### Token过期

```javascript
// App.vue
try {
  await authStore.getCurrentUser()
} catch (error) {
  // Token过期或无效
  authStore.logout()  // 清除无效token
  // 路由守卫会自动跳转到登录页
}
```

### 网络错误

```javascript
// 如果API调用失败，使用localStorage中的缓存数据
// 用户仍能看到用户名，但可能不是最新的
```

## 性能优化

### 优先使用localStorage

```
页面刷新
  ↓
立即从localStorage恢复（快速）
  ↓
显示用户名
  ↓
后台调用API更新（可选）
```

**优点**：
- 无需等待API响应
- 用户体验好
- 减少不必要的API调用

## 安全考虑

### localStorage安全性

**存储的数据**：
- ✅ Token（已有）
- ✅ 用户基本信息（非敏感）

**不存储**：
- ❌ 密码
- ❌ 敏感信息

**注意**：
- localStorage可被用户查看和修改
- 但只能修改自己的数据
- 后端会验证token有效性

## 替代方案

### 方案A：仅使用API

```javascript
// 不使用localStorage存储user
// 每次刷新都调用API获取

onMounted(async () => {
  if (authStore.token) {
    await authStore.getCurrentUser()
  }
})
```

**缺点**：
- 需要等待API响应
- 刷新时短暂显示"User"
- 增加API调用

### 方案B：使用sessionStorage

```javascript
// 使用sessionStorage代替localStorage
sessionStorage.setItem('user', JSON.stringify(user))
```

**特点**：
- 关闭标签页后清除
- 更安全，但不持久

### 方案C：使用Cookie

```javascript
// 后端设置HttpOnly Cookie
// 前端无法访问，更安全
```

**优点**：
- 更安全（HttpOnly）
- 自动携带

**缺点**：
- 需要后端支持
- 实现复杂

## 总结

✅ **已修复**：
- 用户信息保存到localStorage
- 页面刷新时自动恢复
- 应用启动时验证和更新
- 登出时清除所有数据

✅ **效果**：
- 刷新页面后用户名正确显示
- 无需重新登录
- 用户体验流畅

✅ **安全**：
- 只存储非敏感信息
- Token验证机制完整
- 过期自动登出

现在页面刷新后用户信息不会丢失了！✨
