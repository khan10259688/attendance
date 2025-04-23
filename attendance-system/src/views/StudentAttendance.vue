<!-- StudentAttendance.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'


const authStore = useAuthStore()

const statusMap = {
    'Normal': '✅ Normal',
    'Late': '⚠️ Late',
    'Early ': '⚠️ Early ',
    'Late + Early ': '⛔ Late + Early ',
    'Absent': '❌ Absent',
    'Anomaly': '⚠️ Anomaly'
}

const currentStatus = ref('')  // 新增状态码字段

// 考勤状态
const attendanceStatus = ref('')
const checkInTime = ref(null)
const checkOutTime = ref(null)
const courseEndTime = ref(null)

// 状态计算属性
const canCheckIn = computed(() => {
  return !checkInTime.value && !isCourseEnded.value
})

const canCheckOut = computed(() => {
  return checkInTime.value && !checkOutTime.value && !isCourseEnded.value
})

const isCourseEnded = computed(() => {
  // 需要结合当前日期
  const today = new Date().toISOString().split('T')[0]
  const courseEnd = new Date(`${today}T${courseEndTime.value}`)
  console.log('current: ', new Date)
  console.log('courseEnd:  ', courseEnd)
  return new Date() > courseEnd
})

// 获取当日考勤状态
const fetchAttendance = async () => {
  try {
    const response = await api.get(`/attendance/today?student_id=${authStore.user.profile.student_id}`)
    const data = response
    console.log("--------data: ", data.attendance)
    checkInTime.value = data.attendance.check_in
    checkOutTime.value = data.attendance.check_out
    courseEndTime.value = data.attendance.course_end_time

    updateStatusDisplay()
  } catch (error) {
    ElMessage.error('获取考勤状态失败')
  }
}

// 更新状态显示
const updateStatusDisplay = () => {
  if (isCourseEnded.value) {
    attendanceStatus.value = checkInTime.value ? 'Attendance Completed' : 'No check-in after course ended'
    return
  }
  
  if (checkOutTime.value) {
    attendanceStatus.value = `Check-out: ${checkOutTime.value}`
  } else if (checkInTime.value) {
    attendanceStatus.value = `Checked in at ${checkInTime.value}(Pending check-out)`
  } else {
    attendanceStatus.value = 'Pending Check-in'
  }
}

// 签到逻辑修正
const handleCheckIn = async () => {
  try {
    const response = await api.post('/attendance/check-in', {
      student_id: authStore.user?.profile.student_id,  // 改为下划线命名
      course_id: authStore.user?.profile.course.course_id      // 添加课程ID字段
    })
    console.log("=========rsp: ", response)
    checkInTime.value = response.time
    updateStatusDisplay()
    // console.log("=========rsp: ", response)
    // 添加迟到提示
    if (response.status === 'Late') {
      ElMessageBox.alert('Late arrival recorded. Please maintain attendance discipline!', 'Late Arrival Notice', {
        confirmButtonText: 'Acknowledge',
        type: 'warning',
        callback: () => {
          ElMessage.success('Check-in recorded (Late notation added)')
        }
      })
    } else {
      ElMessage.success('Check-in successful')
    }
  } catch (error) {
    ElMessage.error('Check-in failed: ' + (error.response?.data?.error || 'System error'))
  }
}

// 签退逻辑修正
const handleCheckOut = async () => {
  try {
    const response = await api.post('/attendance/check-out', {
      student_id: authStore.user?.profile.student_id
    })
    
    console.log('-------time: ', response)
    checkOutTime.value = response.check_out_time
    updateStatusDisplay()
    
    // 添加早退提示
    if (response.status.includes('Early')) {
      ElMessageBox.alert('Early departure detected. Course participation incomplete!', 'Early  Notice', {
        confirmButtonText: 'Confirm',
        type: 'warning',
        confirmButtonClass: 'warning-confirm',
        callback: () => {
          ElMessage.success('Check-out recorded (Early departure noted)')
        }
      })
    } else {
      ElMessage.success('Check-out successful')
    }
  } catch (error) {
    ElMessage.error('Check-out failed: ' + (error.response?.data?.error || 'System error'))
  }
}

onMounted(() => {
  fetchAttendance()
})
</script>

<template>
  <div class="attendance-container">
    
     <!-- 签到卡片 -->
     <div class="check-card check-in" 
         :class="{ active: checkInTime, disabled: !canCheckIn }"
         @click="handleCheckIn">
      <div class="card-content">
        <div class="icon-wrapper">
          <i class="iconfont icon-fingerprint"></i>
        </div>
        <div class="text-content">
          <h3>{{ checkInTime ? 'Checked In' : 'Check-in' }}</h3>
          <div class="status-info">
            <p class="timestamp" v-if="checkInTime">{{ checkInTime }}</p>
            <p class="instruction" v-else>Click to start attendance tracking</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 签退卡片 -->
    <div class="check-card check-out"
         :class="{ active: checkOutTime, disabled: !canCheckOut }"
         @click="handleCheckOut">
      <div class="card-content">
        <div class="icon-wrapper">
          <i class="iconfont icon-door"></i>
        </div>
        <div class="text-content">
          <h3>{{ checkOutTime ? 'Checked Out' : 'Check-out' }}</h3>
          <div class="status-info">
            <p class="timestamp" v-if="checkOutTime">{{ checkOutTime }}</p>
            <p class="instruction" v-else>Complete your attendance session</p>
          </div>
        </div>
      </div>
    </div>
</div>
</template>
<style scoped>
.attendance-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 16px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.05);
}

.check-card {
  --base-padding: 2.5rem;
  --icon-size: 64px;
  --transition-speed: 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  position: relative;
  min-height: 180px;
  padding: var(--base-padding);
  background: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  transition: var(--transition-speed);
  border: 1px solid transparent;
  
  &:hover:not(.disabled) {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  &.active {
    border-color: rgba(0, 0, 0, 0.08);
    background: linear-gradient(
      135deg,
      var(--active-light) 20%,
      var(--active-dark) 120%
    );
    
    .icon-wrapper {
      background: rgba(255, 255, 255, 0.15);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    h3 {
      color: var(--active-text);
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
  }

  &.disabled {
    opacity: 0.65;
    cursor: not-allowed;
    background: rgba(255, 255, 255, 0.6);
    
    .icon-wrapper {
      filter: grayscale(0.8);
    }
  }
}

.check-in {
  --active-light: #e3f2fd;
  --active-dark: #4dabf5;
  --active-text: #1a73e8;

  .iconfont {
    color: #1a73e8;
  }
}

.check-out {
  --active-light: #fff3e0;
  --active-dark: #ffb74d;
  --active-text: #f57c00;

  .iconfont {
    color: #f57c00;
  }
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 2rem;
}

.icon-wrapper {
  width: var(--icon-size);
  height: var(--icon-size);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-speed);
  
  .iconfont {
    font-size: 32px;
    transition: color var(--transition-speed);
  }
}

.text-content {
  flex: 1;
  
  h3 {
    margin: 0 0 1rem;
    font-size: 1.8rem;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.85);
    transition: color var(--transition-speed);
  }
}

.status-info {
  .timestamp {
    font-size: 1.2rem;
    color: rgba(0, 0, 0, 0.7);
    font-weight: 500;
    letter-spacing: 0.5px;
  }
  
  .instruction {
    font-size: 1.1rem;
    color: rgba(0, 0, 0, 0.6);
    line-height: 1.4;
    max-width: 240px;
  }
}
</style>