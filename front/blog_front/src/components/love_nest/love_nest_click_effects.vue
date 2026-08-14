<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const trailCanvasRef = ref(null)

const sparks = []
const SPARK_MAX = 84
const TRAIL_COLORS = ['#ffc2dd', '#ffb3d9', '#ff9ec8', '#fff0f6', '#f8a8c8']

let trailCtx = null
let rafId = 0
let lastSpawnX = 0
let lastSpawnY = 0

function isPreviewOverlay(target) {
  if (!(target instanceof Element)) return false
  return Boolean(target.closest('.el-image-viewer__wrapper, .el-overlay'))
}

function resizeCanvas() {
  const canvas = trailCanvasRef.value
  if (!canvas) return

  const dpr = window.devicePixelRatio || 1
  const width = window.innerWidth
  const height = window.innerHeight
  canvas.width = Math.floor(width * dpr)
  canvas.height = Math.floor(height * dpr)
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  trailCtx = canvas.getContext('2d')
  if (trailCtx) {
    trailCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
}

function randomColor() {
  return TRAIL_COLORS[Math.floor(Math.random() * TRAIL_COLORS.length)]
}

function pushSpark(spark) {
  sparks.push(spark)
  if (sparks.length > SPARK_MAX) {
    sparks.splice(0, sparks.length - SPARK_MAX)
  }
}

function spawnSpark(x, y, boost = 1) {
  const count = boost > 1 ? 12 : 2
  for (let i = 0; i < count; i += 1) {
    const angle = Math.random() * Math.PI * 2
    const speed = boost > 1 ? 1.2 + Math.random() * 2.8 : 0.4 + Math.random() * 1.0
    pushSpark({
      x: x + (Math.random() - 0.5) * 6,
      y: y + (Math.random() - 0.5) * 6,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      decay: 0.016 + Math.random() * 0.018,
      size: (2 + Math.random() * 3.5) * boost,
      rotation: Math.random() * Math.PI,
      spin: (Math.random() - 0.5) * 0.18,
      color: randomColor(),
    })
  }
}

function spawnClickBurst(x, y) {
  spawnSpark(x, y, 1.5)

  const tiers = [
    { count: 10, sizeMin: 3.2, sizeMax: 4.8, speedMin: 1.0, speedMax: 2.8 },
    { count: 18, sizeMin: 1.4, sizeMax: 2.6, speedMin: 2.2, speedMax: 4.8 },
  ]

  for (const tier of tiers) {
    for (let i = 0; i < tier.count; i += 1) {
      const angle = (Math.PI * 2 * i) / tier.count + (Math.random() - 0.5) * 0.55
      const speed = tier.speedMin + Math.random() * (tier.speedMax - tier.speedMin)
      const size = tier.sizeMin + Math.random() * (tier.sizeMax - tier.sizeMin)
      pushSpark({
        x: x + (Math.random() - 0.5) * 3,
        y: y + (Math.random() - 0.5) * 3,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1,
        decay: 0.012 + Math.random() * 0.01,
        size,
        rotation: Math.random() * Math.PI,
        spin: (Math.random() - 0.5) * 0.24,
        color: randomColor(),
      })
    }
  }
}

function drawStar(ctx, x, y, size, rotation, color, alpha) {
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(rotation)
  ctx.globalAlpha = alpha
  ctx.fillStyle = color
  ctx.beginPath()
  for (let i = 0; i < 4; i += 1) {
    const angle = (Math.PI / 2) * i
    const outerX = Math.cos(angle) * size
    const outerY = Math.sin(angle) * size
    const innerX = Math.cos(angle + Math.PI / 4) * (size * 0.35)
    const innerY = Math.sin(angle + Math.PI / 4) * (size * 0.35)
    if (i === 0) ctx.moveTo(outerX, outerY)
    else ctx.lineTo(outerX, outerY)
    ctx.lineTo(innerX, innerY)
  }
  ctx.closePath()
  ctx.fill()
  ctx.restore()
}

function drawSparks() {
  if (!trailCtx) {
    rafId = window.requestAnimationFrame(drawSparks)
    return
  }

  const width = window.innerWidth
  const height = window.innerHeight
  trailCtx.clearRect(0, 0, width, height)

  for (let i = sparks.length - 1; i >= 0; i -= 1) {
    const spark = sparks[i]
    spark.x += spark.vx
    spark.y += spark.vy
    spark.vx *= 0.98
    spark.vy *= 0.98
    spark.rotation += spark.spin
    spark.life -= spark.decay

    if (spark.life <= 0) {
      sparks.splice(i, 1)
      continue
    }

    const alpha = spark.life * 0.9
    trailCtx.shadowBlur = spark.size > 7 ? 14 : 10
    trailCtx.shadowColor = spark.size > 7 ? 'rgba(255, 140, 190, 0.78)' : 'rgba(255, 158, 200, 0.65)'
    drawStar(trailCtx, spark.x, spark.y, spark.size, spark.rotation, spark.color, alpha)
  }
  trailCtx.shadowBlur = 0

  rafId = window.requestAnimationFrame(drawSparks)
}

function fireClickBurst(event) {
  spawnClickBurst(event.clientX, event.clientY)
}

function onPointerDown(event) {
  if (event.button !== 0) return
  if (isPreviewOverlay(event.target)) return
  fireClickBurst(event)
}

function onPointerMove(event) {
  const dx = event.clientX - lastSpawnX
  const dy = event.clientY - lastSpawnY
  if (dx * dx + dy * dy < 36) return

  lastSpawnX = event.clientX
  lastSpawnY = event.clientY
  spawnSpark(event.clientX, event.clientY)
}

function onWindowResize() {
  resizeCanvas()
}

onMounted(() => {
  resizeCanvas()
  window.addEventListener('pointerdown', onPointerDown, { passive: true })
  window.addEventListener('pointermove', onPointerMove, { passive: true })
  window.addEventListener('resize', onWindowResize)
  rafId = window.requestAnimationFrame(drawSparks)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointerdown', onPointerDown)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('resize', onWindowResize)
  if (rafId) window.cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="ln-click-effects" aria-hidden="true">
    <canvas ref="trailCanvasRef" class="ln-click-effects__trail" />
  </div>
</template>

<style scoped>
.ln-click-effects {
  position: fixed;
  inset: 0;
  z-index: 55;
  pointer-events: none;
}

.ln-click-effects__trail {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
