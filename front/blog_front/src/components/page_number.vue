<template>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage3"
        v-model:page-size="pageSize3"
        layout="prev, pager, next"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
      <div class="jumper-input">
        <el-input
          v-model.number="jumperValue"
          :min="1"
          :max="maxPage"
          class="jumper-input-field"
          @blur="handleJumperBlur"
          @keyup.enter="handleJumperEnter"
        />
      </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'

const currentPage3 = ref(1) //当前页码
const pageSize3 = ref(10) //每页显示数量
const total = ref(1000) //总页数

// 计算最大页数
const maxPage = computed(() => {
  return Math.ceil(total.value / pageSize3.value)
})

// jumper输入框的值，与currentPage3双向绑定
const jumperValue = ref(currentPage3.value)

// 监听currentPage3变化，同步更新jumperValue
watch(currentPage3, (newVal) => {
  jumperValue.value = newVal
})

// 处理输入框失焦事件
const handleJumperBlur = () => {
  updatePageFromJumper()
}

// 处理输入框回车事件
const handleJumperEnter = () => {
  updatePageFromJumper()
}

// 从jumper输入框更新页码
const updatePageFromJumper = () => {
  let page = Number(jumperValue.value)
  if (isNaN(page) || page < 1) {
    page = 1
  } else if (page > maxPage.value) {
    page = maxPage.value
  }
  jumperValue.value = page
  currentPage3.value = page
}

const handleSizeChange = (val: number) => {
  console.log(`${val} items per page`)
}
const handleCurrentChange = (val: number) => {
  console.log(`current page: ${val}`)
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pagination-wrapper > * {
  width: 100%;
}
.jumper-input {
  display: flex;
  align-items: center;
}
.jumper-input-field {
  width: 60px;
}
.jumper-input-field :deep(.el-input__inner) {
  text-align: center;
}
/* 输入框 hover 和 focus 颜色 */
.jumper-input-field :deep(.el-input__wrapper):hover {
  box-shadow: 0 0 0 1px #EF5710 inset !important;
}
.jumper-input-field :deep(.el-input__wrapper):hover .el-input__inner {
  color: #EF5710 !important;
}
.jumper-input-field :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #EF5710 inset !important;
}
.jumper-input-field :deep(.el-input__wrapper.is-focus .el-input__inner) {
  color: #EF5710 !important;
}
/* 分页器统一 hover 颜色 - 覆盖 Element Plus 默认样式 */
:deep(.el-pager li:hover) {
  color: #EF5710 !important;
}
/* 分页器 prev/next 按钮 hover 颜色 */
:deep(.el-pagination .btn-next:hover),
:deep(.el-pagination .btn-prev:hover) {
  color: #EF5710 !important;
}
/* 分页器当前激活页面文字颜色 */
:deep(.el-pager li.is-active) {
  color: #C8161D !important;
}
:deep(.el-pager li.is-active:hover) {
  color: #C8161D !important;
}

</style>