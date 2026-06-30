<template>
  <div ref="chartContainer" class="echarts-container" :style="{ height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true
  },
  height: {
    type: String,
    default: '400px'
  },
  theme: {
    type: String,
    default: 'default'
  }
})

const chartContainer = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartContainer.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartContainer.value, props.theme)
  
  chartInstance.setOption(props.option, true)
}

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const updateChart = () => {
  if (chartInstance && props.option) {
    chartInstance.setOption(props.option, true)
  }
}

onMounted(() => {
  nextTick(() => {
    initChart()
    window.addEventListener('resize', resizeChart)
  })
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', resizeChart)
})

watch(() => props.option, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.theme, () => {
  nextTick(() => {
    initChart()
  })
})
</script>

<style scoped>
.echarts-container {
  width: 100%;
  min-height: 300px;
}
</style>

