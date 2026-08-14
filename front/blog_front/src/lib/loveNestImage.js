const MAX_IMAGE_MB = 5

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

/** 上传前处理：单张不超过 5MB，超出则尝试压缩到 5MB 以内 */
export async function prepareLoveNestImage(file, { maxMB = MAX_IMAGE_MB } = {}) {
  if (!file) {
    throw new Error('未选择图片')
  }

  const maxBytes = maxMB * 1024 * 1024

  if (file.size <= maxBytes) {
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

    if (blob && blob.size <= maxBytes) {
      break
    }

    quality = Math.max(0.45, quality - 0.08)
    width = Math.round(width * 0.9)
    height = Math.round(height * 0.9)
  }

  if (!blob || blob.size > maxBytes) {
    throw new Error(`图片不能超过 ${maxMB}MB`)
  }

  const ext = mimeType === 'image/png' ? '.png' : '.jpg'
  const baseName = (file.name || 'image').replace(/\.[^.]+$/, '')
  return new File([blob], `${baseName}${ext}`, { type: mimeType, lastModified: Date.now() })
}
