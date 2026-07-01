from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.services.user_service import user_service
from app.middleware.auth import get_current_user_id
from loguru import logger

router = APIRouter()


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=200, description="姓名")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=200, description="姓名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    preferred_model: Optional[str] = Field(None, description="偏好模型")


@router.post("/register")
async def register(user_data: UserRegister):
    """用户注册"""
    try:
        result = await user_service.register(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name
        )
        return {"success": True, "user": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="注册失败")


@router.post("/login")
async def login(user_data: UserLogin):
    """用户登录"""
    try:
        result = await user_service.login(
            username=user_data.username,
            password=user_data.password
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="登录失败")


@router.get("/me")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """获取当前用户信息"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/me")
async def update_current_user(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """更新当前用户信息"""
    try:
        result = await user_service.update_user(
            user_id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
            preferred_model=user_data.preferred_model
        )
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"success": True, "user": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        raise HTTPException(status_code=500, detail="更新失败")


@router.get("/list")
async def list_users(user_id: str = Depends(get_current_user_id)):
    """获取用户列表（管理员功能）"""
    # TODO: 添加管理员权限检查
    users = await user_service.list_users()
    return {"users": users}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """禁用用户（管理员功能）"""
    # TODO: 添加管理员权限检查
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"success": True, "message": "用户已禁用"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """激活用户（管理员功能）"""
    # TODO: 添加管理员权限检查
    success = await user_service.activate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"success": True, "message": "用户已激活"}
