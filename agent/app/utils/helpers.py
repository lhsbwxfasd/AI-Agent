import uuid
from datetime import datetime, timedelta
from typing import Optional


def generate_request_id() -> str:
    """生成请求 ID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.utcnow().isoformat()


def format_duration(start_time: datetime, end_time: datetime) -> float:
    """计算持续时间（秒）"""
    return (end_time - start_time).total_seconds()


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
