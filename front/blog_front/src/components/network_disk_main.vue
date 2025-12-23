<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Edit } from '@element-plus/icons-vue'
import { ElIcon } from 'element-plus'
import FullScreenLoading from '../pages/FullScreenLoading.vue'

// Props
const props = defineProps({
  directories: {
    type: Array,
    default: () => []
  },
  files: {
    type: Array,
    default: () => []
  },
  loadingFiles: {
    type: Boolean,
    default: false
  },
  pathParts: {
    type: Array,
    default: () => []
  },
  pathUsernames: {
    type: Array,
    default: () => []
  },
  currentPath: {
    type: String,
    default: ''
  },
  canDelete: {
    type: Boolean,
    default: false
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  currentOwnerId: {
    type: [Number, String, null],
    default: null
  },
  userId: {
    type: [Number, String, null],
    default: null
  }
})

// Emits
const emit = defineEmits([
  'navigate-to-path',
  'enter-directory',
  'download-file',
  'download-archive',
  'delete-items',
  'edit-file'
])

// 选中的文件
const selectedItems = ref([])

// 所有项目（目录+文件）
const allItems = computed(() => {
  return [...props.directories, ...props.files]
})

// 选中的文件（不包括目录）
const selectedFiles = computed(() => {
  return selectedItems.value.filter(item => !item.is_directory)
})

// 是否只选中了一个项目（文件或文件夹）
const isSingleItemSelected = computed(() => {
  return selectedItems.value.length === 1
})

// 是否在根目录
const isRootDirectory = computed(() => {
  return props.pathParts.length === 0
})

// 是否可以编辑（不在根目录且只选中一个项目）
const canEditSelected = computed(() => {
  return !isRootDirectory.value && isSingleItemSelected.value
})

// 是否可以删除（在自己的文件空间下）
const canDeleteSelected = computed(() => {
  return props.canDelete && props.isAuthenticated && props.currentOwnerId === props.userId
})

// 面包屑
const breadcrumbs = computed(() => {
  const parts = props.pathParts.length > 0 ? props.pathParts : []
  const usernames = props.pathUsernames.length > 0 ? props.pathUsernames : []
  const crumbs = [
    { name: '根目录', path: '', isLast: parts.length === 0 }
  ]
  
  parts.forEach((part, index) => {
    const displayName = usernames[index] || part
    crumbs.push({
      name: displayName,
      path: parts.slice(0, index + 1).join('/'),
      isLast: index === parts.length - 1
    })
  })
  
  return crumbs
})

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const tableRef = ref(null)

// 全选/取消全选
const handleSelectAll = (selection) => {
  selectedItems.value = selection
}

// 单选
const handleSelect = (selection, row) => {
  selectedItems.value = selection
}

// 监听 allItems 变化，清空选择
watch(() => [props.directories, props.files], () => {
  selectedItems.value = []
  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}, { deep: true })

// 下载选中的文件/文件夹
const handleDownloadSelected = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要下载的项目')
    return
  }
  
  // 保存选中的项目，因为emit后需要清空
  const itemsToDownload = [...selectedItems.value]
  
  // 如果只有一个文件，直接下载
  if (itemsToDownload.length === 1 && !itemsToDownload[0].is_directory) {
    emit('download-file', itemsToDownload[0].name)
    // 清空选择
    selectedItems.value = []
    if (tableRef.value) {
      tableRef.value.clearSelection()
    }
    return
  }
  
  // 多个文件或包含文件夹，使用打包下载
  emit('download-archive', itemsToDownload)
  
  // 等待一下再清空，确保下载已经开始
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // 清空选择
  selectedItems.value = []
  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}

// 编辑选中的文件/文件夹（重命名）
const handleEditSelected = () => {
  if (selectedItems.value.length !== 1) {
    ElMessage.warning('请选择一个项目进行重命名')
    return
  }
  
  emit('edit-file', selectedItems.value[0])
}

// 删除选中的项目
const handleDeleteSelected = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要删除的项目')
    return
  }
  
  const items = selectedItems.value
  const fileCount = items.filter(item => !item.is_directory).length
  const dirCount = items.filter(item => item.is_directory).length
  
  let message = '确定要删除选中的'
  if (fileCount > 0 && dirCount > 0) {
    message += `${fileCount}个文件和${dirCount}个目录吗？`
  } else if (fileCount > 0) {
    message += `${fileCount}个文件吗？`
  } else {
    message += `${dirCount}个目录吗？（目录下的所有文件将被删除）`
  }
  
  try {
    await ElMessageBox.confirm(
      message,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    emit('delete-items', items)
    
    // 清空选择
    selectedItems.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除错误:', error)
    }
  }
}
</script>

<template>
  <div class="network-disk-container">
    <!-- 路径导航和操作按钮 -->
    <div class="breadcrumb-container">
      <div class="breadcrumb-wrapper" style="flex: 0 0 70%;">
        <div class="dsi-breadcrumbs text-sm items-center gap-2;">
          <ul>
            <li v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
              <a 
                v-if="!crumb.isLast"
                @click.prevent="emit('navigate-to-path', crumb.path)"
                class="breadcrumb-link"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  class="h-4 w-4 stroke-current">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                </svg>
                {{ crumb.name }}
              </a>
              
              <span v-else class="inline-flex items-center gap-2">
                <!-- 当前打开的路径：显示打开的文件夹图标 -->
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  class="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-width="2">
                  <g>
                    <path d="M3 12V7.2c0-1.12 0-1.68.218-2.108a2 2 0 0 1 .874-.874C4.52 4 5.08 4 6.2 4h1.475c.489 0 .733 0 .963.055a2 2 0 0 1 .579.24c.201.123.374.296.72.642l.126.126c.346.346.519.519.72.642c.18.11.375.19.579.24c.23.055.474.055.963.055h.475c1.12 0 1.68 0 2.108.218a2 2 0 0 1 .874.874C16 7.52 16 8.08 16 9.2v.3"></path>
                    <path d="M4.7 20h10.92c.854 0 1.28 0 1.64-.146a2 2 0 0 0 .813-.604c.243-.303.366-.713.611-1.53l1.08-3.6c.419-1.397.628-2.095.477-2.648a2 2 0 0 0-.869-1.168C18.886 10 18.157 10 16.699 10h-5.318c-.854 0-1.281 0-1.642.146a2 2 0 0 0-.812.604c-.243.303-.366.712-.611 1.53l-1.948 6.494A1.72 1.72 0 0 1 4.72 20v0C3.77 20 3 19.23 3 18.28V11m8 4h5"></path>
                  </g>
                </svg>
                {{ crumb.name }}
              </span>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 操作按钮区域 -->
      <div class="action-buttons-wrapper" style="flex: 0 0 30%;" v-if="selectedItems.length > 0">
        <div class="action-buttons">
          <button 
            class="dsi-btn dsi-btn-outline dsi-btn-success"
            @click="handleDownloadSelected"
          >
            <el-icon><Download /></el-icon>
            下载
          </button>
          <button 
            class="dsi-btn dsi-btn-outline dsi-btn-info"
            :disabled="!canEditSelected"
            @click="handleEditSelected"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </button>
          <button 
            class="dsi-btn dsi-btn-outline dsi-btn-error"
            :disabled="!canDeleteSelected"
            @click="handleDeleteSelected"
          >
            <el-icon><Delete /></el-icon>
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <FullScreenLoading :visible="loadingFiles" />
    <div class="file-list-container"">
      <el-table 
        ref="tableRef"
        :data="allItems" 
        style="width: 100%"
        stripe
        @select-all="handleSelectAll"
        @select="handleSelect"
        row-key="name"
      >
        <el-table-column type="selection" width="55" :reserve-selection="false" />
        <el-table-column prop="name" label="名称" min-width="300">
          <template #default="{ row }">
            <div class="file-name-cell">
              <!-- 文件夹图标 -->
              <svg
                v-if="row.is_directory"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                class="h-4 w-4 stroke-current file-icon"
                @click="emit('enter-directory', row)"
                style="cursor: pointer;">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
              </svg>
              <!-- 文件图标 -->
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                class="file-icon file-icon-default">
                <g fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="2">
                  <path stroke-linecap="round" d="M4 4v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.342a2 2 0 0 0-.602-1.43l-4.44-4.342A2 2 0 0 0 13.56 2H6a2 2 0 0 0-2 2m5 9h6m-6 4h3"></path>
                  <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
                </g>
              </svg>
              <!-- 文件夹名称（可点击进入） -->
              <span 
                v-if="row.is_directory"
                @click="emit('enter-directory', row)"
                class="file-name-link"
                style="cursor: pointer;">
                {{ row.display_name || row.name }}
              </span>
              <!-- 文件名称（可点击下载） -->
              <a
                v-else
                @click.prevent="emit('download-file', row.name)"
                class="file-name-link">
                {{ row.name }}
              </a>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size_formatted" label="大小" width="120" align="right">
          <template #default="{ row }">
            {{ row.size_formatted || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="修改时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.modified_time) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.network-disk-container {
  max-width: 1400px;
}

.breadcrumb-container {
  margin: 10px;
  display: flex;
  align-items: center;
}

.breadcrumb-wrapper {
  min-width: 0;
}

.action-buttons-wrapper {
  display: flex;
  justify-content: flex-end;
  min-width: 0;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-buttons button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 14px;
}

.action-buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons button .el-icon {
  font-size: 16px;
}

.file-list-container {
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 10px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.file-name-link {
  text-decoration: none;
}

.file-name-link:hover {
  color: #EF5710;
  text-decoration: underline;
}

.el-table {
  --el-table-border-color: var(--el-border-color-lighter);
}

.el-table :deep(.el-table__row) {
  cursor: default;
}

.el-table :deep(.el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}
.dsi-btn{
  height: 25px;
  font-weight: 400;
  font-size: 12px;
  border: 1px solid;
}
.dsi-btn:hover{
  border: 1px solid var(--dsi-btn-bg);
}
</style>

