<!-- src/layouts/MainLayout.vue -->
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem } from 'element-plus'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const authStore = useAuthStore()
const activeMenu = ref(router.currentRoute.value.path)

router.afterEach((to) => {
  activeMenu.value = to.path
})
</script>

<template>
  <el-container class="main-container">
    <el-header class="system-header">
      <div class="header-left">
        <h1>Attendance Management System</h1>
        <div v-if="authStore.user?.role === 'student'" class="course-info">
          Current Course: {{ authStore.user?.profile?.course?.course_id }}
        </div>
      </div>
      <div class="user-info">
        <span class="username">Welcome: {{ authStore.user?.profile?.name }}</span>
        <span 
          class="logout-btn"
          @click="authStore.logout"
        >
          Logout
        </span>
      </div>
    </el-header>

    <el-container>
      <el-aside width="200px">
        <el-menu 
          :default-active="activeMenu"
          router
          class="side-menu"
        >
          <el-menu-item index="/attendance"
          v-if="authStore.user?.role === 'student'">
            <template #title>📅 Attendance Check-in</template>
          </el-menu-item>

          <el-menu-item index="/search"
          v-if="authStore.user?.role === 'student'">
            <template #title>📅 Attendance Search</template>
          </el-menu-item>

          <el-menu-item 
            index="/report" 
            v-if="authStore.user?.role === 'admin'"
          >
            <template #title>📊 Analytics Dashboard</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <NotificationPopup />
  </el-container>
</template>


<style scoped>
.main-container {
  height: 100vh;
}

.system-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #409EFF;
  color: white;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: baseline;
    gap: 20px;
    
    h1 {
      margin: 0;
      font-size: 24px;
    }
    
    .course-info {
      font-size: 16px;
      opacity: 0.9;
    }
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 16px;

    .username {
    font-size: 16px;
    opacity: 0.9;
  }

  .logout-btn {
    font-size: 16px;
    cursor: pointer;
    margin-left: 15px;
    padding: 5px 12px;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-weight: 500;
    position: relative;
    overflow: hidden;
    
    /* 基础样式 */
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.1);
    
    /* 悬停效果 */
    &:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.2);
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      
      &::after {
        transform: translateX(0);
      }
    }

    /* 点击效果 */
    &:active {
      transform: translateY(1px);
      box-shadow: none;
    }

    /* 滑动装饰线 */
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 1px;
      background: #fff;
      transform: translateX(-100%);
      transition: transform 0.3s ease;
    }
  }
  }
}

.side-menu {
  height: 100%;
  
  :deep(.el-menu-item) {
    font-size: 16px;
    height: 56px;
    line-height: 56px;
    
    &.is-active {
      background-color: #ecf5ff;
    }
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>