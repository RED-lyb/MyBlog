import { ref } from 'vue'

/**
 * 漂浮背景的取图范围。
 * null：使用全部照片。
 * 数组：只使用当前省下城市的照片。
 */
export const floatPhotoSource = ref(null)
