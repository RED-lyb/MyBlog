/**
 * 嵌入 iframe：与主站隔离，禁止 allow-same-origin，避免嵌入脚本访问主站 cookie / storage。
 * @see https://developer.mozilla.org/docs/Web/HTML/Element/iframe#sandbox
 */
export const EMBED_IFRAME_SANDBOX = 'allow-scripts allow-pointer-lock allow-forms allow-popups'

function escapeHtmlAttr(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

/** 防止 width/height 中注入 style（如 100px;position:fixed） */
export function sanitizeEmbedBox(value) {
  const s = String(value || '').trim().slice(0, 32)
  if (/^\d+(\.\d+)?(px|%|rem|em|vh|vw)$/i.test(s)) return s
  if (/^\d+(\.\d+)?$/i.test(s)) return `${s}px`
  return '100%'
}

function embedHintHtml() {
  return '<p class="embed-iframe-hint" role="note">以下内容为用户嵌入，可能存在一定的安全风险，请勿输入帐号密码等敏感信息。</p>'
}

/**
 * @param {'url'|'html'} type
 * @param {string} payload url 或 base64 的 html 片段
 * @param {string} width
 * @param {string} height
 */
export function buildEmbedMarkup(type, payload, width, height) {
  const w = sanitizeEmbedBox(width)
  const h = sanitizeEmbedBox(height)
  const hint = embedHintHtml()

  if (type === 'url') {
    return `<div class="embed-iframe-container">${hint}<iframe
      sandbox="${EMBED_IFRAME_SANDBOX}"
      src="${escapeHtmlAttr(payload)}"
      style="width: ${escapeHtmlAttr(w)}; height: ${escapeHtmlAttr(h)}; border: none;"
      frameborder="0"
      scrolling="auto"
      class="embed-iframe"
      title="嵌入的外部页面"
      referrerpolicy="no-referrer-when-downgrade"
      allowfullscreen
    ></iframe></div>`
  }

  if (type === 'html') {
    try {
      const decodedHtml = decodeURIComponent(escape(atob(payload)))
      const srcdoc = escapeHtmlAttr(decodedHtml)
      return `<div class="embed-iframe-container">${hint}<iframe
      sandbox="${EMBED_IFRAME_SANDBOX}"
      style="width: ${escapeHtmlAttr(w)}; height: ${escapeHtmlAttr(h)}; border: none; overflow: hidden;"
      frameborder="0"
      scrolling="no"
      class="embed-iframe"
      title="用户嵌入的 HTML"
      srcdoc="${srcdoc}"
      allowfullscreen
    ></iframe></div>`
    } catch (e) {
      console.error('HTML解码失败:', e)
      return '<p class="embed-parse-error">嵌入内容解析失败</p>'
    }
  }

  return ''
}
