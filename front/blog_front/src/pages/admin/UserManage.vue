<template>
  <div class="user-manage-container">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" plain @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>
    
    <!-- 用户表格 -->
    <el-table
      v-loading="loading"
      :data="users"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="registered_time" label="注册时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.registered_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="follow_count" label="关注数" width="100" />
      <el-table-column prop="article_count" label="文章数" width="100" />
      <el-table-column prop="liked_article_count" label="喜欢数" width="100" />
      <el-table-column prop="follower_count" label="粉丝数" width="100" />
      <el-table-column prop="is_admin" label="管理员" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_admin ? 'success' : 'info'">
            {{ row.is_admin ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" plain @click="handleEdit(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button 
            link 
            plain
            :type="row.is_admin ? 'warning' : 'success'" 
            @click="handleToggleAdmin(row)"
          >
            <el-icon><UserFilled /></el-icon>
            {{ row.is_admin ? '取消管理员' : '设为管理员' }}
          </el-button>
          <el-button link type="danger" plain @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" disabled />
        </el-form-item>
        <el-form-item label="头像URL" prop="avatar">
          <el-input v-model="formData.avatar" placeholder="请输入头像URL" />
        </el-form-item>
        <el-form-item label="背景色" prop="bg_color">
          <el-input v-model="formData.bg_color" placeholder="CSS颜色值，如 #ffffff" />
        </el-form-item>
        <el-form-item label="背景样式" prop="bg_pattern">
          <el-input v-model="formData.bg_pattern" placeholder="背景点缀样式" />
        </el-form-item>
        <el-form-item label="圆角大小" prop="corner_radius">
          <el-input v-model="formData.corner_radius" placeholder="如 10px 或 10%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" plain @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Edit, Delete, UserFilled } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const formData = ref({
  id: null,
  username: '',
  avatar: '',
  bg_color: '',
  bg_pattern: '',
  corner_radius: ''
})

const formRules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' }
  ]
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}admin/users/`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchKeyword.value
      }
    })
    
    if (response.data.success) {
      users.value = response.data.data.users
      total.value = response.data.data.total
    } else {
      ElMessage.error(response.data.error || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表错误:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchUsers()
}

const handlePageChange = () => {
  fetchUsers()
}

const handleEdit = async (row) => {
  try {
    const response = await apiClient.get(`${apiUrl}admin/users/${row.id}/`)
    
    if (response.data.success) {
      formData.value = {
        id: response.data.data.id,
        username: response.data.data.username,
        avatar: response.data.data.avatar || '',
        bg_color: response.data.data.bg_color || '',
        bg_pattern: response.data.data.bg_pattern || '',
        corner_radius: response.data.data.corner_radius || ''
      }
      dialogVisible.value = true
    } else {
      ElMessage.error(response.data.error || '获取用户信息失败')
    }
  } catch (error) {
    console.error('获取用户信息错误:', error)
    ElMessage.error('获取用户信息失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const response = await apiClient.put(
      `${apiUrl}admin/users/${formData.value.id}/update/`,
      formData.value
    )
    
    if (response.data.success) {
      ElMessage.success('用户信息更新成功')
      dialogVisible.value = false
      fetchUsers()
    } else {
      ElMessage.error(response.data.error || '更新用户信息失败')
    }
  } catch (error) {
    console.error('更新用户信息错误:', error)
    ElMessage.error('更新用户信息失败')
  } finally {
    submitting.value = false
  }
}

const handleToggleAdmin = (row) => {
  const action = row.is_admin ? '取消管理员权限' : '授予管理员权限'
  
  ElMessageBox.confirm(
    `确定要${action}吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.post(
        `${apiUrl}admin/users/${row.id}/toggle-admin/`
      )
      
      if (response.data.success) {
        ElMessage.success(response.data.message || '操作成功')
        fetchUsers()
      } else {
        ElMessage.error(response.data.error || '操作失败')
      }
    } catch (error) {
      console.error('切换管理员状态错误:', error)
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户"${row.username}"吗？此操作不可恢复！`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(`${apiUrl}admin/users/${row.id}/delete/`)
      
      if (response.data.success) {
        ElMessage.success('用户删除成功')
        fetchUsers()
      } else {
        ElMessage.error(response.data.error || '删除用户失败')
      }
    } catch (error) {
      console.error('删除用户错误:', error)
      ElMessage.error('删除用户失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manage-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: var(--el-text-color-primary);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

