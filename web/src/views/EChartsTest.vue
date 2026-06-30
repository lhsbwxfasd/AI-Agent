<template>
  <div class="echarts-test-container">
    <h1>ECharts图表渲染测试</h1>
    
    <div class="test-section">
      <h2>1. 柱状图</h2>
      <MarkdownRenderer :content="barChart" />
    </div>
    
    <div class="test-section">
      <h2>2. 折线图</h2>
      <MarkdownRenderer :content="lineChart" />
    </div>
    
    <div class="test-section">
      <h2>3. 饼图</h2>
      <MarkdownRenderer :content="pieChart" />
    </div>
    
    <div class="test-section">
      <h2>4. 多系列组合图</h2>
      <MarkdownRenderer :content="mixedChart" />
    </div>
    
    <div class="test-section">
      <h2>5. 雷达图</h2>
      <MarkdownRenderer :content="radarChart" />
    </div>
    
    <div class="test-section">
      <h2>6. 完整示例（包含文本和图表）</h2>
      <MarkdownRenderer :content="completeExample" />
    </div>
  </div>
</template>

<script setup>
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

const barChart = `\
\`\`\`echarts
{
  "title": {
    "text": "销售数据统计",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "xAxis": {
    "data": ["一月", "二月", "三月", "四月", "五月", "六月"],
    "axisLabel": {
      "interval": 0
    }
  },
  "yAxis": {
    "name": "销售额（万元）"
  },
  "series": [{
    "type": "bar",
    "name": "销售额",
    "data": [120, 200, 150, 80, 70, 110],
    "itemStyle": {
      "color": "#409eff"
    }
  }]
}
\`\`\`
`

const lineChart = `\
\`\`\`echarts
{
  "title": {
    "text": "温度变化趋势",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "legend": {
    "data": ["最高温度", "最低温度"],
    "top": 30
  },
  "xAxis": {
    "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
  },
  "yAxis": {
    "name": "温度(°C)"
  },
  "series": [
    {
      "type": "line",
      "name": "最高温度",
      "data": [11, 11, 15, 13, 12, 13, 10],
      "smooth": true,
      "itemStyle": {
        "color": "#ff6b6b"
      }
    },
    {
      "type": "line",
      "name": "最低温度",
      "data": [1, -2, 2, 5, 3, 2, 0],
      "smooth": true,
      "itemStyle": {
        "color": "#4ecdc4"
      }
    }
  ]
}
\`\`\`
`

const pieChart = `\
\`\`\`echarts
{
  "title": {
    "text": "访问来源分析",
    "left": "center"
  },
  "tooltip": {
    "trigger": "item",
    "formatter": "{a} <br/>{b}: {c} ({d}%)"
  },
  "legend": {
    "orient": "vertical",
    "left": "left",
    "top": "middle"
  },
  "series": [{
    "name": "访问来源",
    "type": "pie",
    "radius": "50%",
    "center": ["60%", "50%"],
    "data": [
      { "value": 1048, "name": "搜索引擎" },
      { "value": 735, "name": "直接访问" },
      { "value": 580, "name": "邮件营销" },
      { "value": 484, "name": "联盟广告" },
      { "value": 300, "name": "视频广告" }
    ],
    "emphasis": {
      "itemStyle": {
        "shadowBlur": 10,
        "shadowOffsetX": 0,
        "shadowColor": "rgba(0, 0, 0, 0.5)"
      }
    }
  }]
}
\`\`\`
`

const mixedChart = `\
\`\`\`echarts
{
  "title": {
    "text": "销量与增长率对比",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis",
    "axisPointer": {
      "type": "cross"
    }
  },
  "legend": {
    "data": ["销量", "增长率"],
    "top": 30
  },
  "xAxis": {
    "data": ["一月", "二月", "三月", "四月", "五月", "六月"]
  },
  "yAxis": [
    {
      "type": "value",
      "name": "销量",
      "position": "left"
    },
    {
      "type": "value",
      "name": "增长率(%)",
      "position": "right"
    }
  ],
  "series": [
    {
      "name": "销量",
      "type": "bar",
      "data": [120, 200, 150, 80, 70, 110]
    },
    {
      "name": "增长率",
      "type": "line",
      "yAxisIndex": 1,
      "data": [10, 15, -5, 20, 5, 8],
      "smooth": true
    }
  ]
}
\`\`\`
`

const radarChart = `\
\`\`\`echarts
{
  "title": {
    "text": "能力雷达图",
    "left": "center"
  },
  "tooltip": {},
  "radar": {
    "indicator": [
      { "name": "编程能力", "max": 100 },
      { "name": "沟通能力", "max": 100 },
      { "name": "学习能力", "max": 100 },
      { "name": "团队协作", "max": 100 },
      { "name": "创新能力", "max": 100 },
      { "name": "执行能力", "max": 100 }
    ],
    "center": ["50%", "55%"],
    "radius": "65%"
  },
  "series": [{
    "name": "能力值",
    "type": "radar",
    "data": [
      {
        "value": [85, 70, 90, 80, 75, 88],
        "name": "张三",
        "areaStyle": {
          "color": "rgba(64, 158, 255, 0.3)"
        }
      }
    ]
  }]
}
\`\`\`
`

const completeExample = `
## 数据分析报告

根据最近一个月的数据统计，我们得出以下结论：

### 1. 销售趋势分析

从下表可以看出，销售额整体呈上升趋势：

\`\`\`echarts
{
  "title": {
    "text": "月度销售趋势",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "xAxis": {
    "data": ["1月", "2月", "3月", "4月", "5月", "6月"]
  },
  "yAxis": {
    "name": "销售额（万元）"
  },
  "series": [{
    "type": "line",
    "data": [120, 132, 101, 134, 90, 230],
    "smooth": true,
    "areaStyle": {}
  }]
}
\`\`\`

### 2. 产品分布

各类产品的销售占比情况：

\`\`\`echarts
{
  "title": {
    "text": "产品销售占比",
    "left": "center"
  },
  "tooltip": {
    "trigger": "item"
  },
  "series": [{
    "type": "pie",
    "radius": "60%",
    "data": [
      { "value": 335, "name": "产品A" },
      { "value": 310, "name": "产品B" },
      { "value": 234, "name": "产品C" },
      { "value": 135, "name": "产品D" }
    ]
  }]
}
\`\`\`

### 3. 总结

综合以上数据分析，建议：
- 继续保持产品A的市场推广力度
- 产品B有较大增长潜力，可适当增加投入
- 关注产品C的销售下滑趋势
`
</script>

<style scoped>
.echarts-test-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f5f5;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-section h2 {
  margin-bottom: 16px;
  color: #333;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}
</style>
