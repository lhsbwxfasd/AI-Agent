import { marked } from 'marked'
import hljs from 'highlight.js'
import katex from 'katex'
import mermaid from 'mermaid'
import 'highlight.js/styles/github-dark.css'

const customParsers = []

export function registerCustomParser(parser) {
  customParsers.push(parser)
}

export function unregisterCustomParser(parser) {
  const index = customParsers.indexOf(parser)
  if (index > -1) {
    customParsers.splice(index, 1)
  }
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, m => map[m])
}

function parseLatex(text) {
  const blockLatexRegex = /\$\$([\s\S]+?)\$\$/g
  const inlineLatexRegex = /\$([^\$\n]+?)\$/g
  
  text = text.replace(blockLatexRegex, (match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), {
        displayMode: true,
        throwOnError: false,
        errorColor: '#cc0000'
      })
      return `<div class="katex-block">${html}</div>`
    } catch (e) {
      return `<div class="katex-error">LaTeX Error: ${escapeHtml(e.message)}</div>`
    }
  })
  
  text = text.replace(inlineLatexRegex, (match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), {
        displayMode: false,
        throwOnError: false,
        errorColor: '#cc0000'
      })
      return `<span class="katex-inline">${html}</span>`
    } catch (e) {
      return `<span class="katex-error">LaTeX Error: ${escapeHtml(e.message)}</span>`
    }
  })
  
  return text
}

async function parseMermaid(text) {
  const mermaidRegex = /```mermaid\n([\s\S]+?)```/g
  
  const matches = []
  let match
  while ((match = mermaidRegex.exec(text)) !== null) {
    matches.push({
      full: match[0],
      code: match[1]
    })
  }
  
  for (const item of matches) {
    try {
      const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const { svg } = await mermaid.render(id, item.code)
      text = text.replace(item.full, `<div class="mermaid-container">${svg}</div>`)
    } catch (e) {
      text = text.replace(item.full, `<div class="mermaid-error">Mermaid Error: ${escapeHtml(e.message)}</div>`)
    }
  }
  
  return text
}

function parseCustomFormats(text) {
  for (const parser of customParsers) {
    if (typeof parser === 'function') {
      text = parser(text)
    }
  }
  return text
}

function addLineNumbers(code) {
  const lines = code.split('\n')
  const numberedLines = lines.map((line, index) => {
    const lineNumber = index + 1
    return `<span class="code-line"><span class="line-number">${lineNumber}</span><span class="line-content">${line}</span></span>`
  })
  return numberedLines.join('')
}

const renderer = new marked.Renderer()

renderer.code = function(code, language) {
  let highlightedCode
  let lang = language || ''
  
  if (lang === 'mermaid') {
    return `<div class="mermaid">${escapeHtml(code)}</div>`
  }
  
  if (lang === 'echarts') {
    try {
      const option = JSON.parse(code)
      const id = `echarts-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      return `<div class="echarts-chart" data-echarts-id="${id}" data-echarts-option="${escapeHtml(JSON.stringify(option))}"></div>`
    } catch (e) {
      return `<div class="echarts-error">ECharts JSON Error: ${escapeHtml(e.message)}</div>`
    }
  }
  
  if (lang && hljs.getLanguage(lang)) {
    try {
      highlightedCode = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
    } catch (e) {
      console.warn('Highlight error for language:', lang, e)
      highlightedCode = escapeHtml(code)
    }
  } else if (lang) {
    try {
      const result = hljs.highlightAuto(code, [lang])
      highlightedCode = result.value
    } catch (e) {
      highlightedCode = escapeHtml(code)
    }
  } else {
    try {
      highlightedCode = hljs.highlightAuto(code).value
    } catch (e) {
      highlightedCode = escapeHtml(code)
    }
  }
  
  const numberedCode = addLineNumbers(highlightedCode)
  
  const langLabel = lang ? `<span class="code-lang">${escapeHtml(lang)}</span>` : ''
  
  return `<pre class="code-block"><code>${langLabel}<div class="code-content">${numberedCode}</div></code></pre>`
}

renderer.codespan = function(code) {
  return `<code class="inline-code">${escapeHtml(code)}</code>`
}

marked.setOptions({
  renderer: renderer,
  breaks: true,
  gfm: true
})

export async function parseMarkdown(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }
  
  let processedText = text
  
  processedText = parseCustomFormats(processedText)
  
  processedText = parseLatex(processedText)
  
  processedText = await parseMermaid(processedText)
  
  const html = marked(processedText)
  
  return html
}

export function parseMarkdownSync(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }
  
  let processedText = text
  
  processedText = parseCustomFormats(processedText)
  
  processedText = parseLatex(processedText)
  
  const html = marked(processedText)
  
  return html
}

export function initMermaid() {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'inherit'
  })
}
