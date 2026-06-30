# ECharts图表格式规范

## 格式定义

使用Markdown代码块语法，语言标识为 `echarts`，内容为JSON格式的ECharts配置对象。

### 基本格式

```markdown
```echarts
{
  "title": {
    "text": "图表标题"
  },
  "xAxis": {
    "data": ["类目1", "类目2", "类目3"]
  },
  "yAxis": {},
  "series": [{
    "type": "bar",
    "data": [10, 20, 30]
  }]
}
```
```

## 支持的图表类型

### 1. 柱状图 (bar)

```markdown
```echarts
{
  "title": { "text": "销售数据" },
  "xAxis": { "data": ["一月", "二月", "三月", "四月", "五月"] },
  "yAxis": {},
  "series": [{
    "type": "bar",
    "name": "销量",
    "data": [120, 200, 150, 80, 70]
  }]
}
```
```

### 2. 折线图 (line)

```markdown
```echarts
{
  "title": { "text": "温度变化" },
  "xAxis": { "data": ["周一", "周二", "周三", "周四", "周五"] },
  "yAxis": { "name": "温度(°C)" },
  "series": [{
    "type": "line",
    "name": "最高温度",
    "data": [11, 11, 15, 13, 12],
    "smooth": true
  }]
}
```
```

### 3. 饼图 (pie)

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
      { "value": 580, "name": "邮件营销" },
      { "value": 484, "name": "联盟广告" }
    ]
  }]
}
```
```

### 4. 散点图 (scatter)

```markdown
```echarts
{
  "title": { "text": "散点图示例" },
  "xAxis": {},
  "yAxis": {},
  "series": [{
    "type": "scatter",
    "data": [[10, 20], [15, 30], [20, 25], [25, 40], [30, 35]]
  }]
}
```
```

### 5. 雷达图 (radar)

```markdown
```echarts
{
  "title": { "text": "预算 vs 开销" },
  "radar": {
    "indicator": [
      { "name": "销售", "max": 6500 },
      { "name": "管理", "max": 16000 },
      { "name": "信息技术", "max": 30000 },
      { "name": "客服", "max": 38000 },
      { "name": "研发", "max": 52000 },
      { "name": "市场", "max": 25000 }
    ]
  },
  "series": [{
    "type": "radar",
    "data": [{
      "value": [4200, 3000, 20000, 35000, 50000, 19000],
      "name": "预算分配"
    }]
  }]
}
```
```

### 6. 仪表盘 (gauge)

```markdown
```echarts
{
  "series": [{
    "type": "gauge",
    "detail": { "formatter": "{value}%" },
    "data": [{ "value": 50, "name": "完成率" }]
  }]
}
```
```

## 高级配置

### 多系列图表

```markdown
```echarts
{
  "title": { "text": "多系列对比" },
  "xAxis": { "data": ["一月", "二月", "三月"] },
  "yAxis": {},
  "series": [
    {
      "type": "bar",
      "name": "系列1",
      "data": [120, 200, 150]
    },
    {
      "type": "bar",
      "name": "系列2",
      "data": [80, 150, 120]
    }
  ]
}
```
```

### 带图例和提示框

```markdown
```echarts
{
  "title": { "text": "带图例的图表" },
  "tooltip": { "trigger": "axis" },
  "legend": { "data": ["销量", "收入"] },
  "xAxis": { "data": ["一月", "二月", "三月"] },
  "yAxis": {},
  "series": [
    {
      "type": "bar",
      "name": "销量",
      "data": [120, 200, 150]
    },
    {
      "type": "line",
      "name": "收入",
      "data": [220, 180, 260]
    }
  ]
}
```
```

## 后端接口返回格式

后端接口应返回包含 `echarts` 代码块的Markdown文本：

```json
{
  "content": "这是数据分析结果：\n\n```echarts\n{\n  \"title\": { \"text\": \"数据分析\" },\n  \"xAxis\": { \"data\": [\"A\", \"B\", \"C\"] },\n  \"yAxis\": {},\n  \"series\": [{\n    \"type\": \"bar\",\n    \"data\": [10, 20, 30]\n  }]\n}\n```\n\n从图表可以看出..."
}
```

## 注意事项

1. JSON格式必须合法，支持标准JSON语法
2. 配置对象遵循ECharts官方配置项规范
3. 图表会自动适应容器宽度，高度默认为400px
4. 支持所有ECharts支持的图表类型和配置项
5. 建议后端返回格式化的JSON，避免解析错误
