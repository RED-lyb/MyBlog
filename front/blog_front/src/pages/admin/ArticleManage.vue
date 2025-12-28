<template>
  <div class="article-manage-container">
    <div class="page-header">
      <h1 class="page-title">文章管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建文章
      </el-button>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文章标题或作者"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>
    
    <!-- 文章表格 -->
    <el-table
      v-loading="loading"
      :data="articles"
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="author_name" label="作者" width="120" />
      <el-table-column prop="view_count" label="浏览量" width="100" />
      <el-table-column prop="love_count" label="喜欢数" width="100" />
      <el-table-column prop="comment_count" label="评论数" width="100" />
      <el-table-column prop="published_at" label="发布时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.published_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">
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
      :title="dialogTitle"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="作者ID" prop="author_id">
          <el-input-number v-model="formData.author_id" :min="1" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="15"
            placeholder="请输入文章内容（支持Markdown）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const articles = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const selectedArticles = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新建文章')
const submitting = ref(false)
const formRef = ref(null)
const formData = ref({
  id: null,
  title: '',
  content: '',
  author_id: null
})

const formRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' }
  ],
  author_id: [
    { required: true, message: '请输入作者ID', trigger: 'blur' }
  ]
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const fetchArticles = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}admin/articles/`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchKeyword.value
      }
    })
    
    if (response.data.success) {
      articles.value = response.data.data.articles
      total.value = response.data.data.total
    } else {
      ElMessage.error(response.data.error || '获取文章列表失败')
    }
  } catch (error) {
    console.error('获取文章列表错误:', error)
    ElMessage.error('获取文章列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchArticles()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchArticles()
}

const handlePageChange = () => {
  fetchArticles()
}

const handleSelectionChange = (selection) => {
  selectedArticles.value = selection
}

const handleCreate = () => {
  dialogTitle.value = '新建文章'
  formData.value = {
    id: null,
    title: '',
    content: '',
    author_id: null
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑文章'
  formData.value = {
    id: row.id,
    title: row.title,
    content: '',
    author_id: row.author_id
  }
  
  // 获取文章详情
  apiClient.get(`${apiUrl}admin/articles/${row.id}/`).then(response => {
    if (response.data.success) {
      formData.value.content = response.data.data.content
    }
  })
  
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (formData.value.id) {
      // 更新文章
      const response = await apiClient.put(
        `${apiUrl}admin/articles/${formData.value.id}/update/`,
        formData.value
      )
      
      if (response.data.success) {
        ElMessage.success('文章更新成功')
        dialogVisible.value = false
        fetchArticles()
      } else {
        ElMessage.error(response.data.error || '更新文章失败')
      }
    } else {
      // 创建文章
      const response = await apiClient.post(
        `${apiUrl}admin/articles/create/`,
        formData.value
      )
      
      if (response.data.success) {
        ElMessage.success('文章创建成功')
        dialogVisible.value = false
        fetchArticles()
      } else {
        ElMessage.error(response.data.error || '创建文章失败')
      }
    }
  } catch (error) {
    console.error('提交文章错误:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除文章"${row.title}"吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(`${apiUrl}admin/articles/${row.id}/delete/`)
      
      if (response.data.success) {
        ElMessage.success('文章删除成功')
        fetchArticles()
      } else {
        ElMessage.error(response.data.error || '删除文章失败')
      }
    } catch (error) {
      console.error('删除文章错误:', error)
      ElMessage.error('删除文章失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.article-manage-container {
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

