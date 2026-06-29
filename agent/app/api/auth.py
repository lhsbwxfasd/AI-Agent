from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger

from app.models.user import UserLogin, Token, User
from app.services.auth_service import auth_service

router = APIRouter()


async def get_current_user() -> str:
    """获取当前用户（简化版，实际应从JWT token中获取）"""
    return "admin"


@router.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    """用户登录"""
    try:
        result = await auth_service.login(user_data.username, user_data.password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """获取当前用户信息"""
    user = auth_service.get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me/preferred-model")
async def update_preferred_model(
    preferred_model: str,
    current_user: str = Depends(get_current_user)
):
    """更新用户偏好模型"""
    try:
        user = auth_service.update_user_preferred_model(current_user, preferred_model)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User {current_user} updated preferred model to {preferred_model}")
        return {"message": "Preferred model updated", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferred model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
