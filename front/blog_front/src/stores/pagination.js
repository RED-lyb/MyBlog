import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 分页状态管理
export const usePaginationStore = defineStore('pagination', () => {
  const currentPage = ref(1) // 当前页码
  const pageSize = ref(4) // 每页显示数量，固定为4
  const total = ref(0) // 总记录数

  // 计算总页数
  const totalPages = computed(() => {
    return Math.ceil(total.value / pageSize.value)
  })

  // 设置当前页码
  function setCurrentPage(page) {
    if (page >= 1) {
      // 如果总页数为0（还未加载数据），允许设置任何大于等于1的页码
      // 否则需要检查是否在有效范围内
      if (totalPages.value === 0 || page <= totalPages.value) {
        currentPage.value = page
        persistPagination()
      }
    }
  }

  // 设置总记录数
  function setTotal(count) {
    total.value = count
    persistPagination()
  }

  // 设置每页显示数量
  function setPageSize(size) {
    if (size >= 1) {
      pageSize.value = size
    }
  }

  // 重置分页状态
  function reset() {
    currentPage.value = 1
    total.value = 0
    persistPagination()
  }

  // 持久化到 localStorage
  function persistPagination() {
    const paginationData = {
      currentPage: currentPage.value,
      total: total.value
    }
    localStorage.setItem('article_pagination', JSON.stringify(paginationData))
  }

  // 从 localStorage 恢复
  function syncFromLocalStorage() {
    try {
      const raw = localStorage.getItem('article_pagination')
      if (raw) {
        const parsed = JSON.parse(raw)
        if (parsed.currentPage) {
          currentPage.value = parsed.currentPage
        }
        if (parsed.total) {
          total.value = parsed.total
        }
      }
    } catch (_) {
      // 解析失败，使用默认值
    }
  }

  return {
    currentPage,
    pageSize,
    total,
    totalPages,
    setCurrentPage,
    setTotal,
    setPageSize,
    reset,
    syncFromLocalStorage
  }
})

