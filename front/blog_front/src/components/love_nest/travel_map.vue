<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { resolveStaticUrl } from '../../lib/loveNestApi.js'
import {
  PROVINCE_NAMES,
  buildProvinceMapData,
  buildCityMapData,
  fetchGeoJson,
  findProvinceAdcodeByName,
  findProvinceFeature,
  getFeatureCentroid,
  normalizeProvinceAdcode,
} from '../../lib/loveNestMap.js'

const props = defineProps({
  cities: {
    type: Array,
    default: () => [],
  },
  provinceStats: {
    type: Object,
    default: () => ({}),
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const NATIONAL_ZOOM = 1
const PROVINCE_ZOOM = 0.85
const ZOOM_IN_TO_PROVINCE = 10
const ZOOM_OUT_TO_NATION = 0.82
const DRILL_FADE_MS = 100
const DRILL_ANIM_MS = 240
const NATIONAL_LAYOUT_CENTER = ['50%', '56%']
const DEFAULT_LAYOUT_CENTER = ['50%', '50%']
const COMPACT_PROVINCE_CODES = new Set(['810000', '820000'])
const DRILL_LAYOUT_OFFSET_X = 0.1
const DRILL_LAYOUT_OFFSET_Y = 0.08

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function getNationalLayoutCenter() {
  const { width, height } = getViewportSize()
  if (!height) return NATIONAL_LAYOUT_CENTER

  const isMobile = width <= 720

  if (isMobile) {
    const yPercent = clamp(48 + (height / 820) * 3, 48, 51)
    return ['50%', `${yPercent.toFixed(1)}%`]
  }

  const tallHeight = 900
  const shortHeight = 720
  const yAtTall = 63
  const yAtShort = 54

  let yPercent
  if (height >= tallHeight) {
    yPercent = yAtTall
  } else if (height <= shortHeight) {
    yPercent = yAtShort
  } else {
    const ratio = (height - shortHeight) / (tallHeight - shortHeight)
    yPercent = yAtShort + (yAtTall - yAtShort) * ratio
  }

  return ['50%', `${yPercent.toFixed(1)}%`]
}

function buildDrillLayoutCenter() {
  const dx = clamp(lastPointer.x - 0.5, -DRILL_LAYOUT_OFFSET_X, DRILL_LAYOUT_OFFSET_X)
  const dy = clamp(lastPointer.y - 0.5, -DRILL_LAYOUT_OFFSET_Y, DRILL_LAYOUT_OFFSET_Y)
  return [`${((0.5 + dx) * 100).toFixed(1)}%`, `${((0.5 + dy) * 100).toFixed(1)}%`]
}

const chartRef = ref(null)
const mapReady = ref(false)
const mapError = ref('')
const mapDrilling = ref(false)
const activeProvince = ref('')
const selectedCityAdcode = ref('')
const drillAdcode = ref('100000')
const listCollapsed = ref(false)
const hoveredProvinceAdcode = ref('')
const previewOpen = ref(false)
const isMobileList = ref(false)

let chartInstance = null
let resizeObserver = null
let renderToken = 0
let isDrillSwitching = false
let geoRoamTimer = null
let lastGeoZoom = null
let lastPointer = { x: 0.5, y: 0.5 }
let drillFocus = null

const isNationalView = computed(() => drillAdcode.value === '100000')
const visitedCount = computed(() => props.cities.length)
const provinceCount = computed(() => Object.keys(props.provinceStats).length)

const selectedCity = computed(() =>
  props.cities.find((city) => city.adcode === selectedCityAdcode.value) || null
)

const visibleCities = computed(() => {
  if (selectedCity.value) return [selectedCity.value]
  if (activeProvince.value && !isNationalView.value) {
    return props.cities.filter(
      (city) => normalizeProvinceAdcode(city.province_adcode) === activeProvince.value
    )
  }
  return props.cities
})

const listTitle = computed(() => {
  if (selectedCity.value) return selectedCity.value.city_name
  if (!isNationalView.value) return PROVINCE_NAMES[activeProvince.value] || '已访城市'
  return '全部城市'
})

const listMeta = computed(() => {
  if (selectedCity.value) return ''
  if (!isNationalView.value) {
    return `已访 ${visibleCities.value.length} 城`
  }
  return `已访 ${visitedCount.value} 城 · ${provinceCount.value} 省`
})

const cityPreviewList = computed(() => {
  const photos = selectedCity.value?.photos || []
  return photos.map((photo) => photoUrl(photo))
})

const toggleIcon = computed(() => {
  if (isMobileList.value) {
    return listCollapsed.value ? ArrowUp : ArrowDown
  }
  return listCollapsed.value ? ArrowRight : ArrowLeft
})

function escapeHtml(text) {
  return String(text ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function photoUrl(photo) {
  return photo ? resolveStaticUrl(photo.url) : ''
}

function previewIndex(photo) {
  const photos = selectedCity.value?.photos || []
  return photos.findIndex((item) => item.id === photo.id)
}

function getSeriesZoom() {
  const option = chartInstance?.getOption()
  return option?.series?.[0]?.zoom ?? 1
}

function syncGeoZoomBaseline() {
  lastGeoZoom = getSeriesZoom()
}

function getViewportSize() {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  }
}

function getChartPointer(event) {
  const el = chartRef.value
  if (!el) return null
  const rect = el.getBoundingClientRect()
  if (!rect.width || !rect.height) return null
  const px = event.clientX - rect.left
  const py = event.clientY - rect.top
  return {
    x: px / rect.width,
    y: py / rect.height,
    px,
    py,
  }
}

function updateLastPointer(event) {
  const pointer = getChartPointer(event)
  if (pointer) {
    lastPointer = { x: pointer.x, y: pointer.y }
  }
}

async function captureDrillFocus(targetAdcode) {
  const provinceCode = normalizeProvinceAdcode(targetAdcode)
  const nationalGeo = await fetchGeoJson('100000')
  const feature = findProvinceFeature(nationalGeo, provinceCode)
  const centroid = feature ? getFeatureCentroid(feature) : null

  if (COMPACT_PROVINCE_CODES.has(provinceCode)) {
    drillFocus = {
      layoutCenter: [...DEFAULT_LAYOUT_CENTER],
      center: centroid || undefined,
    }
    return
  }

  drillFocus = {
    layoutCenter: buildDrillLayoutCenter(),
    center: centroid || undefined,
  }
}

function resolveLayoutCenter(isNational) {
  if (!isNational && drillFocus?.layoutCenter) {
    return drillFocus.layoutCenter
  }
  return isNational ? getNationalLayoutCenter() : DEFAULT_LAYOUT_CENTER
}

function resolveMapCenter(isNational) {
  if (!isNational && drillFocus?.center) {
    return drillFocus.center
  }
  return undefined
}

function resizeChart() {
  if (!chartInstance) return
  const { width, height } = getViewportSize()
  chartInstance.resize({ width, height })
}

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

function setMapRoam(enabled) {
  if (!chartInstance) return
  chartInstance.setOption({
    series: [{ roam: enabled }],
  })
}

async function animateMapView(isNational) {
  if (!chartInstance) return
  const targetZoom = isNational ? NATIONAL_ZOOM : PROVINCE_ZOOM
  const layoutCenter = resolveLayoutCenter(isNational)
  const center = resolveMapCenter(isNational)
  chartInstance.setOption({
    animation: true,
    animationDurationUpdate: DRILL_ANIM_MS,
    animationEasingUpdate: 'cubicInOut',
    series: [
      {
        zoom: targetZoom,
        center: isNational ? undefined : center,
        layoutCenter,
        layoutSize: '100%',
      },
    ],
  })
  resizeChart()
  await delay(DRILL_ANIM_MS)
}

async function runDrillSwitch({ adcode, province, clearHover = false, usePointerFocus = false }) {
  if (isDrillSwitching) return

  const prevDrill = drillAdcode.value
  const prevProvince = activeProvince.value
  isDrillSwitching = true
  setMapRoam(false)
  mapDrilling.value = true
  await delay(DRILL_FADE_MS)

  if (adcode === '100000') {
    drillFocus = null
  } else if (usePointerFocus) {
    await captureDrillFocus(adcode)
  } else {
    drillFocus = null
  }

  if (province !== undefined) activeProvince.value = province
  drillAdcode.value = adcode
  clearCitySelection()
  if (clearHover) hoveredProvinceAdcode.value = ''
  lastGeoZoom = null
  mapError.value = ''

  const ok = await renderMap({ roamEnabled: false, transition: true })
  if (!ok) {
    activeProvince.value = prevProvince
    drillAdcode.value = prevDrill
    mapDrilling.value = false
    setMapRoam(true)
    isDrillSwitching = false
    return
  }

  await animateMapView(adcode === '100000')
  mapDrilling.value = false
  await delay(60)
  setMapRoam(true)
  isDrillSwitching = false
  syncGeoZoomBaseline()
}

const PROVINCE_LABEL_OFFSETS = {
  '130000': [-12, 16],
  河北省: [-12, 16],
}

function applyProvinceLabelOffsets(mapData) {
  return mapData.map((item) => {
    const offset = PROVINCE_LABEL_OFFSETS[item.adcode] || PROVINCE_LABEL_OFFSETS[item.name]
    if (!offset) return item
    return {
      ...item,
      label: { offset },
    }
  })
}

function buildMapOption(mapName, mapData, isNational, roamEnabled = true, options = {}) {
  const { transition = false, initialZoom, layoutCenter, center } = options
  const maxValue = isNational
    ? 1
    : Math.max(1, ...mapData.map((item) => item.value || 0))
  const baseZoom = isNational ? NATIONAL_ZOOM : PROVINCE_ZOOM
  const zoom = initialZoom ?? baseZoom
  const resolvedLayoutCenter = layoutCenter ?? resolveLayoutCenter(isNational)
  const resolvedCenter = center ?? resolveMapCenter(isNational)

  return {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: transition ? 0 : 320,
    animationDurationUpdate: DRILL_ANIM_MS,
    animationEasing: 'cubicOut',
    animationEasingUpdate: 'cubicInOut',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#111' },
      formatter(params) {
        const data = params.data || {}
        const name = escapeHtml(params.name)
        if (data.cover) {
          const note = data.note ? `<div style="margin-top:6px;max-width:220px;">${escapeHtml(data.note)}</div>` : ''
          const cover = escapeHtml(resolveStaticUrl(data.cover))
          return [
            `<strong>${name}</strong>`,
            note,
            `<img src="${cover}" style="width:120px;height:80px;object-fit:cover;margin-top:8px;border-radius:4px;" />`,
          ].join('')
        }
        if (!isNational) {
          if (data.adcode) {
            const note = data.note
              ? `<div style="margin-top:6px;max-width:220px;">${escapeHtml(data.note)}</div>`
              : ''
            return [`<strong>${name}</strong>`, note || '<br/>已到访'].join('')
          }
          return `${name}<br/>暂未前往`
        }
        if (data.visited > 0 && data.total) {
          const percent = Math.round((data.visited / data.total) * 100)
          return `${name}<br/>已访 ${data.visited}/${data.total} 城（${percent}%）`
        }
        return `${name}<br/>暂未前往`
      },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 12,
      inRange: {
        color: ['#e8ddd4', '#ddb8c0', '#8f3d4a'],
      },
      text: isNational ? ['高', '低'] : ['多', '少'],
      textStyle: { color: '#7d6e72' },
    },
    series: [
      {
        type: 'map',
        map: mapName,
        roam: roamEnabled,
        scaleLimit: { min: 0.75, max: 12 },
        zoom,
        center: resolvedCenter,
        layoutCenter: resolvedLayoutCenter,
        layoutSize: '100%',
        label: {
          show: true,
          color: '#4a3d40',
          fontSize: isNational ? 9 : 10,
        },
        itemStyle: {
          borderColor: 'rgba(100, 82, 76, 0.42)',
          borderWidth: 0.6,
          areaColor: 'rgba(224, 212, 200, 0.78)',
        },
        emphasis: {
          itemStyle: {
            areaColor: '#faf0d4',
            borderColor: 'rgba(120, 100, 60, 0.45)',
            borderWidth: 0.8,
          },
          label: {
            color: '#111',
            fontSize: isNational ? 10 : 11,
          },
        },
        data: mapData,
      },
    ],
  }
}

function bindMapEvents(geoJson, isNational) {
  chartInstance.off('click')
  chartInstance.off('mouseover')
  chartInstance.off('georoam')

  chartInstance.on('mouseover', (params) => {
    if (isNational) {
      const data = params.data || {}
      const adcode = data.adcode || findProvinceAdcodeByName(geoJson, params.name)
      if (adcode) hoveredProvinceAdcode.value = adcode
    }
  })

  chartInstance.on('click', (params) => {
    const data = params.data || {}
    if (isNational) {
      const adcode = data.adcode || findProvinceAdcodeByName(geoJson, params.name)
      if (adcode) drillToProvince(adcode)
      return
    }
    if (data.adcode) {
      selectCity(data.adcode)
      const city = props.cities.find((item) => item.adcode === data.adcode)
      if (city) activeProvince.value = normalizeProvinceAdcode(city.province_adcode)
    }
  })

  chartInstance.on('georoam', () => {
    if (isDrillSwitching) return
    clearTimeout(geoRoamTimer)
    geoRoamTimer = setTimeout(() => {
      handleGeoRoam()
    }, 150)
  })
}

function selectCity(adcode) {
  selectedCityAdcode.value = adcode
}

function clearCitySelection() {
  selectedCityAdcode.value = ''
}

async function drillToProvince(adcode, { usePointerFocus = false } = {}) {
  if (!adcode || drillAdcode.value === adcode || isDrillSwitching) return
  await runDrillSwitch({ adcode, province: adcode, usePointerFocus })
}

async function drillToNational() {
  if (drillAdcode.value === '100000' || isDrillSwitching) return
  await runDrillSwitch({ adcode: '100000', province: '', clearHover: true })
}

function handleGeoRoam() {
  if (!chartInstance || isDrillSwitching) return

  const zoom = getSeriesZoom()
  if (lastGeoZoom !== null && Math.abs(zoom - lastGeoZoom) < 0.04) {
    return
  }

  const isNational = drillAdcode.value === '100000'

  if (isNational && zoom >= ZOOM_IN_TO_PROVINCE) {
    const adcode = hoveredProvinceAdcode.value || activeProvince.value
    if (adcode) {
      drillToProvince(adcode, { usePointerFocus: true })
      return
    }
  }

  if (!isNational && zoom <= ZOOM_OUT_TO_NATION) {
    drillToNational()
    return
  }

  lastGeoZoom = zoom
}

async function renderMap({ roamEnabled = true, transition = false } = {}) {
  const token = ++renderToken
  mapError.value = ''

  await nextTick()
  if (!chartRef.value) return false

  try {
    const geoJson = await fetchGeoJson(drillAdcode.value)
    if (token !== renderToken) return false

    const mapName = `map_${drillAdcode.value}`
    echarts.registerMap(mapName, geoJson)

    if (!chartInstance) {
      chartInstance = echarts.init(chartRef.value)
    }

    const isNational = drillAdcode.value === '100000'
    let mapData = isNational
      ? await buildProvinceMapData(props.provinceStats)
      : buildCityMapData(props.cities, geoJson, drillAdcode.value)

    if (isNational) {
      mapData = applyProvinceLabelOffsets(mapData)
    }

    mapData.forEach((item) => {
      if (item.cover) item.cover = resolveStaticUrl(item.cover)
    })

    if (token !== renderToken) return false

    const baseZoom = isNational ? NATIONAL_ZOOM : PROVINCE_ZOOM
    const initialZoom = transition
      ? (isNational ? baseZoom * 1.05 : baseZoom * 0.88)
      : undefined
    const layoutCenter = resolveLayoutCenter(isNational)
    const center = resolveMapCenter(isNational)

    chartInstance.setOption(
      buildMapOption(mapName, mapData, isNational, roamEnabled, {
        transition,
        initialZoom,
        layoutCenter,
        center,
      }),
      {
        notMerge: true,
      }
    )

    bindMapEvents(geoJson, isNational)

    await nextTick()
    resizeChart()
    if (!isDrillSwitching) {
      syncGeoZoomBaseline()
    }
    mapReady.value = true
    return true
  } catch (error) {
    if (token !== renderToken) return false
    mapError.value = error.message || '地图加载失败'
    mapReady.value = false
    return false
  }
}

async function scheduleRenderMap() {
  if (props.loading) return
  await renderMap()
}

function toggleListCollapsed() {
  listCollapsed.value = !listCollapsed.value
}

function onCityCardClick(city) {
  selectCity(city.adcode)
  if (!activeProvince.value) {
    activeProvince.value = normalizeProvinceAdcode(city.province_adcode)
  }
}

function onPreviewShow() {
  previewOpen.value = true
  document.body.style.overflow = 'hidden'
}

function onPreviewClose() {
  previewOpen.value = false
  document.body.style.overflow = ''
}

function preventPageScroll(event) {
  event.preventDefault()
}

function onWindowResize() {
  updateMobileList()
  resizeChart()
  if (chartInstance && drillAdcode.value === '100000' && !isDrillSwitching) {
    chartInstance.setOption({
      series: [
        {
          layoutCenter: getNationalLayoutCenter(),
          center: undefined,
        },
      ],
    })
  }
}

function updateMobileList() {
  isMobileList.value = window.matchMedia('(max-width: 720px)').matches
}

watch(
  () => [props.cities, props.provinceStats, props.loading],
  () => {
    scheduleRenderMap()
  },
  { deep: true, flush: 'post' }
)

onMounted(async () => {
  updateMobileList()
  await nextTick()
  scheduleRenderMap()
  const chartHost = chartRef.value?.parentElement
  chartHost?.addEventListener('wheel', preventPageScroll, { passive: false })
  chartHost?.addEventListener('mousemove', updateLastPointer)
  window.addEventListener('resize', onWindowResize)
  if (chartHost && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      resizeChart()
    })
    resizeObserver.observe(chartHost)
  }
  window.addEventListener('orientationchange', onWindowResize)
})

onBeforeUnmount(() => {
  clearTimeout(geoRoamTimer)
  chartRef.value?.parentElement?.removeEventListener('wheel', preventPageScroll)
  chartRef.value?.parentElement?.removeEventListener('mousemove', updateLastPointer)
  window.removeEventListener('resize', onWindowResize)
  window.removeEventListener('orientationchange', onWindowResize)
  if (previewOpen.value) {
    document.body.style.overflow = ''
  }
  renderToken += 1
  resizeObserver?.disconnect()
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<template>
  <section class="travel-map">
    <div
      class="travel-map__chart-host"
      :class="{
        'is-ready': mapReady && !loading,
        'is-drilling': mapDrilling,
      }"
    >
      <div ref="chartRef" class="travel-map__chart-inner" />
    </div>

    <div class="travel-map__stage">
      <div v-if="loading" class="travel-map__loading">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="mapError" class="travel-map__overlay travel-map__error">
        <p class="ln-empty-hint">{{ mapError }}</p>
      </div>

      <aside class="travel-map__list" :class="{ 'is-hidden': listCollapsed, 'is-mobile': isMobileList }">
        <div class="travel-map__list-body">
          <div class="travel-map__list-head">
            <h3 class="travel-map__list-title">{{ listTitle }}</h3>
            <p v-if="listMeta" class="travel-map__meta ln-meta">{{ listMeta }}</p>
            <button
              v-if="selectedCity"
              type="button"
              class="travel-map__back-city"
              @click="clearCitySelection"
            >
              返回列表
            </button>
          </div>

          <template v-if="selectedCity">
            <p v-if="selectedCity.visited_at" class="travel-city-card__date">
              {{ selectedCity.visited_at }}
            </p>
            <p v-if="selectedCity.note" class="travel-city-card__note">{{ selectedCity.note }}</p>

            <p v-if="!selectedCity.photos?.length" class="ln-empty-hint">暂无照片</p>

            <div v-else class="travel-city-photos">
              <el-image
                v-for="photo in selectedCity.photos"
                :key="photo.id"
                class="travel-city-photos__item"
                :src="photoUrl(photo)"
                :preview-src-list="cityPreviewList"
                :initial-index="previewIndex(photo)"
                preview-teleported
                fit="cover"
                :alt="photo.title || selectedCity.city_name"
                @show="onPreviewShow"
                @close="onPreviewClose"
              />
            </div>
          </template>

          <template v-else>
            <p v-if="!visibleCities.length" class="ln-empty-hint">还没有旅行记录</p>

            <article
              v-for="city in visibleCities"
              :key="city.id"
              class="travel-city-card"
              :class="{ 'is-active': selectedCityAdcode === city.adcode }"
              @click="onCityCardClick(city)"
            >
              <img
                v-if="photoUrl(city.photos?.[0])"
                :src="photoUrl(city.photos[0])"
                :alt="city.city_name"
                class="travel-city-card__cover"
              />
              <div class="travel-city-card__body">
                <h4>{{ city.city_name }}</h4>
                <p v-if="city.visited_at" class="travel-city-card__date">{{ city.visited_at }}</p>
                <p v-if="city.note" class="travel-city-card__note">{{ city.note }}</p>
                <p v-if="city.photos?.length" class="travel-city-card__photos-count">
                  {{ city.photos.length }} 张照片
                </p>
              </div>
            </article>
          </template>
        </div>

        <button
          type="button"
          class="travel-map__list-toggle"
          :aria-label="listCollapsed ? '展开城市列表' : '收起城市列表'"
          @click="toggleListCollapsed"
        >
          <el-icon>
            <component :is="toggleIcon" />
          </el-icon>
        </button>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.travel-map {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.travel-map__chart-host {
  position: fixed;
  inset: 0;
  z-index: 20;
  width: 100%;
  height: 100%;
  pointer-events: auto;
  touch-action: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.travel-map__chart-host.is-ready {
  opacity: 1;
}

.travel-map__chart-inner {
  width: 100%;
  height: 100%;
  transition:
    opacity 0.2s ease,
    transform 0.48s cubic-bezier(0.22, 1, 0.36, 1);
  transform-origin: center center;
}

.travel-map__chart-host.is-drilling .travel-map__chart-inner {
  opacity: 0.2;
  transform: scale(0.97);
}

.travel-map__stage {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  pointer-events: none;
}

.travel-map__loading,
.travel-map__overlay {
  position: fixed;
  inset: 0;
  z-index: 48;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
  pointer-events: none;
}

.travel-map__error {
  pointer-events: auto;
}

.travel-map__list {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 51;
  display: flex;
  align-items: stretch;
  max-width: min(332px, 92vw);
  transform: translateX(0);
  transition: transform 0.28s ease;
  pointer-events: auto;
}

.travel-map__list.is-hidden {
  transform: translateX(calc(-100% + 32px));
}

.travel-map__list-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  padding: 14px;
  box-sizing: border-box;
  border-radius: 0 12px 12px 0;
  background: rgba(255, 252, 249, 0.9);
  backdrop-filter: blur(10px);
  overflow-y: auto;
}

.travel-map__list-toggle {
  flex-shrink: 0;
  align-self: center;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 64px;
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 0 10px 10px 0;
  background: rgba(255, 252, 249, 0.94);
  color: var(--ln-ink);
  box-shadow: 2px 0 10px rgba(17, 17, 17, 0.1);
  cursor: pointer;
}

.travel-map__list-head {
  flex-shrink: 0;
  padding-left: 0;
}

.travel-map__list-title {
  margin: 0;
  font-family: var(--ln-font-serif);
  font-size: 1.05rem;
  color: var(--ln-ink);
}

.travel-map__meta {
  margin: 6px 0 0;
}

.travel-map__back-city {
  margin-top: 8px;
  padding: 0;
  border: none;
  background: none;
  color: var(--ln-muted);
  font-size: 0.82rem;
  cursor: pointer;
  text-decoration: underline;
}

.travel-city-card {
  display: flex;
  gap: 12px;
  padding: 6px 4px;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: background 0.2s ease;
}

.travel-city-card:hover,
.travel-city-card.is-active {
  background: rgba(221, 184, 192, 0.22);
}

.travel-city-card__cover {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.travel-city-card__body h4 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--ln-ink);
}

.travel-map__list-body > .travel-city-card__date,
.travel-map__list-body > .travel-city-card__note {
  margin: 4px 0 0;
  font-size: 0.82rem;
  color: var(--ln-muted);
  line-height: 1.5;
}

.travel-city-card__date,
.travel-city-card__note,
.travel-city-card__photos-count {
  margin: 4px 0 0;
  font-size: 0.82rem;
  color: var(--ln-muted);
  line-height: 1.5;
}

.travel-city-photos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.travel-city-photos__item {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  cursor: zoom-in;
}

.travel-city-photos__item :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 720px) {
  .travel-map__list.is-mobile {
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    max-width: none;
    width: 100%;
    max-height: 46%;
    flex-direction: column-reverse;
  }

  .travel-map__list.is-mobile.is-hidden {
    transform: translateY(calc(100% - 36px));
  }

  .travel-map__list.is-mobile .travel-map__list-body {
    border-radius: 12px 12px 0 0;
    padding: 12px 12px 8px;
    max-height: 100%;
  }

  .travel-map__list.is-mobile .travel-map__list-toggle {
    align-self: center;
    width: 56px;
    height: 36px;
    border-radius: 10px 10px 0 0;
    box-shadow: 0 -2px 10px rgba(17, 17, 17, 0.1);
  }
}
</style>
