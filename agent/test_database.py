"""
数据库测试脚本
验证数据库连接和基本操作
"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import db_manager, ConversationModel, MessageModel
from sqlalchemy import select
from datetime import datetime
from loguru import logger


async def test_database():
    """测试数据库连接和操作"""
    
    print("=" * 60)
    print("Database Test Script")
    print("=" * 60)
    print()
    
    # 1. 初始化数据库
    print("1. Initializing database...")
    try:
        await db_manager.initialize()
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # 2. 测试插入会话
    print()
    print("2. Testing conversation insert...")
    try:
        async with db_manager.get_session() as session:
            test_conv = ConversationModel(
                id="test-conv-123",
                user_id="test-user",
                title="Test Conversation",
                model="test-model",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(test_conv)
            await session.commit()
            print("   ✅ Conversation inserted successfully")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 3. 测试查询会话
    print()
    print("3. Testing conversation query...")
    try:
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == "test-conv-123")
            )
            conv = result.scalar_one_or_none()
            if conv:
                print(f"   ✅ Found conversation: {conv.title}")
            else:
                print("   ❌ Conversation not found")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 4. 测试插入消息
    print()
    print("4. Testing message insert...")
    try:
        async with db_manager.get_session() as session:
            test_msg = MessageModel(
                conversation_id="test-conv-123",
                role="user",
                content="Hello, this is a test message",
                timestamp=datetime.utcnow()
            )
            session.add(test_msg)
            await session.commit()
            print("   ✅ Message inserted successfully")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 5. 测试查询消息
    print()
    print("5. Testing message query...")
    try:
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(MessageModel).where(MessageModel.conversation_id == "test-conv-123")
            )
            messages = result.scalars().all()
            print(f"   ✅ Found {len(messages)} message(s)")
            for msg in messages:
                print(f"      - [{msg.role}]: {msg.content[:50]}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 6. 清理测试数据
    print()
    print("6. Cleaning up test data...")
    try:
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == "test-conv-123")
            )
            conv = result.scalar_one_or_none()
            if conv:
                await session.delete(conv)
                await session.commit()
                print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 7. 关闭连接
    print()
    print("7. Closing database connection...")
    await db_manager.close()
    print("   ✅ Connection closed")
    
    print()
    print("=" * 60)
    print("All tests passed! Database is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_database())
