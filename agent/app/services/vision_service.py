import base64
from typing import Optional
from io import BytesIO
from PIL import Image
from loguru import logger
from config import settings

class VisionService:
    def __init__(self):
        self.supported_vision_models = {
            'gpt-4-vision-preview',
            'gpt-4o',
            'gpt-4o-mini',
            'claude-3-opus',
            'claude-3-sonnet',
            'claude-3-haiku',
            'gemini-pro-vision'
        }
    
    def is_vision_model(self, model: str) -> bool:
        """检查模型是否支持视觉"""
        return any(vision_model in model.lower() for vision_model in self.supported_vision_models)
    
    async def analyze_image_with_vision_model(
        self,
        image_content: bytes,
        filename: str,
        question: str,
        model: str
    ) -> Optional[str]:
        """使用视觉模型分析图片"""
        try:
            from app.core.llm import llm_service
            
            if not self.is_vision_model(model):
                logger.info(f"Model {model} does not support vision")
                return None
            
            # 转换图片为 base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # 获取图片格式
            image = Image.open(BytesIO(image_content))
            image_format = image.format.lower() if image.format else 'png'
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question or "请详细描述这张图片的内容。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用视觉模型
            response = await llm_service.chat(
                messages=messages,
                model=model
            )
            
            logger.info(f"Vision model {model} analyzed image {filename}")
            return response
            
        except Exception as e:
            logger.error(f"Vision model analysis failed: {str(e)}")
            return None

vision_service = VisionService()
