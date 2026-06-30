# ECharts自定义解析器使用指南

## 概述

已成功实现ECharts图表自定义解析器，支持在Markdown中嵌入ECharts图表配置，自动渲染为交互式图表。

## 安装依赖

```bash
npm install echarts
```

## 格式定义

使用Markdown代码块语法，语言标识为 `echarts`，内容为JSON格式的ECharts配置对象：

```markdown
```echarts
{
  "title": { "text": "图表标题" },
  "xAxis": { "data": ["A", "B", "C"] },
  "yAxis": {},
  "series": [{
    "type": "bar",
    "data": [10, 20, 30]
  }]
}
```
```

## 实现原理

### 1. 解析阶段 (markdownParser.js)

在`renderer.code`函数中添加ECharts识别逻辑：

```javascript
if (lang === 'echarts') {
  try {
    const option = JSON.parse(code)
    const id = `echarts-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    return `<div class="echarts-chart" data-echarts-id="${id}" data-echarts-option="${escapeHtml(JSON.stringify(option))}"></div>`
  } catch (e) {
    return `<div class="echarts-error">ECharts JSON Error: ${escapeHtml(e.message)}</div>`
  }
}
```

### 2. 渲染阶段 (MarkdownRenderer.vue)

在组件挂载后，查找所有`.echarts-chart`元素并初始化ECharts实例：

```javascript
const initEChartsCharts = () => {
  const chartElements = rendererRef.value.querySelectorAll('.echarts-chart')
  
  chartElements.forEach(element => {
    const optionStr = element.getAttribute('data-echarts-option')
    const option = JSON.parse(optionStr)
    
    const chartInstance = echarts.init(element)
    chartInstance.setOption(option)
    
    echartsInstances.push(chartInstance)
  })
}
```

## 使用示例

### 基础柱状图

```markdown
```echarts
{
  "title": { "text": "销售数据" },
  "xAxis": { "data": ["一月", "二月", "三月"] },
  "yAxis": {},
  "series": [{
    "type": "bar",
    "data": [120, 200, 150]
  }]
}
```
```

### 多系列折线图

```markdown
```echarts
{
  "title": { "text": "温度变化" },
  "tooltip": { "trigger": "axis" },
  "legend": { "data": ["最高温度", "最低温度"] },
  "xAxis": { "data": ["周一", "周二", "周三"] },
  "yAxis": {},
  "series": [
    {
      "type": "line",
      "name": "最高温度",
      "data": [11, 11, 15]
    },
    {
      "type": "line",
      "name": "最低温度",
      "data": [1, -2, 2]
    }
  ]
}
```
```

### 饼图

```markdown
```echarts
{
  "title": { "text": "访问来源", "left": "center" },
  "series": [{
    "type": "pie",
    "radius": "50%",
    "data": [
      { "value": 1048, "name": "搜索引擎" },
      { "value": 735, "name": "直接访问" },
      { "value": 580, "name": "邮件营销" }
    ]
  }]
}
```
```

## 后端接口实现

### 返回格式示例

后端AI接口应返回包含ECharts代码块的Markdown文本：

```python
# Python示例
def generate_response(query):
    # 分析数据
    data = analyze_data(query)
    
    # 生成图表配置
    chart_config = {
        "title": {"text": "数据分析结果"},
        "xAxis": {"data": data.categories},
        "yAxis": {},
        "series": [{
            "type": "bar",
            "data": data.values
        }]
    }
    
    # 构建Markdown响应
    response = f"""
根据您的查询，数据分析结果如下：

```echarts
{json.dumps(chart_config, ensure_ascii=False)}
```

从图表可以看出，{data.summary}
"""
    return response
```

### Node.js示例

```javascript
function generateResponse(query) {
  const data = analyzeData(query)
  
  const chartConfig = {
    title: { text: '数据分析结果' },
    xAxis: { data: data.categories },
    yAxis: {},
    series: [{
      type: 'bar',
      data: data.values
    }]
  }
  
  return `
根据您的查询，数据分析结果如下：

\`\`\`echarts
${JSON.stringify(chartConfig, null, 2)}
\`\`\`

从图表可以看出，${data.summary}
`
}
```

## 支持的图表类型

- **柱状图 (bar)** - 适合对比数据
- **折线图 (line)** - 适合趋势分析
- **饼图 (pie)** - 适合占比分析
- **散点图 (scatter)** - 适合相关性分析
- **雷达图 (radar)** - 适合多维度对比
- **仪表盘 (gauge)** - 适合进度展示
- **所有ECharts支持的图表类型**

## 高级配置

### 自定义主题

在MarkdownRenderer组件中支持主题配置：

```vue
<EChartsRenderer :option="chartOption" theme="dark" />
```

### 响应式设计

图表会自动响应窗口大小变化，无需额外配置。

### 错误处理

如果JSON格式错误，会显示友好的错误提示：

```
ECharts JSON Error: Unexpected token...
```

## 性能优化

1. **按需引入ECharts模块**（可选）

```javascript
// 替代 import * as echarts from 'echarts'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  CanvasRenderer
])
```

2. **图表实例管理**
   - 自动销毁旧实例
   - 组件卸载时清理资源
   - 避免内存泄漏

## 测试方法

访问测试页面验证功能：

```javascript
// 在router中添加路由
{
  path: '/echarts-test',
  component: () => import('@/views/EChartsTest.vue')
}
```

## 注意事项

1. JSON配置必须合法，使用双引号
2. 不支持JavaScript表达式，仅支持静态JSON
3. 图表默认高度400px，可通过CSS调整
4. 建议后端返回格式化的JSON，提高可读性
5. 复杂图表配置建议使用ECharts官方配置项手册

## 文件清单

- `ECHARTS_FORMAT.md` - 格式规范文档
- `src/utils/markdownParser.js` - 解析器核心逻辑
- `src/components/EChartsRenderer.vue` - 独立图表组件
- `src/components/MarkdownRenderer.vue` - 集成渲染器
- `src/views/EChartsTest.vue` - 测试页面
- `ECHARTS_USAGE.md` - 本使用指南
