const DEFAULT_MAX_UPLOAD_MB = 8
const DEFAULT_TARGET_MAX_MB = 5

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

function loadImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = dataUrl
  })
}

function canvasToBlob(canvas, mimeType, quality) {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), mimeType, quality)
  })
}

/**
 * 上传前处理图片：允许最大 8MB，超过 5MB 时尝试压缩到 5MB 以下
 */
export async function prepareLoveNestImage(
  file,
  { maxUploadMB = DEFAULT_MAX_UPLOAD_MB, targetMaxMB = DEFAULT_TARGET_MAX_MB } = {}
) {
  if (!file) {
    throw new Error('未选择图片')
  }

  const maxUploadBytes = maxUploadMB * 1024 * 1024
  const targetBytes = targetMaxMB * 1024 * 1024

  if (file.size > maxUploadBytes) {
    throw new Error(`图片不能超过 ${maxUploadMB}MB`)
  }

  if (file.size <= targetBytes) {
    return file
  }

  const dataUrl = await readFileAsDataUrl(file)
  const image = await loadImage(dataUrl)

  let width = image.width
  let height = image.height
  let quality = 0.88
  let blob = null
  const mimeType = file.type === 'image/png' ? 'image/jpeg' : (file.type || 'image/jpeg')

  for (let attempt = 0; attempt < 8; attempt += 1) {
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const ctx = canvas.getContext('2d')
    ctx.drawImage(image, 0, 0, width, height)
    blob = await canvasToBlob(canvas, mimeType, quality)

    if (blob && blob.size <= targetBytes) {
      break
    }

    quality = Math.max(0.45, quality - 0.08)
    width = Math.round(width * 0.9)
    height = Math.round(height * 0.9)
  }

  if (!blob) {
    throw new Error('图片压缩失败')
  }

  if (blob.size > maxUploadBytes) {
    throw new Error(`压缩后仍超过 ${maxUploadMB}MB，请换一张较小的图片`)
  }

  const ext = mimeType === 'image/png' ? '.png' : '.jpg'
  const baseName = (file.name || 'image').replace(/\.[^.]+$/, '')
  return new File([blob], `${baseName}${ext}`, { type: mimeType, lastModified: Date.now() })
}
