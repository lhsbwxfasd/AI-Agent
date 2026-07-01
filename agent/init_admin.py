"""
初始化管理员用户脚本

使用方法：
    python init_admin.py
"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import db_manager, UserModel
from app.services.user_service import user_service
from sqlalchemy import select
from loguru import logger


async def init_admin():
    """初始化管理员用户"""
    
    print("=" * 60)
    print("Initialize Admin User")
    print("=" * 60)
    print()
    
    # 初始化数据库
    print("1. Initializing database...")
    await db_manager.initialize()
    print("   ✅ Database initialized")
    print()
    
    # 检查管理员是否已存在
    print("2. Checking if admin exists...")
    async with db_manager.get_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.username == "admin")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            print("   ⚠️  Admin user already exists")
            print(f"      Username: {admin.username}")
            print(f"      Email: {admin.email}")
            print()
            
            update = input("Do you want to update admin password? (yes/no): ")
            if update.lower() == 'yes':
                new_password = input("Enter new password: ")
                admin.password_hash = user_service.get_password_hash(new_password)
                await session.commit()
                print("   ✅ Admin password updated")
            else:
                print("   ℹ️  No changes made")
        else:
            print("   ℹ️  Admin user does not exist")
            print()
            
            # 创建管理员
            print("3. Creating admin user...")
            password = input("Enter admin password (default: admin123): ") or "admin123"
            email = input("Enter admin email (optional): ") or None
            
            try:
                user = await user_service.register(
                    username="admin",
                    password=password,
                    email=email,
                    full_name="Administrator"
                )
                
                # 设置为管理员
                async with db_manager.get_session() as session:
                    result = await session.execute(
                        select(UserModel).where(UserModel.username == "admin")
                    )
                    admin_user = result.scalar_one_or_none()
                    if admin_user:
                        admin_user.is_admin = 1
                        await session.commit()
                
                print("   ✅ Admin user created successfully")
                print(f"      Username: admin")
                print(f"      Password: {password}")
                if email:
                    print(f"      Email: {email}")
                
            except Exception as e:
                print(f"   ❌ Failed to create admin: {e}")
    
    print()
    print("=" * 60)
    print("Initialization completed!")
    print("=" * 60)
    print()
    print("You can now login with:")
    print("  Username: admin")
    print("  Password: [the password you set]")
    print()
    
    # 关闭数据库
    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(init_admin())
