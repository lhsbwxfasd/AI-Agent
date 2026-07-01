from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.services.attachment_service import attachment_service
from app.middleware.auth import get_current_user_id
from loguru import logger

router = APIRouter()

@router.post("/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user_id)
):
    """上传附件并解析内容"""
    try:
        result = await attachment_service.upload_and_parse(file, current_user)
        attachment_data = {
            "id": result['id'],
            "filename": result['filename'],
            "content_type": result['content_type'],
            "size": result['size'],
            "parsed_content": result['parsed_content']
        }
        
        # 如果有base64数据，也返回
        if result.get('raw_content_base64'):
            attachment_data['raw_content_base64'] = result['raw_content_base64']
        
        return {
            "success": True,
            "attachment": attachment_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Attachment upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/multiple")
async def upload_multiple_attachments(
    files: List[UploadFile] = File(...),
    current_user: str = Depends(get_current_user_id)
):
    """批量上传附件"""
    try:
        results = []
        for file in files:
            try:
                result = await attachment_service.upload_and_parse(file, current_user)
                results.append({
                    "id": result['id'],
                    "filename": result['filename'],
                    "content_type": result['content_type'],
                    "size": result['size'],
                    "parsed_content": result['parsed_content']
                })
            except Exception as e:
                logger.error(f"Error uploading {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "attachments": results
        }
    except Exception as e:
        logger.error(f"Multiple attachment upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: str,
    current_user: str = Depends(get_current_user_id)
):
    """删除附件"""
    try:
        success = attachment_service.delete_attachment(attachment_id)
        if success:
            return {"success": True, "message": "附件已删除"}
        else:
            raise HTTPException(status_code=404, detail="附件不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Attachment deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
