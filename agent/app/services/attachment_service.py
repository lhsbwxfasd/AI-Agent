import os
import uuid
import base64
from typing import Dict, Optional, Tuple
from io import BytesIO
from fastapi import UploadFile, HTTPException
from loguru import logger
import PyPDF2
import docx
from PIL import Image

try:
    import pytesseract
    
    # Windows 系统显式设置 Tesseract 路径
    if os.name == 'nt':  # Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Tesseract-OCR', 'tesseract.exe'),
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract OCR path set to: {path}")
                break
        else:
            # 尝试从环境变量 PATH 中查找
            path_env = os.environ.get('PATH', '')
            for path_dir in path_env.split(os.pathsep):
                tesseract_exe = os.path.join(path_dir, 'tesseract.exe')
                if os.path.exists(tesseract_exe):
                    pytesseract.pytesseract.tesseract_cmd = tesseract_exe
                    logger.info(f"Tesseract OCR found in PATH: {tesseract_exe}")
                    break
    
    # 测试 Tesseract 是否可用
    try:
        version = pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        logger.info(f"Tesseract OCR initialized successfully, version: {version}")
    except Exception as e:
        TESSERACT_AVAILABLE = False
        logger.warning(f"Tesseract OCR not available: {str(e)}")
        
except Exception as e:
    TESSERACT_AVAILABLE = False
    logger.warning(f"Tesseract import failed: {str(e)}")

class AttachmentService:
    def __init__(self):
        self.upload_dir = "data/attachments"
        os.makedirs(self.upload_dir, exist_ok=True)
        
        self.supported_types = {
            'application/pdf': self._parse_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._parse_docx,
            'text/plain': self._parse_txt,
            'image/jpeg': self._parse_image,
            'image/png': self._parse_image,
            'image/gif': self._parse_image,
            'image/webp': self._parse_image
        }
        
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def upload_and_parse(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> Dict:
        """上传并解析文件"""
        try:
            content_type = file.content_type
            if content_type not in self.supported_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"不支持的文件类型: {content_type}"
                )
            
            file_content = await file.read()
            if len(file_content) > self.max_file_size:
                raise HTTPException(
                    status_code=400, 
                    detail=f"文件大小超过限制（最大{self.max_file_size // 1024 // 1024}MB）"
                )
            
            file_id = str(uuid.uuid4())
            file_ext = os.path.splitext(file.filename)[1]
            file_path = os.path.join(self.upload_dir, f"{file_id}{file_ext}")
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            parse_func = self.supported_types[content_type]
            parsed_content = await parse_func(file_content, file.filename)
            
            result = {
                'id': file_id,
                'filename': file.filename,
                'content_type': content_type,
                'size': len(file_content),
                'path': file_path,
                'parsed_content': parsed_content,
                'user_id': user_id,
                'raw_content_base64': None
            }
            
            # 如果是图片且OCR不可用，保存base64以便后续使用视觉模型
            if content_type.startswith('image/') and not TESSERACT_AVAILABLE:
                result['raw_content_base64'] = base64.b64encode(file_content).decode('utf-8')
            
            logger.info(f"File uploaded and parsed: {file.filename} ({file_id})")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    async def _parse_pdf(self, content: bytes, filename: str) -> str:
        """解析PDF文件"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_content.append(text.strip())
            
            result = "\n\n".join(text_content)
            logger.info(f"Parsed PDF {filename}: {len(result)} chars")
            return f"[PDF文件: {filename}]\n\n{result}"
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            return f"[PDF文件: {filename}]\n\n解析失败: {str(e)}"
    
    async def _parse_docx(self, content: bytes, filename: str) -> str:
        """解析DOCX文件"""
        try:
            doc_file = BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text.strip())
            
            result = "\n\n".join(text_content)
            logger.info(f"Parsed DOCX {filename}: {len(result)} chars")
            return f"[Word文档: {filename}]\n\n{result}"
            
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return f"[Word文档: {filename}]\n\n解析失败: {str(e)}"
    
    async def _parse_txt(self, content: bytes, filename: str) -> str:
        """解析TXT文件"""
        try:
            text = content.decode('utf-8')
            logger.info(f"Parsed TXT {filename}: {len(text)} chars")
            return f"[文本文件: {filename}]\n\n{text}"
            
        except UnicodeDecodeError:
            try:
                text = content.decode('gbk')
                logger.info(f"Parsed TXT {filename}: {len(text)} chars")
                return f"[文本文件: {filename}]\n\n{text}"
            except Exception as e:
                logger.error(f"Error parsing TXT: {str(e)}")
                return f"[文本文件: {filename}]\n\n解析失败: {str(e)}"
        except Exception as e:
            logger.error(f"Error parsing TXT: {str(e)}")
            return f"[文本文件: {filename}]\n\n解析失败: {str(e)}"
    
    async def _parse_image(self, content: bytes, filename: str) -> str:
        """解析图片文件（OCR）"""
        try:
            image = Image.open(BytesIO(content))
            
            # 尝试使用 Tesseract OCR
            if TESSERACT_AVAILABLE:
                try:
                    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                    if text.strip():
                        logger.info(f"Parsed image {filename} with OCR: {len(text)} chars")
                        return f"[图片: {filename}]\n\n图片中的文字内容:\n{text.strip()}"
                    else:
                        logger.info(f"No text detected in image {filename}")
                        return f"[图片: {filename}]\n\n(图片已上传，但未检测到文字内容。如果图片包含图表或视觉内容，请描述您想了解的信息)"
                except Exception as ocr_error:
                    logger.warning(f"OCR failed for {filename}: {str(ocr_error)}")
            
            # OCR 不可用时的降级方案
            logger.info(f"Tesseract OCR not available for {filename}, using fallback")
            return f"[图片: {filename}]\n\n【重要提示】\n图片已成功上传，但 OCR 文字识别功能不可用。\n\n可能的原因：\n1. Tesseract OCR 未安装\n2. 系统环境变量未配置\n\n解决方案：\n- 方案1：安装 Tesseract OCR（推荐）\n  下载地址：https://github.com/UB-Mannheim/tesseract/wiki\n  安装后重启服务\n\n- 方案2：使用视觉模型\n  如果您的问题需要理解图片内容，建议：\n  • 切换到支持视觉的模型（如 GPT-4V、Claude Vision）\n  • 或手动描述图片内容\n\n当前您可以：\n• 描述您想从图片中获取什么信息\n• 我会尽力基于您的描述提供帮助"
                
        except Exception as e:
            logger.error(f"Error parsing image: {str(e)}")
            return f"[图片: {filename}]\n\n解析失败: {str(e)}"
    
    def get_attachment_path(self, file_id: str) -> Optional[str]:
        """获取附件路径"""
        for ext in ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.webp']:
            path = os.path.join(self.upload_dir, f"{file_id}{ext}")
            if os.path.exists(path):
                return path
        return None
    
    def delete_attachment(self, file_id: str) -> bool:
        """删除附件"""
        path = self.get_attachment_path(file_id)
        if path and os.path.exists(path):
            os.remove(path)
            logger.info(f"Attachment deleted: {file_id}")
            return True
        return False

attachment_service = AttachmentService()
