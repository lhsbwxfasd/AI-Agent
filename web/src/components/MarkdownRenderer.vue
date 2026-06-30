<template>
  <div class="markdown-renderer" ref="rendererRef" v-html="renderedContent"></div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { parseMarkdown, parseMarkdownSync, initMermaid } from '@/utils/markdownParser'
import * as echarts from 'echarts'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  async: {
    type: Boolean,
    default: true
  }
})

const renderedContent = ref('')
const rendererRef = ref(null)
const echartsInstances = []

const renderContent = async () => {
  if (!props.content) {
    renderedContent.value = ''
    return
  }
  
  try {
    if (props.async) {
      renderedContent.value = await parseMarkdown(props.content)
    } else {
      renderedContent.value = parseMarkdownSync(props.content)
    }
    
    await nextTick()
    initEChartsCharts()
  } catch (error) {
    console.error('Markdown rendering error:', error)
    renderedContent.value = props.content
  }
}

const initEChartsCharts = () => {
  if (!rendererRef.value) return
  
  echartsInstances.forEach(instance => {
    if (instance) {
      instance.dispose()
    }
  })
  echartsInstances.length = 0
  
  const chartElements = rendererRef.value.querySelectorAll('.echarts-chart')
  
  chartElements.forEach(element => {
    try {
      const optionStr = element.getAttribute('data-echarts-option')
      if (!optionStr) return
      
      const option = JSON.parse(optionStr)
      
      element.style.width = '100%'
      element.style.height = '400px'
      
      const chartInstance = echarts.init(element)
      chartInstance.setOption(option)
      
      echartsInstances.push(chartInstance)
      
      const resizeHandler = () => {
        chartInstance.resize()
      }
      window.addEventListener('resize', resizeHandler)
      element._resizeHandler = resizeHandler
    } catch (e) {
      console.error('ECharts initialization error:', e)
      element.innerHTML = `<div class="echarts-error">ECharts Error: ${e.message}</div>`
    }
  })
}

onMounted(() => {
  initMermaid()
  renderContent()
})

onBeforeUnmount(() => {
  echartsInstances.forEach(instance => {
    if (instance) {
      instance.dispose()
    }
  })
  
  if (rendererRef.value) {
    const chartElements = rendererRef.value.querySelectorAll('.echarts-chart')
    chartElements.forEach(element => {
      if (element._resizeHandler) {
        window.removeEventListener('resize', element._resizeHandler)
      }
    })
  }
})

watch(() => props.content, () => {
  renderContent()
}, { immediate: true })
</script>

<style scoped>
.markdown-renderer {
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-renderer :deep(.code-block) {
  background-color: #2d2d2d;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
  position: relative;
}

.markdown-renderer :deep(.code-block code) {
  display: block;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  color: #f8f8f2;
}

.markdown-renderer :deep(.code-lang) {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 12px;
  color: #999;
  font-family: sans-serif;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.markdown-renderer :deep(.code-content) {
  padding-top: 8px;
}

.markdown-renderer :deep(.code-line) {
  display: block;
  line-height: 1.5;
}

.markdown-renderer :deep(.line-number) {
  display: inline-block;
  width: 40px;
  text-align: right;
  color: #858790;
  user-select: none;
  font-size: 13px;
  padding-right: 16px;
  margin-right: 8px;
  border-right: 1px solid #404040;
}

.markdown-renderer :deep(.line-content) {
  display: inline;
}

.markdown-renderer :deep(.inline-code) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #e83e8c;
}

.markdown-renderer :deep(p) {
  margin: 8px 0;
}

.markdown-renderer :deep(h1),
.markdown-renderer :deep(h2),
.markdown-renderer :deep(h3),
.markdown-renderer :deep(h4),
.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.markdown-renderer :deep(li) {
  margin: 4px 0;
}

.markdown-renderer :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 12px 0;
  color: #666;
  background-color: #f9f9f9;
  padding: 8px 16px;
  border-radius: 4px;
}

.markdown-renderer :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

.markdown-renderer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-renderer :deep(th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

.markdown-renderer :deep(.katex-block) {
  display: block;
  text-align: center;
  margin: 16px 0;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-renderer :deep(.katex-inline) {
  display: inline;
}

.markdown-renderer :deep(.katex-error) {
  color: #cc0000;
  font-style: italic;
}

.markdown-renderer :deep(.mermaid-container) {
  text-align: center;
  margin: 16px 0;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-renderer :deep(.mermaid) {
  display: none;
}

.markdown-renderer :deep(.mermaid-error) {
  color: #cc0000;
  padding: 12px;
  background-color: #fff0f0;
  border-radius: 4px;
  margin: 12px 0;
}

.markdown-renderer :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 8px 0;
}

.markdown-renderer :deep(hr) {
  border: none;
  border-top: 2px solid #eee;
  margin: 16px 0;
}

.markdown-renderer :deep(.echarts-chart) {
  width: 100%;
  height: 400px;
  margin: 16px 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markdown-renderer :deep(.echarts-error) {
  color: #cc0000;
  padding: 16px;
  background-color: #fff0f0;
  border-radius: 8px;
  margin: 16px 0;
  border: 1px solid #ffcccc;
}
</style>
