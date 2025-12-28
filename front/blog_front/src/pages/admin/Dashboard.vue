<template>
  <div class="dashboard-container">
    <h1 class="page-title">统计面板</h1>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon user-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.users?.total || 0 }}</div>
          <div class="stat-label">总用户数</div>
          <div class="stat-change positive">今日新增: {{ statistics.users?.today_new || 0 }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon article-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.articles?.total || 0 }}</div>
          <div class="stat-label">总文章数</div>
          <div class="stat-change positive">今日新增: {{ statistics.articles?.today_new || 0 }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon view-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(statistics.views?.total || 0) }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon like-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(statistics.likes?.total || 0) }}</div>
          <div class="stat-label">总喜欢数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon file-icon">
          <el-icon><Folder /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.network_disk?.file_count || 0 }}</div>
          <div class="stat-label">网盘文件数</div>
          <div class="stat-change">{{ statistics.network_disk?.total_size_gb || 0 }} GB</div>
        </div>
      </div>
    </div>
    
    <!-- 趋势图表 -->
    <div class="chart-container">
      <div class="chart-card">
        <h2 class="chart-title">最近7天数据趋势</h2>
        <canvas ref="trendChartRef"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import { User, Document, View, Star, Folder } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import apiClient from '../../lib/api.js'

Chart.register(...registerables)

const apiUrl = import.meta.env.VITE_API_URL
const statistics = ref({
  users: {},
  articles: {},
  views: {},
  likes: {},
  network_disk: {},
  trend: []
})

const trendChartRef = ref(null)
let trendChart = null

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const fetchStatistics = async () => {
  try {
    const response = await apiClient.get(`${apiUrl}admin/statistics/`)
    if (response.data.success) {
      statistics.value = response.data.data
      updateChart()
    } else {
      ElMessage.error(response.data.error || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据错误:', error)
    ElMessage.error('获取统计数据失败')
  }
}

const updateChart = () => {
  if (!trendChartRef.value || !statistics.value.trend) return
  
  const ctx = trendChartRef.value.getContext('2d')
  
  // 销毁旧图表
  if (trendChart) {
    trendChart.destroy()
  }
  
  const trendData = statistics.value.trend || []
  const labels = trendData.map(item => item.date)
  const userData = trendData.map(item => item.users)
  const articleData = trendData.map(item => item.articles)
  
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '新增用户',
          data: userData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        },
        {
          label: '新增文章',
          data: articleData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

onMounted(() => {
  fetchStatistics()
})

onBeforeUnmount(() => {
  if (trendChart) {
    trendChart.destroy()
  }
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 24px;
  color: var(--el-text-color-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.user-icon {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.article-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.view-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.like-icon {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.file-icon {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-change.positive {
  color: #67c23a;
}

.chart-container {
  margin-top: 30px;
}

.chart-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 24px;
}

.chart-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
}

.chart-card canvas {
  max-height: 400px;
}
</style>

