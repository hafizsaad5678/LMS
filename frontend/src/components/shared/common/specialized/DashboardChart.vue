<template>
  <div class="card h-100 border-0 shadow-sm dashboard-chart-card">
    <!-- Header -->
    <div class="card-header bg-transparent border-0 d-flex justify-content-between align-items-center pt-4 px-4 pb-0">
      <div class="d-flex align-items-center gap-2 flex-wrap">
        <h6 class="mb-0 chart-title">{{ title }}</h6>
        <span v-if="refreshInterval > 0" class="live-badge">
          <span class="live-dot"></span>LIVE
        </span>
      </div>
      <div class="d-flex align-items-center gap-3">
        <slot name="header-actions"></slot>
        <span v-if="lastUpdated" class="updated-text">{{ lastUpdatedText }}</span>
        <button v-if="refreshInterval > 0" class="btn-refresh" :class="{ spinning: isRefreshing }" @click="triggerRefresh" title="Refresh">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body px-4 pb-4 pt-3 position-relative" style="min-height: 290px;">
      <!-- Loading overlay -->
      <div v-if="loading || isRefreshing" class="chart-overlay" :class="{ soft: isRefreshing && !loading }">
        <div class="spinner-border spinner-border-sm text-primary"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="isEmpty" class="empty-state">
        <i class="bi bi-bar-chart-line"></i>
        <span>No data available yet</span>
      </div>

      <!-- Chart Canvas -->
      <div v-show="!loading && !isEmpty" style="position: relative; height: 260px;">
        <canvas ref="canvasRef"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  title:           { type: String, required: true },
  type:            { type: String, default: 'bar' },
  chartData:       { type: Object, required: true },
  options:         { type: Object, default: () => ({}) },
  loading:         { type: Boolean, default: false },
  refreshInterval: { type: Number, default: 30000 },
})

const emit = defineEmits(['refresh'])

const canvasRef   = ref(null)
const isRefreshing = ref(false)
const lastUpdated  = ref(null)
let chartInstance  = null
let pollingTimer   = null

// ─── Computed ──────────────────────────────────────────────────────────────
const isEmpty = computed(() => {
  if (!props.chartData) return true
  const labels   = props.chartData.labels || []
  const datasets = props.chartData.datasets || []
  return labels.length === 0 || datasets.length === 0 ||
    datasets.every(ds => !ds.data || ds.data.length === 0)
})

const lastUpdatedText = computed(() => {
  if (!lastUpdated.value) return ''
  const s = Math.floor((Date.now() - lastUpdated.value) / 1000)
  if (s < 10)  return 'just now'
  if (s < 60)  return `${s}s ago`
  return `${Math.floor(s / 60)}m ago`
})

// ─── Gradient helper ────────────────────────────────────────────────────────
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `${r}, ${g}, ${b}`
}

function makeGradient(ctx, height, color, alphaTop = 0.28, alphaBot = 0.0) {
  const g = ctx.createLinearGradient(0, 0, 0, height)
  const rgb = color.startsWith('#') ? hexToRgb(color) : color
  g.addColorStop(0, `rgba(${rgb}, ${alphaTop})`)
  g.addColorStop(1, `rgba(${rgb}, ${alphaBot})`)
  return g
}

// ─── Bar colour helper (multi-colour bars) ──────────────────────────────────
function makeBarGradients(ctx, height, colors) {
  return colors.map(c => {
    const g = ctx.createLinearGradient(0, 0, 0, height)
    const rgb = c.startsWith('#') ? hexToRgb(c) : c
    g.addColorStop(0, `rgba(${rgb}, 0.90)`)
    g.addColorStop(1, `rgba(${rgb}, 0.55)`)
    return g
  })
}

// ─── Chart init ─────────────────────────────────────────────────────────────
const PALETTE = ['#6366f1','#10b981','#f59e0b','#3b82f6','#ec4899','#8b5cf6','#06b6d4','#f97316']

// Custom plugin to draw percentage/total in center of doughnut
const centerTextPlugin = {
  id: 'centerText',
  beforeDraw(chart) {
    if (chart.config.type !== 'doughnut') return
    const { ctx } = chart
    const meta = chart.getDatasetMeta(0)
    if (!meta || !meta.data || meta.data.length === 0) return
    
    const x = meta.data[0].x
    const y = meta.data[0].y
    if (x == null || y == null) return

    ctx.save()
    const activeElements = chart.getActiveElements()
    let text = ''
    let label = ''
    
    const dataset = chart.data.datasets[0]
    const total = dataset.data.reduce((a, b) => a + b, 0)

    if (activeElements.length > 0) {
      const activeIndex = activeElements[0].index
      const value = dataset.data[activeIndex]
      const percentage = total > 0 ? ((value / total) * 100).toFixed(0) : 0
      text = `${percentage}%`
      label = chart.data.labels[activeIndex]
    } else {
      text = total.toLocaleString()
      label = 'Total'
    }
    
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    
    // Draw Value (Percentage/Total)
    ctx.font = 'bold 24px Outfit, Inter, system-ui'
    ctx.fillStyle = '#1e293b'
    ctx.fillText(text, x, y - 8)
    
    // Draw Label (Submitted/Pending/Total)
    ctx.font = '600 11px Outfit, Inter, system-ui'
    ctx.fillStyle = '#64748b'
    ctx.fillText(label, x, y + 14)
    
    ctx.restore()
  }
}

const initChart = () => {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
  if (isEmpty.value || !canvasRef.value) return

  const ctx    = canvasRef.value.getContext('2d')
  const h      = canvasRef.value.offsetHeight || 260
  const isDonut = props.type === 'doughnut' || props.type === 'pie'
  const isLine  = props.type === 'line'
  const isBar   = props.type === 'bar'
  const isHoriz = props.options?.indexAxis === 'y'

  // Process datasets — auto gradients / colours
  const processedDatasets = props.chartData.datasets.map((ds, dsi) => {
    const base = { ...ds }
    const color = ds.borderColor || ds.backgroundColor || PALETTE[dsi % PALETTE.length]
    const solidColor = (typeof color === 'string' && color.startsWith('#')) ? color : PALETTE[dsi % PALETTE.length]

    if (isLine && ds.fill) {
      base.backgroundColor = makeGradient(ctx, h, solidColor, 0.25, 0.0)
      base.pointBackgroundColor  = solidColor
      base.pointBorderColor      = '#fff'
      base.pointBorderWidth      = 2
      base.pointRadius           = 4
      base.pointHoverRadius      = 7
      base.pointHoverBackgroundColor = solidColor
    }

    if (isBar) {
      // Multi-color bars per index when single dataset & no borderColor
      if (!ds.borderColor && props.chartData.labels?.length) {
        const colors = props.chartData.labels.map((_, i) => PALETTE[i % PALETTE.length])
        base.backgroundColor = makeBarGradients(ctx, h, colors)
        base.borderRadius    = { topLeft: 6, topRight: 6 }
        base.borderSkipped   = false
      } else {
        // Gradient for single-color bar
        base.backgroundColor = makeGradient(ctx, h, solidColor, 0.88, 0.55)
        base.borderRadius    = { topLeft: 6, topRight: 6 }
        base.borderSkipped   = false
      }
      base.minBarLength = 0
    }

    if (isDonut) {
      if (!ds.borderWidth) base.borderWidth = 0
      base.hoverOffset = 12
      // Default to palette if no colors set
      if (!Array.isArray(ds.backgroundColor)) {
        base.backgroundColor = PALETTE.slice(0, (ds.data || []).length)
      }
      base.cutout = '70%' // Ensure center is spacious for text plugin
    }

    return base
  })

  // Tooltip config
  const tooltipConfig = {
    enabled:    true,
    mode:       isDonut ? 'nearest' : 'index',
    intersect:  isDonut,
    padding:    { top: 10, bottom: 10, left: 14, right: 14 },
    backgroundColor:  'rgba(15, 23, 42, 0.95)',
    titleColor:       '#f1f5f9',
    bodyColor:        '#ffffff',
    borderColor:      'rgba(99, 102, 241, 0.35)',
    borderWidth:      1,
    titleFont:  { family: 'Outfit, Inter, system-ui', size: 12, weight: 'bold' },
    bodyFont:   { family: 'Outfit, Inter, system-ui', size: 12 },
    footerFont: { family: 'Outfit, Inter, system-ui', size: 10 },
    footerColor:'#64748b',
    cornerRadius: 8,
    caretSize:    5,
    displayColors: true,
    boxPadding:    4,
    callbacks: {
      label(ctx) {
        const v = ctx.parsed?.y ?? ctx.parsed ?? 0
        const label = ctx.dataset.label || ctx.label || ''
        if (isDonut) {
          const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
          const pct = total > 0 ? ((v / total) * 100).toFixed(1) : 0
          return `  ${label}: ${v}  (${pct}%)`
        }
        const unit = (ctx.dataset.label || '').includes('%') ? '%' : ''
        return `  ${label}: ${Number(v).toLocaleString()}${unit}`
      },
      footer(items) {
        if (isDonut || items.length < 2) return null
        const total = items.reduce((s, i) => s + (i.parsed?.y ?? 0), 0)
        return `Total: ${Number(total).toLocaleString()}`
      },
    },
  }

  // Scales — dynamically configure based on chart orientation
  const valueAxisTicks = {
    font: { family: 'Outfit, Inter, system-ui', size: 11 },
    color: '#94a3b8',
    precision: 0,
    callback: v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v,
  }
  const categoryAxisTicks = {
    font: { family: 'Outfit, Inter, system-ui', size: 11 },
    color: '#64748b',
    maxRotation: 0,
    minRotation: 0,
    callback: function(value) {
      let label = this.getLabelForValue(value) || '';
      if (typeof label !== 'string') return label;
      
      const words = label.split(' ');
      let lines = [];
      let currentLine = '';
      
      for (let i = 0; i < words.length; i++) {
        if ((currentLine + words[i]).length > 15 && currentLine.length > 0) {
          lines.push(currentLine.trim());
          currentLine = words[i] + ' ';
        } else {
          currentLine += words[i] + ' ';
        }
      }
      if (currentLine.trim()) lines.push(currentLine.trim());
      return lines.length > 1 ? lines : lines[0];
    }
  }

  const scales = isDonut ? {} : {
    x: {
      grid: { display: isHoriz, color: 'rgba(226,232,240,0.6)', drawBorder: false },
      border: { display: false },
      ticks: isHoriz ? valueAxisTicks : categoryAxisTicks,
      beginAtZero: isHoriz,
    },
    y: {
      grid: { display: !isHoriz, color: 'rgba(226,232,240,0.6)', drawBorder: false },
      border: { display: false },
      ticks: isHoriz ? categoryAxisTicks : valueAxisTicks,
      beginAtZero: !isHoriz,
    },
  }

  const userScales = props.options?.scales || {}
  const finalScales = {
    x: { ...scales.x, ...userScales.x },
    y: { ...scales.y, ...userScales.y },
  }

  const userPlugins = props.options?.plugins || {}
  const mergedOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 700, easing: 'easeInOutQuart' },
    plugins: {
      legend: {
        display: isDonut,
        position: 'bottom',
        labels: {
          usePointStyle: true,
          pointStyleWidth: 10,
          font: { family: 'Outfit, Inter, system-ui', size: 11, weight: '600' },
          padding: 16,
          color: '#64748b',
        },
        ...userPlugins.legend,
      },
      tooltip: { ...tooltipConfig, ...userPlugins.tooltip },
      ...userPlugins,
    },
    interaction: { mode: isDonut ? 'nearest' : 'index', intersect: isDonut },
    scales: isDonut ? {} : finalScales,
    // Pass through any remaining user options (e.g. indexAxis)
    ...Object.fromEntries(
      Object.entries(props.options).filter(([k]) => !['plugins','scales'].includes(k))
    ),
  }

  chartInstance = new Chart(ctx, {
    type: props.type,
    data: { ...props.chartData, datasets: processedDatasets },
    options: mergedOptions,
    plugins: [centerTextPlugin],
  })

  lastUpdated.value = Date.now()
}

// ─── Real-time polling ───────────────────────────────────────────────────────
const triggerRefresh = async () => {
  if (isRefreshing.value) return
  isRefreshing.value = true
  emit('refresh')
  await new Promise(r => setTimeout(r, 400))
  isRefreshing.value = false
}

const startPolling = () => {
  if (props.refreshInterval > 0)
    pollingTimer = setInterval(triggerRefresh, props.refreshInterval)
}
const stopPolling = () => { if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null } }

// ─── Watchers ───────────────────────────────────────────────────────────────
watch(() => props.chartData, () => nextTick(initChart), { deep: true })
watch(() => props.loading,   v => { if (!v) nextTick(initChart) })
watch(() => props.refreshInterval, () => { stopPolling(); startPolling() })

onMounted(() => { initChart(); startPolling() })
onBeforeUnmount(() => { stopPolling(); if (chartInstance) chartInstance.destroy() })
</script>

<style scoped>
.dashboard-chart-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  border-radius: 16px;
  overflow: hidden;
}
.dashboard-chart-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 32px -8px rgba(99, 102, 241, 0.12),
              0 4px 8px -2px rgba(0,0,0,0.06) !important;
}

/* Header */
.chart-title {
  font-family: 'Outfit', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: 0.1px;
}

/* LIVE badge */
.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  color: #10b981;
  background: rgba(16, 185, 129, 0.09);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 20px;
  padding: 2px 8px;
}
.live-dot {
  width: 5px; height: 5px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse-live 1.6s infinite;
}
@keyframes pulse-live {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.35; transform: scale(0.65); }
}

/* Timestamp */
.updated-text {
  font-size: 0.67rem;
  color: #94a3b8;
  white-space: nowrap;
}

/* Refresh button */
.btn-refresh {
  background: none;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 7px;
  color: #6366f1;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 0.78rem;
  transition: background 0.15s, border-color 0.15s;
  padding: 0;
  flex-shrink: 0;
}
.btn-refresh:hover { background: rgba(99,102,241,0.07); border-color: rgba(99,102,241,0.45); }
.btn-refresh.spinning i { animation: spin 0.65s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Overlays */
.chart-overlay {
  position: absolute; inset: 0;
  display: flex; justify-content: center; align-items: center;
  background: rgba(255,255,255,0.88); border-radius: 8px; z-index: 10;
}
.chart-overlay.soft { background: rgba(255,255,255,0.5); }

/* Empty state */
.empty-state {
  height: 240px;
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  gap: 8px; color: #cbd5e1;
}
.empty-state i { font-size: 2rem; }
.empty-state span { font-size: 0.82rem; font-family: 'Outfit', sans-serif; }
</style>
