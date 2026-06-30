# AI后端图表生成功能使用指南

## 功能概述

后端AI接口现在支持自动识别用户的图表请求，并返回ECharts格式的可视化数据。

## 实现原理

### 1. 图表检测 (`chart_processor.py`)

`ChartDetector`类负责检测用户消息中是否包含图表请求：

**支持的触发关键词：**
- 中文：图表、图形、图、可视化、绘制、画图
- 英文：chart、graph、plot、echart、echarts
- 具体类型：柱状图、折线图、饼图、散点图、雷达图等

**图表类型识别：**
- 自动识别用户请求的图表类型
- 如果未明确指定，根据上下文推断：
  - "对比"、"比较" → 柱状图
  - "趋势"、"变化" → 折线图
  - "占比"、"分布" → 饼图

### 2. 图表生成 (`chart_processor.py`)

`ChartGenerator`类负责生成ECharts配置：

- 从AI响应中提取数据（数字、类别等）
- 根据图表类型生成对应的ECharts配置
- 返回Markdown格式的代码块

### 3. Agent集成 (`agent.py`)

在`Agent`类中集成了图表处理：

- **非流式响应**：`process`方法中调用`_process_chart_request`
- **流式响应**：`process_stream`方法中在响应结束后生成图表

## 使用示例

### 示例1：基础柱状图

**用户请求：**
```
请用图表展示最近5个月的销售数据
```

**AI响应：**
```markdown
根据数据分析，最近5个月的销售数据如下：

1月份销售额为120万元
2月份销售额为150万元
3月份销售额为180万元
4月份销售额为160万元
5月份销售额为200万元

```echarts
{
  "title": {
    "text": "最近5个月的销售数据",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis",
    "axisPointer": {
      "type": "shadow"
    }
  },
  "xAxis": {
    "type": "category",
    "data": ["1月份", "2月份", "3月份", "4月份", "5月份"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [{
    "type": "bar",
    "data": [120, 150, 180, 160, 200]
  }]
}
```
```

### 示例2：折线图

**用户请求：**
```
用折线图显示温度变化趋势
```

**AI响应：**
```markdown
根据气象数据，温度变化趋势如下：

```echarts
{
  "title": {
    "text": "温度变化趋势",
    "left": "center"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "xAxis": {
    "type": "category",
    "data": ["周一", "周二", "周三", "周四", "周五"],
    "boundaryGap": false
  },
  "yAxis": {
    "type": "value"
  },
  "series": [{
    "type": "line",
    "data": [20, 22, 19, 23, 21],
    "smooth": true
  }]
}
```
```

### 示例3：饼图

**用户请求：**
```
用饼图展示各部门人员占比
```

**AI响应：**
```markdown
各部门人员分布情况：

```echarts
{
  "title": {
    "text": "各部门人员占比",
    "left": "center"
  },
  "tooltip": {
    "trigger": "item",
    "formatter": "{a} <br/>{b}: {c} ({d}%)"
  },
  "legend": {
    "orient": "vertical",
    "left": "left"
  },
  "series": [{
    "type": "pie",
    "radius": "50%",
    "data": [
      {"name": "研发部", "value": 50},
      {"name": "市场部", "value": 30},
      {"name": "销售部", "value": 40},
      {"name": "人事部", "value": 10}
    ]
  }]
}
```
```

## 支持的图表类型

| 图表类型 | 触发关键词 | 适用场景 |
|---------|-----------|---------|
| **柱状图 (bar)** | 柱状图、条形图、对比、比较 | 数据对比、排名展示 |
| **折线图 (line)** | 折线图、线图、趋势、变化 | 趋势分析、时间序列 |
| **饼图 (pie)** | 饼图、扇形图、占比、分布 | 占比分析、分布展示 |
| **散点图 (scatter)** | 散点图、点图 | 相关性分析、分布 |
| **雷达图 (radar)** | 雷达图 | 多维度对比、能力评估 |

## 数据提取逻辑

图表生成器会从AI响应中自动提取：

1. **数字数据**：使用正则表达式 `\d+\.?\d*` 提取所有数字
2. **类别标签**：提取时间表达（如"1月"、"周一"）或使用默认标签
3. **数据对齐**：确保类别和数值数量匹配

## 配置选项

图表生成器内置配色方案：

```python
color_palette = [
    '#409eff',  # 蓝色（主色）
    '#67c23a',  # 绿色
    '#e6a23c',  # 橙色
    '#f56c6c',  # 红色
    '#909399',  # 灰色
    '#5470c6',  # 深蓝
    '#91cc75',  # 浅绿
    '#fac858',  # 黄色
    '#ee6666',  # 浅红
    '#73c0de'   # 浅蓝
]
```

## API接口说明

### 非流式接口

**请求：**
```json
POST /api/v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "用图表展示销售数据"}
  ],
  "model": "deepseek-chat"
}
```

**响应：**
```json
{
  "content": "销售数据分析结果...\n\n```echarts\n{...}\n```",
  "model": "deepseek-chat",
  "conversation_id": "xxx"
}
```

### 流式接口

**请求：**
```json
POST /api/v1/chat/completions/stream
{
  "messages": [
    {"role": "user", "content": "用图表展示销售数据"}
  ],
  "stream": true
}
```

**响应（SSE格式）：**
```
data: {"type": "start", "request_id": "xxx", ...}

data: {"type": "content", "content": "销售数据分析结果..."}

data: {"type": "content", "content": "\n\n```echarts\n{...}\n```"}

data: {"type": "end", "request_id": "xxx", ...}
```

## 最佳实践

### 1. 明确图表类型

**推荐：**
```
请用柱状图展示各部门销售额对比
```

**不推荐：**
```
展示销售数据
```

### 2. 提供数据上下文

**推荐：**
```
分析以下销售数据并用图表展示：
1月：120万，2月：150万，3月：180万
```

**说明：** 明确的数据有助于生成准确的图表

### 3. 指定分析维度

**推荐：**
```
用饼图展示各产品线的收入占比
```

**说明：** 明确维度可以生成更有意义的图表

## 错误处理

如果图表生成失败，系统会：
1. 记录错误日志
2. 返回原始AI响应（不含图表）
3. 不影响正常对话流程

## 扩展建议

### 1. 自定义图表模板

可以在`chart_processor.py`中添加更多图表模板：

```python
def _generate_custom_chart(self, data: Dict, description: str) -> Dict:
    """自定义图表生成逻辑"""
    # 实现自定义图表配置
    pass
```

### 2. 数据验证

添加数据验证逻辑：

```python
def _validate_data(self, data: Dict) -> bool:
    """验证数据有效性"""
    return len(data['categories']) > 0 and len(data['values']) > 0
```

### 3. 智能推荐

根据数据特征自动推荐最佳图表类型：

```python
def _recommend_chart_type(self, data: Dict) -> str:
    """根据数据特征推荐图表类型"""
    # 实现智能推荐逻辑
    pass
```

## 文件清单

| 文件 | 说明 |
|------|------|
| `app/core/chart_processor.py` | 图表检测与生成核心模块 |
| `app/core/agent.py` | Agent集成图表处理逻辑 |
| `CHART_USAGE.md` | 本使用指南 |

## 测试方法

### 1. 单元测试

```python
from app.core.chart_processor import chart_detector, chart_generator

# 测试检测
is_chart, chart_type, desc = chart_detector.detect_chart_request("用柱状图展示销售数据")
assert is_chart == True
assert chart_type == "bar"

# 测试生成
chart = chart_generator.generate_chart("bar", "销售数据", "1月:120, 2月:150")
assert "```echarts" in chart
```

### 2. 集成测试

使用curl或Postman测试API：

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "用图表展示销售数据"}]
  }'
```

## 注意事项

1. **数据提取依赖AI响应格式**：确保AI返回的数据格式规范
2. **图表类型推断可能不准确**：建议用户明确指定图表类型
3. **大数据量性能**：大量数据点可能影响渲染性能
4. **前端兼容性**：确保前端已安装echarts依赖

## 更新日志

- **v1.0.0** (2024-01-XX)
  - 初始实现图表检测与生成功能
  - 支持5种基础图表类型
  - 集成到Agent处理流程
