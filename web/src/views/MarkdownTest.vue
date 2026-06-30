<template>
  <div class="test-container">
    <h1>Markdown解析器测试</h1>
    
    <div class="test-section">
      <h2>JavaScript代码</h2>
      <MarkdownRenderer :content="javascriptCode" />
    </div>
    
    <div class="test-section">
      <h2>Python代码</h2>
      <MarkdownRenderer :content="pythonCode" />
    </div>
    
    <div class="test-section">
      <h2>数学公式</h2>
      <MarkdownRenderer :content="mathFormula" />
    </div>
    
    <div class="test-section">
      <h2>Mermaid流程图</h2>
      <MarkdownRenderer :content="mermaidDiagram" />
    </div>
  </div>
</template>

<script setup>
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

const javascriptCode = `\
\`\`\`javascript
function fibonacci(n) {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
}

const result = fibonacci(10)
console.log(\`Fibonacci(10) = \${result}\`)
\`\`\`
`

const pythonCode = `\
\`\`\`python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

numbers = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(numbers))
\`\`\`
`

const mathFormula = `
行内公式：$E = mc^2$

块级公式：

$$
\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}
$$
`

const mermaidDiagram = `\
\`\`\`mermaid
graph TD
    A[开始] --> B[输入数据]
    B --> C{数据验证}
    C -->|有效| D[处理数据]
    C -->|无效| E[显示错误]
    E --> B
    D --> F[保存结果]
    F --> G[结束]
\`\`\`
`
</script>

<style scoped>
.test-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.test-section {
  margin-bottom: 40px;
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
