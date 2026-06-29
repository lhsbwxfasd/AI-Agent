"""
本地MCP工具实现
提供常用的工具功能，如天气查询、搜索、计算等
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger


class MCPToolsService:
    """MCP工具服务"""
    
    def __init__(self):
        self.tools = {
            "weather": self.get_weather,
            "search": self.web_search,
            "calculate": self.calculate,
            "datetime": self.get_datetime,
            "format": self.format_text,
            "count": self.count_words,
            "translate": self.translate,
        }
        logger.info(f"MCP Tools service initialized with {len(self.tools)} tools")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            result = await self.tools[tool_name](parameters)
            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def list_tools(self) -> Dict[str, Dict]:
        """列出所有可用工具"""
        return {
            "weather": {
                "name": "天气查询",
                "description": "查询指定城市的天气信息",
                "parameters": {
                    "city": "城市名称（必需）",
                    "unit": "温度单位（celsius/fahrenheit，可选，默认celsius）"
                }
            },
            "search": {
                "name": "网络搜索",
                "description": "在网络上搜索信息",
                "parameters": {
                    "query": "搜索关键词（必需）",
                    "num_results": "返回结果数量（可选，默认5）"
                }
            },
            "calculate": {
                "name": "计算器",
                "description": "执行数学计算",
                "parameters": {
                    "expression": "数学表达式（必需），如：2+3*4"
                }
            },
            "datetime": {
                "name": "日期时间",
                "description": "获取当前日期时间或转换时区",
                "parameters": {
                    "timezone": "时区（可选，默认本地时区）",
                    "format": "时间格式（可选，默认ISO格式）"
                }
            },
            "format": {
                "name": "文本格式化",
                "description": "格式化文本（大小写、去除空格等）",
                "parameters": {
                    "text": "要格式化的文本（必需）",
                    "operation": "操作类型（upper/lower/trim/capitalize，必需）"
                }
            },
            "count": {
                "name": "字数统计",
                "description": "统计文本的字数、字符数等",
                "parameters": {
                    "text": "要统计的文本（必需）"
                }
            },
            "translate": {
                "name": "文本翻译",
                "description": "翻译文本（模拟）",
                "parameters": {
                    "text": "要翻译的文本（必需）",
                    "target_lang": "目标语言（可选，默认英语）"
                }
            }
        }
    
    async def get_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """天气查询工具（模拟）"""
        city = params.get("city")
        if not city:
            raise ValueError("city parameter is required")
        
        unit = params.get("unit", "celsius")
        
        # 模拟天气数据（实际应调用真实天气API）
        mock_weather_data = {
            "北京": {"temp": 25, "condition": "晴", "humidity": 45, "wind": "东北风3级"},
            "上海": {"temp": 28, "condition": "多云", "humidity": 65, "wind": "东南风2级"},
            "广州": {"temp": 32, "condition": "雷阵雨", "humidity": 80, "wind": "南风4级"},
            "深圳": {"temp": 30, "condition": "阴", "humidity": 75, "wind": "西南风3级"},
        }
        
        if city in mock_weather_data:
            data = mock_weather_data[city]
            return {
                "city": city,
                "temperature": f"{data['temp']}°{unit[0].upper()}",
                "condition": data["condition"],
                "humidity": f"{data['humidity']}%",
                "wind": data["wind"],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # 返回模拟数据
            return {
                "city": city,
                "temperature": f"20°{unit[0].upper()}",
                "condition": "晴",
                "humidity": "50%",
                "wind": "微风",
                "note": "模拟数据，实际使用请接入真实天气API"
            }
    
    async def web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """网络搜索工具（模拟）"""
        query = params.get("query")
        if not query:
            raise ValueError("query parameter is required")
        
        num_results = params.get("num_results", 5)
        
        # 模拟搜索结果（实际应调用真实搜索API）
        mock_results = [
            {
                "title": f"关于'{query}'的搜索结果1",
                "url": "https://example.com/result1",
                "snippet": f"这是关于{query}的搜索结果摘要..."
            },
            {
                "title": f"关于'{query}'的搜索结果2",
                "url": "https://example.com/result2",
                "snippet": f"更多关于{query}的信息..."
            },
        ]
        
        return {
            "query": query,
            "total_results": len(mock_results),
            "results": mock_results[:num_results],
            "note": "模拟搜索结果，实际使用请接入真实搜索API"
        }
    
    async def calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算器工具"""
        expression = params.get("expression")
        if not expression:
            raise ValueError("expression parameter is required")
        
        try:
            # 安全的数学表达式求值（使用ast代替eval）
            import ast
            import operator
            
            # 允许的运算符
            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    left = eval_expr(node.left)
                    right = eval_expr(node.right)
                    op_type = type(node.op)
                    if op_type in operators:
                        return operators[op_type](left, right)
                    else:
                        raise ValueError(f"Unsupported operator: {op_type}")
                elif isinstance(node, ast.UnaryOp):
                    operand = eval_expr(node.operand)
                    op_type = type(node.op)
                    if op_type in operators:
                        return operators[op_type](operand)
                    else:
                        raise ValueError(f"Unsupported operator: {op_type}")
                else:
                    raise ValueError(f"Unsupported expression type: {type(node)}")
            
            # 解析并计算表达式
            tree = ast.parse(expression, mode='eval')
            result = eval_expr(tree.body)
            
            return {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    async def get_datetime(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """日期时间工具"""
        timezone = params.get("timezone", "local")
        time_format = params.get("format", "iso")
        
        now = datetime.now()
        
        if time_format == "iso":
            formatted = now.isoformat()
        elif time_format == "timestamp":
            formatted = str(int(now.timestamp()))
        elif time_format == "date":
            formatted = now.strftime("%Y-%m-%d")
        elif time_format == "time":
            formatted = now.strftime("%H:%M:%S")
        else:
            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "datetime": formatted,
            "timezone": timezone,
            "unix_timestamp": int(now.timestamp())
        }
    
    async def format_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """文本格式化工具"""
        text = params.get("text")
        operation = params.get("operation")
        
        if not text or not operation:
            raise ValueError("text and operation parameters are required")
        
        if operation == "upper":
            result = text.upper()
        elif operation == "lower":
            result = text.lower()
        elif operation == "trim":
            result = text.strip()
        elif operation == "capitalize":
            result = text.capitalize()
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            "original": text,
            "operation": operation,
            "result": result
        }
    
    async def count_words(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """字数统计工具"""
        text = params.get("text")
        if not text:
            raise ValueError("text parameter is required")
        
        # 统计各种指标
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        word_count = len(text.split())
        line_count = len(text.split("\n"))
        
        # 中文字符统计
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        return {
            "character_count": char_count,
            "character_count_no_spaces": char_count_no_spaces,
            "word_count": word_count,
            "line_count": line_count,
            "chinese_character_count": chinese_chars
        }
    
    async def translate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """文本翻译工具（模拟）"""
        text = params.get("text")
        target_lang = params.get("target_lang", "en")
        
        if not text:
            raise ValueError("text parameter is required")
        
        # 模拟翻译（实际应调用真实翻译API）
        return {
            "original_text": text,
            "target_language": target_lang,
            "translated_text": f"[模拟翻译] {text} (目标语言: {target_lang})",
            "note": "模拟翻译结果，实际使用请接入真实翻译API"
        }


mcp_tools_service = MCPToolsService()
