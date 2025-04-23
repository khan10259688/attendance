<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { ElNotification, type FormInstance } from 'element-plus'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loginForm = ref<FormInstance>()
const authStore = useAuthStore()
const form = ref({
  username: '',
  password: ''
})

const validateRules = {
  username: [{ required: true, message: 'Please enter email', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const loading = ref(false)

const handleLogin = async () => {
  try {
    loading.value = true
    
    // 表单验证
    await loginForm.value?.validate()
    
    const result = await authStore.login(form.value)
    
    if (result?.success) {
      ElNotification.success({
        title: 'Login Successful',
        message: `Welcome back, ${authStore.user?.profile.name}!`,
        duration: 3000
      })
      
      // 根据角色跳转
      const redirectPath = result.redirect || (authStore.user?.role ? '/report' : '/attendance')
      router.push(redirectPath)
    }
  } catch (error: any) {
    ElNotification.error({
      title: 'Login Failed',
      message: error.message || 'System error, please try again later',
      duration: 5000
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="branding">
        <h1 class="campus-name">HONG KONG BAPTIST UNIVERSITY</h1>
        <h2 class="system-name">Attendance Management System</h2>
      </div>
      
      <el-form 
        ref="loginForm"
        :model="form"
        :rules="validateRules"
        @submit.prevent="handleLogin"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model.trim="form.username"
            placeholder="Student/Staff Email"
            clearable
            :disabled="loading"
          >
            <template #prefix>
              <el-icon><user /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model.trim="form.password"
            type="password"
            placeholder="Password"
            show-password
            clearable
            :disabled="loading"
          >
            <template #prefix>
              <el-icon><lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button
          native-type="submit"
          type="primary"
          :loading="loading"
          class="auth-button"
        >
          {{ loading ? 'Logging in...' : 'Login Now' }}
        </el-button>
      </el-form>

      <div class="footer">
        <p>© 2025 Data Science</p>
      </div>
  </div>
  </div>
</template>
<style scoped>
.auth-container {
  display: grid;
  place-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  padding: 48px 40px;
  border-radius: 24px;
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.08),
    inset 0 0 0 1px rgba(255, 255, 255, 0.3);
  /* backdrop-filter: blur(12px); */
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.auth-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 
    0 16px 40px rgba(0, 0, 0, 0.12),
    inset 0 0 0 1px rgba(255, 255, 255, 0.4);
}

.branding {
  text-align: center;
  margin-bottom: 40px;
}

.campus-name {
  font-size: 13px;
  color: #6c757d;
  letter-spacing: 1.2px;
  margin-bottom: 8px;
  font-weight: 500;
}

.system-name {
  font-size: 24px;
  color: #212529;
  margin: 0;
  font-weight: 600;
  position: relative;
  padding-bottom: 12px;
}

.system-name::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48px;
  height: 2px;
  background: #409EFF;
  border-radius: 1px;
}

.login-form {
  margin: 32px 0;
}

:deep(.el-form-item) {
  margin-bottom: 32px;
}

:deep(.el-input) {
  --el-input-focus-border-color: rgba(64, 158, 255, 0.6);
  --el-input-hover-border-color: rgba(64, 158, 255, 0.3);
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(241, 243, 245, 0.6);
  box-shadow: none;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(241, 243, 245, 0.9);
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.2);
}

:deep(.el-input__prefix) {
  margin-right: 12px;
}

:deep(.el-icon) {
  color: rgba(64, 158, 255, 0.8);
  font-size: 18px;
}

.auth-button {
  width: 100%;
  height: 48px;
  font-size: 15px;
  letter-spacing: 0.5px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.9), rgba(51, 117, 185, 0.9));
  border: none;
  color: white;
  transition: 
    transform 0.3s ease,
    box-shadow 0.3s ease,
    opacity 0.3s ease;
}

.auth-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.25);
  opacity: 0.95;
}

.auth-button:active {
  transform: translateY(0);
  opacity: 1;
}

.footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #868e96;
  letter-spacing: 0.5px;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 40px 24px;
    margin: 0 16px;
    border-radius: 20px;
  }

  :deep(.el-input__wrapper) {
    padding: 6px 14px;
  }

  .auth-button {
    height: 44px;
    font-size: 14px;
  }
}
</style>