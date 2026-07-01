"""
数据迁移工具：将 JSON 文件数据迁移到数据库

使用方法：
    python migrate_to_database.py
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.db.database import db_manager, ConversationModel, MessageModel
from config import settings


async def migrate_conversations():
    """迁移会话数据"""
    conversations_dir = Path("./data/conversations")
    
    if not conversations_dir.exists():
        logger.warning("No conversations directory found, nothing to migrate")
        return
    
    # 初始化数据库
    await db_manager.initialize()
    
    async with db_manager.get_session() as session:
        # 读取所有 JSON 文件
        json_files = list(conversations_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} conversation files to migrate")
        
        migrated = 0
        skipped = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否已存在
                result = await session.execute(
                    select(ConversationModel).where(ConversationModel.id == data['id'])
                )
                if result.scalar_one_or_none():
                    logger.info(f"Conversation {data['id']} already exists, skipping")
                    skipped += 1
                    continue
                
                # 创建会话记录
                created_at = data.get('created_at')
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                elif not created_at:
                    created_at = datetime.utcnow()
                
                updated_at = data.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = datetime.fromisoformat(updated_at)
                elif not updated_at:
                    updated_at = datetime.utcnow()
                
                conv_model = ConversationModel(
                    id=data['id'],
                    user_id=data['user_id'],
                    title=data['title'],
                    model=data['model'],
                    summary=data.get('summary'),
                    created_at=created_at,
                    updated_at=updated_at
                )
                session.add(conv_model)
                
                # 创建消息记录
                for msg_data in data.get('messages', []):
                    attachments_json = None
                    if msg_data.get('attachments'):
                        attachments_json = [
                            {
                                "id": att.get('id', ''),
                                "filename": att.get('filename', ''),
                                "content_type": att.get('content_type', ''),
                                "size": att.get('size', 0)
                            }
                            for att in msg_data['attachments']
                        ]
                    
                    msg_timestamp = msg_data.get('timestamp')
                    if isinstance(msg_timestamp, str):
                        msg_timestamp = datetime.fromisoformat(msg_timestamp)
                    elif not msg_timestamp:
                        msg_timestamp = datetime.utcnow()
                    
                    msg_model = MessageModel(
                        conversation_id=data['id'],
                        role=msg_data['role'],
                        content=msg_data['content'],
                        timestamp=msg_timestamp,
                        attachments=attachments_json
                    )
                    session.add(msg_model)
                
                migrated += 1
                logger.info(f"Migrated conversation: {data['id']}")
                
            except Exception as e:
                logger.error(f"Error migrating {json_file}: {str(e)}")
        
        await session.commit()
        
        logger.info(f"""
Migration completed!
- Migrated: {migrated}
- Skipped: {skipped}
- Total: {len(json_files)}
        """)


async def main():
    """主函数"""
    print("=" * 60)
    print("Data Migration Tool: JSON to Database")
    print("=" * 60)
    print()
    
    print(f"Database type: {settings.db_type}")
    print(f"Database URL: {settings.database_url}")
    print()
    
    confirm = input("Do you want to migrate data from JSON files to database? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Migration cancelled")
        return
    
    print()
    print("Starting migration...")
    print()
    
    try:
        await migrate_conversations()
        
        print()
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Verify data in database")
        print("2. Restart the application")
        print("3. Test conversation loading")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print()
        print("=" * 60)
        print("Migration failed!")
        print("=" * 60)
    
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
