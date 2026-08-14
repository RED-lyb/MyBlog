export const GEO_DATAV_BASE = 'https://geo.datav.aliyun.com/areas_v3/bound'

export const PROVINCE_NAMES = {
  '110000': '北京',
  '120000': '天津',
  '130000': '河北',
  '140000': '山西',
  '150000': '内蒙古',
  '210000': '辽宁',
  '220000': '吉林',
  '230000': '黑龙江',
  '310000': '上海',
  '320000': '江苏',
  '330000': '浙江',
  '340000': '安徽',
  '350000': '福建',
  '360000': '江西',
  '370000': '山东',
  '410000': '河南',
  '420000': '湖北',
  '430000': '湖南',
  '440000': '广东',
  '450000': '广西',
  '460000': '海南',
  '500000': '重庆',
  '510000': '四川',
  '520000': '贵州',
  '530000': '云南',
  '540000': '西藏',
  '610000': '陕西',
  '620000': '甘肃',
  '630000': '青海',
  '640000': '宁夏',
  '650000': '新疆',
  '710000': '台湾',
  '810000': '香港',
  '820000': '澳门',
}

const geoCache = new Map()

function isTaiwanFeature(feature) {
  const code = String(feature?.properties?.adcode || '')
  const name = feature?.properties?.name || ''
  return code.startsWith('71') || name.includes('台湾')
}

function normalizeGeoJson(json) {
  if (json.type === 'Feature') {
    return { type: 'FeatureCollection', features: [json] }
  }
  if (json.features?.length) return json
  throw new Error('地图数据格式无效')
}

async function fetchTaiwanFeature() {
  const response = await fetch(`${GEO_DATAV_BASE}/710000.json`)
  if (!response.ok) return null
  const json = await response.json()
  if (json.type === 'FeatureCollection' && json.features?.length) {
    return json.features[0]
  }
  if (json.type === 'Feature') return json
  return null
}

async function ensureNationalGeoJson(geoJson) {
  if (geoJson.features.some(isTaiwanFeature)) {
    return geoJson
  }
  const taiwanFeature = await fetchTaiwanFeature()
  if (!taiwanFeature) return geoJson
  return {
    ...geoJson,
    features: [...geoJson.features, taiwanFeature],
  }
}

async function fetchGeoJsonRaw(adcode) {
  const key = String(adcode)
  let response = await fetch(`${GEO_DATAV_BASE}/${key}_full.json`)
  if (!response.ok) {
    response = await fetch(`${GEO_DATAV_BASE}/${key}.json`)
  }
  if (!response.ok) {
    throw new Error(`地图数据加载失败: ${key}`)
  }
  return normalizeGeoJson(await response.json())
}

export async function fetchGeoJson(adcode) {
  const key = String(adcode)
  if (geoCache.has(key)) {
    return geoCache.get(key)
  }
  let json = await fetchGeoJsonRaw(key)
  if (key === '100000') {
    json = await ensureNationalGeoJson(json)
  }
  geoCache.set(key, json)
  return json
}

export function normalizeProvinceAdcode(adcode) {
  const code = String(adcode || '')
  if (!code) return ''
  if (code.length === 6 && code.endsWith('0000')) return code
  if (code.length >= 2) return `${code.slice(0, 2)}0000`
  return code
}

function isValidAreaOption(item) {
  const adcode = String(item?.adcode || '').trim()
  const name = String(item?.name || '').trim()
  return Boolean(adcode && name)
}

export async function fetchProvinceOptions() {
  const geoJson = await fetchGeoJson('100000')
  return geoJson.features
    .map((feature) => ({
      adcode: String(feature.properties.adcode),
      name: feature.properties.name,
    }))
    .filter(isValidAreaOption)
    .sort((a, b) => a.adcode.localeCompare(b.adcode))
}

export async function fetchCityOptions(provinceAdcode) {
  const code = normalizeProvinceAdcode(provinceAdcode)
  if (!code) return []
  const geoJson = await fetchGeoJson(code)
  return geoJson.features
    .map((feature) => ({
      adcode: String(feature.properties.adcode),
      name: feature.properties.name,
    }))
    .filter(isValidAreaOption)
    .sort((a, b) => a.adcode.localeCompare(b.adcode))
}

function collectCoordinatePairs(coords, points = []) {
  if (!Array.isArray(coords) || !coords.length) return points
  if (typeof coords[0] === 'number') {
    points.push(coords)
    return points
  }
  coords.forEach((item) => collectCoordinatePairs(item, points))
  return points
}

export function getFeatureCentroid(feature) {
  const points = collectCoordinatePairs(feature?.geometry?.coordinates)
  if (!points.length) return null
  const lng = points.reduce((sum, point) => sum + point[0], 0) / points.length
  const lat = points.reduce((sum, point) => sum + point[1], 0) / points.length
  return [lng, lat]
}

export function findProvinceFeature(geoJson, provinceAdcode) {
  const provinceCode = normalizeProvinceAdcode(provinceAdcode)
  return (
    geoJson.features.find(
      (feature) => normalizeProvinceAdcode(feature.properties.adcode) === provinceCode
    ) || null
  )
}

const provinceCityCountCache = new Map()

export async function getProvinceCityCount(provinceAdcode) {
  const code = normalizeProvinceAdcode(provinceAdcode)
  if (!code) return 0
  if (provinceCityCountCache.has(code)) {
    return provinceCityCountCache.get(code)
  }
  const geoJson = await fetchGeoJson(code)
  const count = geoJson.features
    .map((feature) => ({
      adcode: String(feature.properties.adcode),
      name: feature.properties.name,
    }))
    .filter(isValidAreaOption).length
  provinceCityCountCache.set(code, count)
  return count
}

export async function buildProvinceMapData(provinceStats = {}) {
  const geoJson = await fetchGeoJson('100000')
  const provinces = geoJson.features.map((feature) => {
    const adcode = normalizeProvinceAdcode(feature.properties.adcode)
    return {
      name: feature.properties.name,
      adcode,
      visited: provinceStats[adcode] || 0,
    }
  })

  return Promise.all(
    provinces.map(async (province) => {
      const total = await getProvinceCityCount(province.adcode)
      const value = total > 0 ? province.visited / total : 0
      return {
        name: province.name,
        adcode: province.adcode,
        visited: province.visited,
        total,
        value,
      }
    })
  )
}

export function buildCityMapData(cities, geoJson, provinceAdcode) {
  const provinceCode = normalizeProvinceAdcode(provinceAdcode)
  const nameByAdcode = new Map(
    geoJson.features.map((feature) => [
      String(feature.properties.adcode),
      feature.properties.name,
    ])
  )

  return cities
    .filter((city) => normalizeProvinceAdcode(city.province_adcode) === provinceCode)
    .map((city) => ({
      name: nameByAdcode.get(String(city.adcode)) || city.city_name,
      value: 1,
      adcode: city.adcode,
      note: city.note,
      cover: city.photos?.[0]?.url || '',
    }))
}

export function findProvinceAdcodeByName(geoJson, name) {
  const feature = geoJson.features.find((item) => item.properties.name === name)
  return feature ? normalizeProvinceAdcode(feature.properties.adcode) : ''
}
