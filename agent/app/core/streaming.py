import json
from typing import Dict, Any


def stream_formatter(data: Dict[str, Any]) -> str:
    """格式化 SSE 流式响应"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


class StreamBuffer:
    """流式响应缓冲区"""
    
    def __init__(self, buffer_size: int = 100):
        self.buffer = []
        self.buffer_size = buffer_size
    
    def add(self, chunk: str) -> bool:
        """添加内容到缓冲区"""
        self.buffer.append(chunk)
        return len(self.buffer) >= self.buffer_size
    
    def get_content(self) -> str:
        """获取缓冲区内容并清空"""
        content = ''.join(self.buffer)
        self.buffer = []
        return content
    
    def flush(self) -> str:
        """刷新缓冲区"""
        return self.get_content()
