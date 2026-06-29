from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import PyPDF2
import docx
from io import BytesIO

from app.services.knowledge_service import knowledge_service
from loguru import logger

router = APIRouter()


@router.post("/documents")
async def add_document(
    content: str,
    metadata: Optional[dict] = None,
    doc_id: Optional[str] = None
):
    """添加文本文档"""
    try:
        result = await knowledge_service.add_documents(
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id] if doc_id else None
        )
        return result
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch")
async def add_documents_batch(documents: List[dict]):
    """批量添加文档"""
    try:
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata") for doc in documents]
        ids = [doc.get("id") for doc in documents]
        
        result = await knowledge_service.add_documents(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        return result
    except Exception as e:
        logger.error(f"Error adding documents batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    source: Optional[str] = None
):
    """上传文件并添加到知识库"""
    try:
        content = await file.read()
        
        # 根据文件类型解析
        if file.filename.endswith('.pdf'):
            text = await extract_text_from_pdf(content)
        elif file.filename.endswith('.docx'):
            text = await extract_text_from_docx(content)
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        result = await knowledge_service.add_documents(
            documents=[text],
            metadatas=[{"source": source or file.filename}],
            ids=None
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents")
async def delete_documents(ids: List[str]):
    """删除文档"""
    try:
        result = await knowledge_service.delete_documents(ids)
        return result
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_knowledge_info():
    """获取知识库信息"""
    try:
        result = await knowledge_service.get_collection_info()
        return result
    except Exception as e:
        logger.error(f"Error getting knowledge info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def extract_text_from_pdf(content: bytes) -> str:
    """从 PDF 提取文本"""
    pdf_file = BytesIO(content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    return text


async def extract_text_from_docx(content: bytes) -> str:
    """从 DOCX 提取文本"""
    doc_file = BytesIO(content)
    doc = docx.Document(doc_file)
    
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    return text
