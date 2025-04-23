
<template>
    <div class="student-report">
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
  
          <el-form-item label="Status">
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
          <el-table-column prop="date" label="Date" width="120" />
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
  import { useAuthStore } from '@/stores/auth'
  
  const authStore = useAuthStore()
  const dateRange = ref([])
  const filter = reactive({
    status: ''
  })
  const pagination = reactive({
    total: 0,
    current_page: 1,
    per_page: 10
  })
  const records = ref([])
  const loading = ref(false)
  
  const loadData = async () => {
    try {
      loading.value = true
      const params = {
        page: pagination.current_page,
        per_page: pagination.per_page,
        status: filter.status,
        start_date: dateRange.value?.[0],
        end_date: dateRange.value?.[1],
        student_id: authStore.user?.profile?.student_id
      }
  
      const response = await api.get('/attendance/search', { params })
      records.value = response.data
      console.log('---res--', records.value)
      pagination.total = response.pagination.total
      pagination.current_page = response.pagination.current_page
      pagination.per_page = response.pagination.per_page
    } finally {
      loading.value = false
    }
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

  // 分页处理方法同AdminReport
  const handleSizeChange = (size) => {
    pagination.per_page = size
    loadData()
  }
  
  const handlePageChange = (page) => {
    pagination.current_page = page
    loadData()
  }
  
  // 样式和工具函数复用AdminReport
  </script>