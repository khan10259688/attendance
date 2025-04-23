<!--    AdminReport.vue -->
<template>
    <div class="admin-report">
      <!-- 查询条件 -->
      <el-card class="filter-card">
        <el-form :inline="true" @submit.prevent="loadData">
          <el-form-item label="Date Range">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
            />
          </el-form-item>
          
          <el-form-item label="Student ID">
            <el-input 
              v-model="filter.student_id" 
              placeholder="Enter Student ID"
              clearable
            />
          </el-form-item>

          <el-form-item label="Student Name">
            <el-input
              v-model="filter.student_name"
              placeholder="Enter Name"
              clearable
            />
          </el-form-item>

          <el-form-item label="Attendance Status">
            <el-select 
              v-model="filter.status" 
              placeholder="All Status"
              clearable
            >
              <el-option label="Normal" value="Normal" />
              <el-option label="Late" value="Late" />
              <el-option label="Early " value="Early " />
              <el-option label="Late + Early " value="Late + Early " />
              <el-option label="Absent" value="Absent" />
              <el-option label="Anomaly" value="Anomaly" />
            </el-select>
          </el-form-item>
  
          <el-form-item>
            <el-button 
              type="primary" 
              icon="el-icon-search"
              @click="loadData"
            >
              Search
            </el-button>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="success" 
              icon="el-icon-download"
              @click="handleExport"
              :disabled="pagination.total === 0"
              :loading="exportLoading"
            >
              Export Excel
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
  
      <!-- 数据表格 -->
      <el-card class="table-card">
        <el-table 
          :data="records" 
          v-loading="loading"
          stripe
          border
          style="width: 100%"
        >
          <el-table-column prop="student_id" label="Student ID" width="120" />
          <el-table-column prop="student_name" label="Name" width="100" />
          <el-table-column prop="date" label="Date" width="120">
            <template #default="{row}">
              {{ formatDate(row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="course_name" label="Course" />
          <el-table-column label="Check-in Time" width="100">
            <template #default="{row}">
              {{ row.check_in || '--' }}
            </template>
          </el-table-column>
          <el-table-column label="Check-out Time" width="100">
            <template #default="{row}">
              {{ row.check_out || '--' }}
            </template>
          </el-table-column>
          <el-table-column label="Status" width="120">
            <template #default="{row}">
              <el-tag :type="statusTagType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
  
        <!-- 分页 -->
        <el-pagination
          class="pagination"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          :current-page="pagination.current_page"
          :page-sizes="[10, 20, 50]"
          :page-size="pagination.per_page"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        />
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import api from '@/utils/api'
  import dayjs from 'dayjs'
  import utc from 'dayjs/plugin/utc'
  import timezone from 'dayjs/plugin/timezone'
  import { ElMessage } from 'element-plus'
  

  // 配置时区插件
  dayjs.extend(utc)
  dayjs.extend(timezone)
  dayjs.tz.setDefault("Asia/Shanghai") // 设置为东八区

  const exportLoading = ref(false)

  // 状态管理
  const loading = ref(false)
  const dateRange = ref([])
  const filter = reactive({
    student_id: ''
  })
  
  // 分页配置
  const pagination = reactive({
    total: 0,
    current_page: 1,
    per_page: 10
  })
  
  // 数据存储
  const records = ref([])
  


  const handleExport = async () => {
  exportLoading.value = true
  try {
    const params = {
      start_date: dateRange.value?.[0] ? dayjs(dateRange.value[0]).format('YYYY-MM-DD') : undefined,
      end_date: dateRange.value?.[1] ? dayjs(dateRange.value[1]).format('YYYY-MM-DD') : undefined,
      student_id: filter.student_id,
      student_name: filter.student_name,
      status: filter.status
    }

    // 过滤空值参数
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== undefined)
    )

    const response = await api.post('/admin/attendance/export', filteredParams)
    
    // 创建隐藏iframe下载
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = response.data.url
    document.body.appendChild(iframe)
    setTimeout(() => document.body.removeChild(iframe), 5000)

  } catch (error) {
    if (error.response?.data?.error === 'No data to export') {
      ElMessage.warning('No records found matching current filters')
    } else {
      ElMessage.error('Export failed. Please check network or contact administrator')
    }
  } finally {
    exportLoading.value = false
  }
}


// 新增日期验证方法
const validatePickerDate = (dateArray) => {
  if (!dateArray || dateArray.length !== 2) return false
  return dateArray.every(date => 
    dayjs(date, 'YYYY-MM-DD', true).isValid()
  )
}
  // 加载数据
  const loadData = async () => {
    const params = {
      page: pagination.current_page,
      per_page: pagination.per_page,
      student_id: filter.student_id,
      student_name: filter.student_name,
      status: filter.status
    }
  try {
    loading.value = true
    // 调试日志：打印原始日期值
    console.log('原始dateRange:', dateRange.value)

    // 严格校验日期参数
    if (dateRange.value?.length) {
      if (!validatePickerDate(dateRange.value)) {
        ElMessage.error('Invalid date format. Please reselect dates')
        dateRange.value = [] // 重置选择器
        return
      }

      params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    }
     // 调试日志：验证参数
     console.log('最终请求参数:', JSON.parse(JSON.stringify(params)))

    const data = await api.get('/admin/attendance', { params })
      console.log('data: ', data)
      records.value = data.data
      pagination.total = data.pagination.total
      pagination.current_page = data.pagination.current_page
      pagination.per_page = data.pagination.per_page
      
    } catch (error) {
        console.error('请求参数:', params) // 调试日志
        ElMessage.error('Failed to load data. Please verify parameters')
    } finally {
      loading.value = false
    }
  }
  
  // 分页处理
  const handleSizeChange = (size) => {
    pagination.per_page = size
    loadData()
  }
  
  const handlePageChange = (page) => {
    pagination.current_page = page
    loadData()
  }

  // 增强日期选择器配置
const handleDateChange = (val) => {
  if (val && val.length === 2) {
    dateRange.value = val.map(date => 
      dayjs(date).format('YYYY-MM-DD')
    )
  } else {
    dateRange.value = []
  }
}
  
  // 工具方法
  const formatDate = (dateStr) => {
    return dayjs(dateStr).format('YYYY-MM-DD')
  }
  
  const statusTagType = (status) => {
    const types = {
      'Normal': 'success',
      'Late': 'warning',
      'Early ': 'warning',
      'Late + Early ': 'danger',
      'Absent': 'info'
    }
    return types[status] || ''
  }
  
  // 初始化加载
  loadData()
  </script>
  
  <style scoped>
  .admin-report {
    padding: 20px;
  }
  
  .filter-card {
    margin-bottom: 20px;
  }
  
  .table-card {
    margin-top: 20px;
  }
  
  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
  
  .el-form--inline .el-form-item {
    margin-right: 20px;
    margin-bottom: 0;
  }
  </style>