<template>
  <div class="love-nest-manage">
    <div class="page-header">
      <h1 class="page-title">爱情小窝管理</h1>
    </div>

    <el-tabs v-model="activeTab" class="manage-tabs">
      <el-tab-pane v-if="isAdmin" label="基础配置" name="config">
        <el-form label-width="120px" class="config-form">
          <el-form-item label="在一起日期">
            <el-date-picker
              v-model="configForm.start_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
            />
          </el-form-item>
          <el-form-item label="爱情口号">
            <el-input v-model="configForm.slogan" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" plain :loading="savingConfig" @click="saveConfig">
              保存配置
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane v-if="isAdmin" label="成员管理" name="members">
        <el-form label-width="120px" class="config-form">
          <el-form-item label="编辑成员">
            <el-select
              v-model="memberIds"
              multiple
              filterable
              placeholder="选择可编辑成员"
              style="width: 100%; max-width: 480px;"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.id"
                :label="`${user.username} (ID: ${user.id})`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" plain :loading="savingMembers" @click="saveMembers">
              保存成员
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="相册" name="photos">
        <div class="tab-toolbar">
          <el-button type="primary" plain @click="openPhotoCreate">
            <el-icon><Plus /></el-icon>
            上传照片
          </el-button>
        </div>
        <el-table v-loading="loadingPhotos" :data="photos" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column label="预览" width="100">
            <template #default="{ row }">
              <el-image :src="photoUrl(row)" fit="cover" style="width: 56px; height: 56px;" />
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="120" />
          <el-table-column label="分类" width="90">
            <template #default="{ row }">{{ photoCategoryLabel(row.category) }}</template>
          </el-table-column>
          <el-table-column prop="caption" label="描述" min-width="160" show-overflow-tooltip />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openPhotoEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="removePhoto(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="时光" name="diaries">
        <div class="tab-toolbar">
          <el-button type="primary" plain @click="openDiaryCreate">
            <el-icon><Plus /></el-icon>
            新建时光
          </el-button>
        </div>
        <el-table v-loading="loadingDiaries" :data="diaries" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="diary_date" label="日期" width="120" />
          <el-table-column label="配图" width="90">
            <template #default="{ row }">
              <img
                v-if="row.image_url"
                :src="resolveStaticUrl(row.image_url)"
                alt=""
                class="diary-thumb"
              />
              <span v-else class="text-muted">无</span>
            </template>
          </el-table-column>
          <el-table-column prop="sentence" label="一句话" min-width="220" show-overflow-tooltip />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDiaryEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="removeDiary(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="旅行" name="travel">
        <div class="tab-toolbar">
          <el-button type="primary" plain @click="openTravelCreate">
            <el-icon><Plus /></el-icon>
            添加城市
          </el-button>
        </div>
        <el-table v-loading="loadingTravel" :data="travelCities" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="city_name" label="城市" min-width="120" />
          <el-table-column label="省份" min-width="100">
            <template #default="{ row }">{{ provinceLabel(row.province_adcode) }}</template>
          </el-table-column>
          <el-table-column prop="adcode" label="编码" width="100" />
          <el-table-column prop="visited_at" label="到访日期" width="120" />
          <el-table-column prop="note" label="感言" min-width="160" show-overflow-tooltip />
          <el-table-column label="照片" min-width="180">
            <template #default="{ row }">
              <div v-if="row.photos?.length" class="travel-thumb-row">
                <img
                  v-for="photo in row.photos.slice(0, 4)"
                  :key="photo.id"
                  :src="photoUrl(photo)"
                  :alt="photo.title || row.city_name"
                  class="travel-thumb"
                />
                <span v-if="row.photos.length > 4" class="travel-thumb-more">
                  +{{ row.photos.length - 4 }}
                </span>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openTravelEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="removeTravel(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="纪念日" name="milestones">
        <div class="tab-toolbar">
          <el-button type="primary" plain @click="openMilestoneCreate">
            <el-icon><Plus /></el-icon>
            新建纪念日
          </el-button>
        </div>
        <el-table v-loading="loadingMilestones" :data="milestones" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="title" label="名称" min-width="140" />
          <el-table-column prop="milestone_date" label="日期" width="120" />
          <el-table-column label="每年重复" width="100">
            <template #default="{ row }">{{ row.is_yearly ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openMilestoneEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="removeMilestone(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="photoDialogVisible"
      :title="photoDialogTitle"
      width="560px"
      :close-on-click-modal="false"
      destroy-on-close
      @closed="resetPhotoDialog"
    >
      <el-form label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="photoForm.category" style="width: 160px;">
            <el-option label="人物" value="person" />
            <el-option label="风景" value="scenery" />
            <el-option label="食物" value="food" />
          </el-select>
        </el-form-item>
        <el-form-item label="照片">
          <div class="photo-upload-tools">
            <el-upload
              :show-file-list="false"
              accept="image/*"
              :http-request="handlePhotoFilePick"
            >
              <el-button type="primary" plain>
                {{ photoDialogMode === 'create' ? '选择图片' : '更换图片' }}
              </el-button>
            </el-upload>
            <span v-if="photoPendingFile" class="form-tip inline-tip">
              已选：{{ photoPendingFile.name }}
            </span>
          </div>
          <img v-if="photoPreviewSrc" :src="photoPreviewSrc" alt="" class="photo-preview" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="photoForm.title" placeholder="可选" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="photoForm.caption" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="photoDialogVisible = false">取消</el-button>
        <el-button type="primary" plain :loading="submitting" @click="submitPhotoDialog">
          {{ photoDialogMode === 'create' ? '上传' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="diaryDialogVisible" :title="diaryDialogTitle" width="640px">
      <el-form label-width="88px">
        <el-form-item label="日期">
          <el-date-picker v-model="diaryForm.diary_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="配图">
          <el-radio-group v-model="diaryImageMode" class="diary-image-mode">
            <el-radio-button value="album">从相册选择</el-radio-button>
            <el-radio-button value="upload">上传新图</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="diaryImageMode === 'album'" label="相册">
          <div class="album-picker">
            <div
              v-for="photo in albumPickerPhotos"
              :key="photo.id"
              class="album-picker__item"
              :class="{ 'is-selected': diarySelectedPhotoId === photo.id }"
              @click="selectDiaryPhoto(photo)"
            >
              <img :src="photoUrl(photo)" :alt="photo.title || '相册图片'" />
            </div>
            <p v-if="!albumPickerPhotos.length" class="form-tip">相册暂无图片</p>
          </div>
        </el-form-item>

        <template v-else>
          <el-form-item label="分类">
            <el-select v-model="diaryUploadCategory" style="width: 160px;">
              <el-option label="人物" value="person" />
              <el-option label="风景" value="scenery" />
              <el-option label="食物" value="food" />
            </el-select>
          </el-form-item>
          <el-form-item label="照片">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              @change="handleDiaryImageSelect"
            >
              <el-button type="primary" plain>选择图片</el-button>
            </el-upload>
          </el-form-item>
        </template>

        <el-form-item v-if="diaryImagePreview" label="预览">
          <img
            :src="diaryImagePreview"
            alt=""
            class="diary-preview"
          />
        </el-form-item>
        <el-form-item label="一句话">
          <el-input
            v-model="diaryForm.sentence"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="diaryDialogVisible = false">取消</el-button>
        <el-button type="primary" plain :loading="submitting" @click="submitDiary">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="travelDialogVisible" :title="travelDialogTitle" width="640px">
      <el-form label-width="88px">
        <el-form-item label="省份">
          <el-select
            v-model="travelForm.province_adcode"
            filterable
            placeholder="选择省份"
            style="width: 220px;"
            :disabled="!!travelForm.id"
          >
            <el-option
              v-for="item in provinceOptionsFromApi"
              :key="item.adcode"
              :label="item.name"
              :value="item.adcode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-select
            v-model="travelForm.adcode"
            filterable
            placeholder="请先选择省份"
            style="width: 220px;"
            :disabled="!!travelForm.id || !travelForm.province_adcode"
            :loading="loadingTravelCities"
            @change="onTravelCityChange"
          >
            <el-option
              v-for="item in travelCityOptions"
              :key="item.adcode"
              :label="item.name"
              :value="item.adcode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="到访日期">
          <el-date-picker
            v-model="travelForm.visited_at"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="感言">
          <el-input v-model="travelForm.note" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
        <el-form-item label="配图">
          <el-radio-group v-model="travelImageMode" class="diary-image-mode">
            <el-radio-button value="album">从相册选择</el-radio-button>
            <el-radio-button value="upload">上传新图</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="travelImageMode === 'album'" label="相册">
          <div class="album-picker">
            <div
              v-for="photo in albumPickerPhotos"
              :key="photo.id"
              class="album-picker__item"
              :class="{ 'is-selected': travelSelectedPhotoIds.includes(photo.id) }"
              @click="toggleTravelPhoto(photo.id)"
            >
              <img :src="photoUrl(photo)" :alt="photo.title || '相册图片'" />
            </div>
            <p v-if="!albumPickerPhotos.length" class="form-tip">相册暂无图片</p>
          </div>
          <p v-if="travelSelectedPhotoIds.length" class="form-tip">
            已选 {{ travelSelectedPhotoIds.length }} 张
          </p>
        </el-form-item>
        <template v-else>
          <el-form-item label="分类">
            <el-select v-model="travelUploadCategory" style="width: 160px;">
              <el-option label="人物" value="person" />
              <el-option label="风景" value="scenery" />
              <el-option label="食物" value="food" />
            </el-select>
          </el-form-item>
          <el-form-item label="照片">
            <el-upload
              multiple
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              @change="handleTravelImagesSelect"
            >
              <el-button type="primary" plain>选择图片</el-button>
            </el-upload>
            <div v-if="travelPendingPreviews.length" class="album-picker">
              <div
                v-for="(preview, index) in travelPendingPreviews"
                :key="preview"
                class="album-picker__item travel-pending-item"
              >
                <img :src="preview" alt="待上传" />
                <button
                  type="button"
                  class="travel-pending-remove"
                  @click="removeTravelPendingFile(index)"
                >
                  ×
                </button>
              </div>
            </div>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="travelDialogVisible = false">取消</el-button>
        <el-button type="primary" plain :loading="submitting" @click="submitTravel">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="milestoneDialogVisible" :title="milestoneDialogTitle" width="520px">
      <el-form label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="milestoneForm.title" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="milestoneForm.milestone_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="每年重复">
          <el-switch v-model="milestoneForm.is_yearly" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="milestoneForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="milestoneForm.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="milestoneDialogVisible = false">取消</el-button>
        <el-button type="primary" plain :loading="submitting" @click="submitMilestone">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'
import {
  fetchLoveNestConfig,
  fetchLoveNestPhotos,
  fetchLoveNestDiaries,
  fetchLoveNestMilestones,
  checkLoveNestEditor,
  updateLoveNestConfig,
  updateLoveNestMembers,
  uploadLoveNestPhoto,
  updateLoveNestPhoto,
  deleteLoveNestPhoto,
  createLoveNestDiary,
  updateLoveNestDiary,
  deleteLoveNestDiary,
  createLoveNestMilestone,
  updateLoveNestMilestone,
  deleteLoveNestMilestone,
  fetchLoveNestTravel,
  createLoveNestTravelCity,
  updateLoveNestTravelCity,
  deleteLoveNestTravelCity,
  resolveStaticUrl,
} from '../../lib/loveNestApi.js'
import { prepareLoveNestImage } from '../../lib/loveNestImage.js'
import { PROVINCE_NAMES, fetchProvinceOptions, fetchCityOptions } from '../../lib/loveNestMap.js'

const router = useRouter()
const apiUrl = import.meta.env.VITE_API_URL

const activeTab = ref('photos')
const isAdmin = ref(false)
const canEdit = ref(false)

const configForm = ref({ start_date: '', slogan: '' })
const memberIds = ref([])
const userOptions = ref([])

const photos = ref([])
const diaries = ref([])
const milestones = ref([])
const travelCities = ref([])

const loadingPhotos = ref(false)
const loadingDiaries = ref(false)
const loadingMilestones = ref(false)
const loadingTravel = ref(false)
const savingConfig = ref(false)
const savingMembers = ref(false)
const submitting = ref(false)

const photoDialogVisible = ref(false)
const photoDialogMode = ref('create')
const photoPendingFile = ref(null)
const photoPreviewSrc = ref('')
const diaryDialogVisible = ref(false)
const milestoneDialogVisible = ref(false)
const travelDialogVisible = ref(false)

const PHOTO_CATEGORY_LABELS = {
  person: '人物',
  scenery: '风景',
  food: '食物',
}

function photoCategoryLabel(value) {
  return PHOTO_CATEGORY_LABELS[value] || value || '-'
}

function provinceLabel(adcode) {
  return PROVINCE_NAMES[adcode] || adcode || '-'
}

const photoForm = ref({ id: null, title: '', caption: '', category: 'person' })
const diaryForm = ref({ id: null, sentence: '', diary_date: '' })
const diaryImageMode = ref('album')
const diarySelectedPhotoId = ref(null)
const diaryUploadCategory = ref('person')
const diaryImagePreview = ref('')
const travelForm = ref({
  id: null,
  province_adcode: '',
  city_name: '',
  adcode: '',
  visited_at: '',
  note: '',
})
const travelImageMode = ref('album')
const travelSelectedPhotoIds = ref([])
const travelUploadCategory = ref('scenery')
const travelPendingFiles = ref([])
const travelPendingPreviews = ref([])
const provinceOptionsFromApi = ref([])
const travelCityOptions = ref([])
const loadingTravelCities = ref(false)
const milestoneForm = ref({
  id: null,
  title: '',
  milestone_date: '',
  description: '',
  is_yearly: true,
  sort_order: 0,
})
const diaryDialogTitle = computed(() => (diaryForm.value.id ? '编辑时光' : '新建时光'))
const milestoneDialogTitle = computed(() => (milestoneForm.value.id ? '编辑纪念日' : '新建纪念日'))
const photoDialogTitle = computed(() => (photoDialogMode.value === 'create' ? '上传照片' : '编辑照片'))
const travelDialogTitle = computed(() => (travelForm.value.id ? '编辑旅行' : '添加城市'))
const albumPickerPhotos = computed(() =>
  photos.value.filter((photo) => ['person', 'scenery', 'food'].includes(photo.category))
)

function photoUrl(row) {
  return resolveStaticUrl(row.url)
}

async function ensureAccess() {
  try {
    const response = await checkLoveNestEditor()
    if (!response.data.success || !response.data.data?.can_edit) {
      ElMessage.error('你没有爱情小窝编辑权限')
      router.replace('/home')
      return false
    }
    isAdmin.value = !!response.data.data?.is_admin
    canEdit.value = true
    activeTab.value = isAdmin.value ? 'config' : 'photos'
    return true
  } catch (error) {
    ElMessage.error('权限检查失败')
    router.replace('/home')
    return false
  }
}

async function loadConfig() {
  const response = await fetchLoveNestConfig()
  if (response.data.success) {
    const data = response.data.data || {}
    configForm.value = {
      start_date: data.start_date || '',
      slogan: data.slogan || '',
    }
    memberIds.value = (data.members || []).map((item) => item.id)
  }
}

async function loadUsers() {
  if (!isAdmin.value) return
  const response = await apiClient.get(`${apiUrl}admin/users/`, {
    params: { page: 1, page_size: 200 },
  })
  if (response.data.success) {
    userOptions.value = response.data.data?.users || []
  }
}

async function loadPhotos() {
  loadingPhotos.value = true
  try {
    const response = await fetchLoveNestPhotos({ page: 1, page_size: 100 })
    if (response.data.success) {
      photos.value = response.data.data?.photos || []
    }
  } finally {
    loadingPhotos.value = false
  }
}

async function loadDiaries() {
  loadingDiaries.value = true
  try {
    const response = await fetchLoveNestDiaries({ page: 1, page_size: 100 })
    if (response.data.success) {
      diaries.value = response.data.data?.diaries || []
    }
  } finally {
    loadingDiaries.value = false
  }
}

async function loadMilestones() {
  loadingMilestones.value = true
  try {
    const response = await fetchLoveNestMilestones()
    if (response.data.success) {
      milestones.value = response.data.data?.milestones || []
    }
  } finally {
    loadingMilestones.value = false
  }
}

async function loadProvinceOptions() {
  try {
    provinceOptionsFromApi.value = await fetchProvinceOptions()
  } catch {
    provinceOptionsFromApi.value = Object.entries(PROVINCE_NAMES).map(([adcode, name]) => ({
      adcode,
      name,
    }))
  }
}

async function loadTravelCityOptions(provinceAdcode) {
  if (!provinceAdcode) {
    travelCityOptions.value = []
    return
  }
  loadingTravelCities.value = true
  try {
    travelCityOptions.value = await fetchCityOptions(provinceAdcode)
  } catch (error) {
    travelCityOptions.value = []
    ElMessage.error(error.message || '城市列表加载失败')
  } finally {
    loadingTravelCities.value = false
  }
}

function onTravelCityChange(adcode) {
  const city = travelCityOptions.value.find((item) => item.adcode === adcode)
  if (city) {
    travelForm.value.adcode = city.adcode
    travelForm.value.city_name = city.name
  }
}

watch(
  () => travelForm.value.province_adcode,
  async (code, prevCode) => {
    if (!travelDialogVisible.value) return
    await loadTravelCityOptions(code)
    if (!travelForm.value.id && code !== prevCode) {
      travelForm.value.adcode = ''
      travelForm.value.city_name = ''
    }
  }
)

async function loadTravel() {
  loadingTravel.value = true
  try {
    const response = await fetchLoveNestTravel()
    if (response.data.success) {
      travelCities.value = response.data.data?.cities || []
    }
  } finally {
    loadingTravel.value = false
  }
}

async function saveConfig() {
  savingConfig.value = true
  try {
    const response = await updateLoveNestConfig({
      start_date: configForm.value.start_date || null,
      slogan: configForm.value.slogan || null,
    })
    if (response.data.success) {
      ElMessage.success('配置已保存')
      await loadConfig()
    }
  } catch (error) {
    ElMessage.error('保存配置失败')
  } finally {
    savingConfig.value = false
  }
}

async function saveMembers() {
  savingMembers.value = true
  try {
    const response = await updateLoveNestMembers({ member_user_ids: memberIds.value })
    if (response.data.success) {
      ElMessage.success('成员已保存')
      await loadConfig()
    }
  } catch (error) {
    ElMessage.error('保存成员失败')
  } finally {
    savingMembers.value = false
  }
}

function resetPhotoDialog() {
  photoPendingFile.value = null
  photoPreviewSrc.value = ''
  photoForm.value = { id: null, title: '', caption: '', category: 'person' }
  photoDialogMode.value = 'create'
}

function openPhotoCreate() {
  resetPhotoDialog()
  photoDialogMode.value = 'create'
  photoDialogVisible.value = true
}

async function handlePhotoFilePick(options) {
  const rawFile = options.file?.raw || options.file
  if (!rawFile) return
  try {
    const file = await prepareLoveNestImage(rawFile)
    photoPendingFile.value = file
    photoPreviewSrc.value = URL.createObjectURL(file)
  } catch (error) {
    ElMessage.error(error.message || '图片处理失败')
  }
}

function openPhotoEdit(row) {
  photoDialogMode.value = 'edit'
  photoForm.value = {
    id: row.id,
    title: row.title || '',
    caption: row.caption || '',
    category: row.category || 'person',
  }
  photoPendingFile.value = null
  photoPreviewSrc.value = photoUrl(row)
  photoDialogVisible.value = true
}

async function submitPhotoDialog() {
  submitting.value = true
  try {
    if (photoDialogMode.value === 'create') {
      if (!photoPendingFile.value) {
        ElMessage.warning('请先选择图片')
        return
      }
      const formData = new FormData()
      formData.append('file', photoPendingFile.value)
      formData.append('category', photoForm.value.category || 'person')
      if (photoForm.value.title) formData.append('title', photoForm.value.title)
      if (photoForm.value.caption) formData.append('caption', photoForm.value.caption)
      const response = await uploadLoveNestPhoto(formData)
      if (response.data.success) {
        ElMessage.success('上传成功')
        photoDialogVisible.value = false
        await loadPhotos()
      } else {
        ElMessage.error(response.data.error || '上传失败')
      }
      return
    }

    const formData = new FormData()
    formData.append('category', photoForm.value.category || 'person')
    if (photoForm.value.title) formData.append('title', photoForm.value.title)
    if (photoForm.value.caption) formData.append('caption', photoForm.value.caption)
    if (photoPendingFile.value) {
      formData.append('file', photoPendingFile.value)
    }

    const response = await updateLoveNestPhoto(photoForm.value.id, formData)
    if (response.data.success) {
      ElMessage.success('已保存')
      photoDialogVisible.value = false
      await loadPhotos()
    } else {
      ElMessage.error(response.data.error || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function removePhoto(row) {
  try {
    await ElMessageBox.confirm('确定删除这张照片？', '确认', { type: 'warning' })
    const response = await deleteLoveNestPhoto(row.id)
    if (response.data.success) {
      ElMessage.success('已删除')
      await loadPhotos()
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function openDiaryCreate() {
  diaryForm.value = { id: null, sentence: '', diary_date: '' }
  diaryImageMode.value = 'album'
  diarySelectedPhotoId.value = null
  diaryUploadCategory.value = 'person'
  diaryImagePreview.value = ''
  diaryPendingFile.value = null
  diaryDialogVisible.value = true
}

function openDiaryEdit(row) {
  diaryForm.value = {
    id: row.id,
    sentence: row.sentence || '',
    diary_date: row.diary_date || '',
  }
  diaryImageMode.value = 'album'
  diarySelectedPhotoId.value = row.photo_id || null
  diaryUploadCategory.value = 'person'
  diaryPendingFile.value = null
  diaryImagePreview.value = row.photo?.url
    ? resolveStaticUrl(row.photo.url)
    : (row.image_url ? resolveStaticUrl(row.image_url) : '')
  diaryDialogVisible.value = true
}

function selectDiaryPhoto(photo) {
  diarySelectedPhotoId.value = photo.id
  diaryImagePreview.value = photoUrl(photo)
  diaryPendingFile.value = null
}

const diaryPendingFile = ref(null)

async function handleDiaryImageSelect(uploadFile) {
  const rawFile = uploadFile?.raw || uploadFile
  if (!rawFile) return
  try {
    const file = await prepareLoveNestImage(rawFile)
    diaryPendingFile.value = file
    diarySelectedPhotoId.value = null
    diaryImagePreview.value = URL.createObjectURL(file)
  } catch (error) {
    ElMessage.error(error.message || '图片处理失败')
  }
}

async function submitDiary() {
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('diary_date', diaryForm.value.diary_date || '')
    formData.append('sentence', diaryForm.value.sentence || '')

    if (diaryImageMode.value === 'album' && diarySelectedPhotoId.value) {
      formData.append('photo_id', String(diarySelectedPhotoId.value))
    } else if (diaryImageMode.value === 'upload' && diaryPendingFile.value) {
      formData.append('file', diaryPendingFile.value)
      formData.append('category', diaryUploadCategory.value)
    }

    const response = diaryForm.value.id
      ? await updateLoveNestDiary(diaryForm.value.id, formData)
      : await createLoveNestDiary(formData)

    if (response.data.success) {
      ElMessage.success('已保存')
      diaryDialogVisible.value = false
      await loadDiaries()
      if (diaryImageMode.value === 'upload' && diaryPendingFile.value) {
        await loadPhotos()
      }
    } else {
      ElMessage.error(response.data.error || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function removeDiary(row) {
  try {
    await ElMessageBox.confirm('确定删除这条时光记录？', '确认', { type: 'warning' })
    const response = await deleteLoveNestDiary(row.id)
    if (response.data.success) {
      ElMessage.success('已删除')
      await loadDiaries()
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetTravelPendingFiles() {
  travelPendingPreviews.value.forEach((url) => URL.revokeObjectURL(url))
  travelPendingFiles.value = []
  travelPendingPreviews.value = []
}

function openTravelCreate() {
  travelForm.value = {
    id: null,
    province_adcode: '',
    city_name: '',
    adcode: '',
    visited_at: '',
    note: '',
  }
  travelImageMode.value = 'album'
  travelSelectedPhotoIds.value = []
  travelUploadCategory.value = 'scenery'
  resetTravelPendingFiles()
  travelCityOptions.value = []
  travelDialogVisible.value = true
}

async function openTravelEdit(row) {
  travelForm.value = {
    id: row.id,
    province_adcode: row.province_adcode || '',
    city_name: row.city_name || '',
    adcode: row.adcode || '',
    visited_at: row.visited_at || '',
    note: row.note || '',
  }
  travelImageMode.value = 'album'
  travelSelectedPhotoIds.value = (row.photos || []).map((photo) => photo.id)
  resetTravelPendingFiles()
  travelDialogVisible.value = true
  await loadTravelCityOptions(row.province_adcode)
}

function toggleTravelPhoto(photoId) {
  const ids = travelSelectedPhotoIds.value
  if (ids.includes(photoId)) {
    travelSelectedPhotoIds.value = ids.filter((id) => id !== photoId)
  } else {
    travelSelectedPhotoIds.value = [...ids, photoId]
  }
}

async function handleTravelImagesSelect(uploadFile) {
  const rawFile = uploadFile?.raw || uploadFile
  if (!rawFile) return
  try {
    const file = await prepareLoveNestImage(rawFile)
    travelPendingFiles.value.push(file)
    travelPendingPreviews.value.push(URL.createObjectURL(file))
  } catch (error) {
    ElMessage.error(error.message || '图片处理失败')
  }
}

function removeTravelPendingFile(index) {
  const preview = travelPendingPreviews.value[index]
  if (preview) URL.revokeObjectURL(preview)
  travelPendingFiles.value.splice(index, 1)
  travelPendingPreviews.value.splice(index, 1)
}

async function submitTravel() {
  submitting.value = true
  try {
    if (!travelForm.value.province_adcode || !travelForm.value.adcode) {
      ElMessage.warning('请选择省份和城市')
      return
    }

    let photoIds = [...travelSelectedPhotoIds.value]

    if (travelPendingFiles.value.length) {
      for (const file of travelPendingFiles.value) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('category', travelUploadCategory.value)
        const uploadResponse = await uploadLoveNestPhoto(formData)
        if (!uploadResponse.data.success) {
          ElMessage.error(uploadResponse.data.error || '图片上传失败')
          return
        }
        photoIds.push(uploadResponse.data.data.id)
      }
      await loadPhotos()
    }

    const payload = {
      province_adcode: travelForm.value.province_adcode,
      city_name: travelForm.value.city_name,
      adcode: travelForm.value.adcode,
      visited_at: travelForm.value.visited_at || null,
      note: travelForm.value.note || null,
      photo_ids: photoIds,
    }

    const response = travelForm.value.id
      ? await updateLoveNestTravelCity(travelForm.value.id, payload)
      : await createLoveNestTravelCity(payload)

    if (response.data.success) {
      ElMessage.success('已保存')
      travelDialogVisible.value = false
      resetTravelPendingFiles()
      await loadTravel()
    } else {
      ElMessage.error(response.data.error || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function removeTravel(row) {
  try {
    await ElMessageBox.confirm('确定删除这条旅行记录？', '确认', { type: 'warning' })
    const response = await deleteLoveNestTravelCity(row.id)
    if (response.data.success) {
      ElMessage.success('已删除')
      await loadTravel()
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function openMilestoneCreate() {
  milestoneForm.value = {
    id: null,
    title: '',
    milestone_date: '',
    description: '',
    is_yearly: true,
    sort_order: 0,
  }
  milestoneDialogVisible.value = true
}

function openMilestoneEdit(row) {
  milestoneForm.value = { ...row }
  milestoneDialogVisible.value = true
}

async function submitMilestone() {
  submitting.value = true
  try {
    const payload = { ...milestoneForm.value }
    delete payload.id
    const response = milestoneForm.value.id
      ? await updateLoveNestMilestone(milestoneForm.value.id, payload)
      : await createLoveNestMilestone(payload)
    if (response.data.success) {
      ElMessage.success('已保存')
      milestoneDialogVisible.value = false
      await loadMilestones()
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

async function removeMilestone(row) {
  try {
    await ElMessageBox.confirm('确定删除这个纪念日？', '确认', { type: 'warning' })
    const response = await deleteLoveNestMilestone(row.id)
    if (response.data.success) {
      ElMessage.success('已删除')
      await loadMilestones()
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  const ok = await ensureAccess()
  if (!ok) return
  await Promise.all([
    loadProvinceOptions(),
    loadConfig(),
    loadUsers(),
    loadPhotos(),
    loadDiaries(),
    loadMilestones(),
    loadTravel(),
  ])
})
</script>

<style scoped>
.love-nest-manage {
  padding: 0 4px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.manage-tabs {
  margin-top: 8px;
}

.config-form {
  max-width: 640px;
  padding-top: 12px;
}

.tab-toolbar {
  margin-bottom: 16px;
}

.photo-preview {
  display: block;
  width: 160px;
  height: 160px;
  margin-top: 12px;
  object-fit: cover;
  border-radius: 6px;
}

.photo-upload-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.diary-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
}

.diary-preview {
  display: block;
  width: 120px;
  height: 120px;
  margin-top: 12px;
  object-fit: cover;
  border-radius: 6px;
}

.form-tip {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.inline-tip {
  margin: 0 0 0 12px;
}

.diary-image-mode {
  margin-bottom: 0;
}

.album-picker {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
  gap: 10px;
  max-height: 220px;
  overflow-y: auto;
  padding: 4px 2px;
}

.album-picker__item {
  border: 2px solid var(--el-border-color);
  cursor: pointer;
  aspect-ratio: 1;
  overflow: hidden;
}

.album-picker__item.is-selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

.album-picker__item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.text-muted {
  color: var(--el-text-color-secondary);
}

.travel-thumb-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.travel-thumb {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.travel-thumb-more {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.travel-pending-item {
  position: relative;
}

.travel-pending-remove {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
}

.inline-tip {
  margin: 0 0 0 12px;
}
</style>
