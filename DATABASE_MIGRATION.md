# 数据库迁移说明

## 概述

已将会话数据存储从 JSON 文件迁移到数据库，支持：
- **开发环境**：SQLite (db.sqlite3)
- **生产环境**：MySQL

## 为什么需要迁移？

### JSON 文件存储的问题

❌ **不适合生产环境**：
- 无事务支持，数据一致性无法保证
- 并发访问性能差
- 无索引，查询效率低
- 文件锁问题
- 难以备份和恢复

✅ **数据库存储的优势**：
- ACID 事务，数据安全
- 高并发支持
- 索引优化，查询快速
- 支持复杂查询
- 易于备份和扩展

## 实现的功能

### 1. 数据库模型

#### 会话表 (conversations)
```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    model VARCHAR(100) NOT NULL,
    summary TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_user_id (user_id)
);
```

#### 消息表 (messages)
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    attachments JSON,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id)
);
```

#### 附件表 (attachments)
```sql
CREATE TABLE attachments (
    id VARCHAR(36) PRIMARY KEY,
    message_id INTEGER,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    size INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_content TEXT,
    user_id VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id)
);
```

### 2. 数据库连接管理

- 异步连接池
- 自动重连
- 连接健康检查
- 支持 SQLite 和 MySQL

### 3. 会话服务重写

使用 SQLAlchemy ORM：
- 异步数据库操作
- 事务支持
- 自动映射

## 配置说明

### 开发环境（SQLite）

`.env` 配置：
```bash
DB_TYPE=sqlite
DB_SQLITE_PATH=./data/db.sqlite3
```

**优点**：
- 无需安装数据库
- 零配置
- 适合开发测试

### 生产环境（MySQL）

`.env` 配置：
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=webuser
DB_PASSWORD=Webuser@123
DB_DATABASE=safedb
```

**优点**：
- 高性能
- 高可用
- 支持集群

## 使用步骤

### 1. 安装依赖

```bash
cd agent
pip install -r requirements.txt
```

新增依赖：
- `sqlalchemy==2.0.23` - ORM 框架
- `aiomysql==0.2.0` - 异步 MySQL 驱动
- `pymysql==1.1.0` - MySQL 驱动
- `aiosqlite==0.20.0` - 异步 SQLite 驱动

### 2. 迁移现有数据（可选）

如果有 JSON 格式的旧数据：

```bash
cd agent
python migrate_to_database.py
```

迁移工具会：
- 读取 `data/conversations/*.json`
- 导入到数据库
- 跳过已存在的数据
- 显示迁移统计

### 3. 启动应用

```bash
cd agent
python main.py
```

启动日志会显示：
```
INFO - Database initialized: sqlite
INFO - Database initialized successfully
```

### 4. 验证数据库

#### SQLite
```bash
# 查看数据库文件
ls -lh data/db.sqlite3

# 查询数据
sqlite3 data/db.sqlite3
sqlite> SELECT * FROM conversations;
sqlite> SELECT * FROM messages;
```

#### MySQL
```bash
# 连接数据库
mysql -u webuser -p safedb

# 查询数据
mysql> SELECT * FROM conversations;
mysql> SELECT * FROM messages;
mysql> SHOW INDEX FROM conversations;
```

## 数据库初始化

应用启动时自动：
1. 创建数据库连接
2. 创建表结构
3. 创建索引
4. 准备就绪

无需手动执行 SQL 脚本！

## 性能优化

### 1. 索引优化

已创建索引：
- `conversations.user_id` - 用户查询
- `messages.conversation_id` - 消息加载
- `attachments.message_id` - 附件查询
- `attachments.user_id` - 用户附件

### 2. 连接池

MySQL 配置：
- 连接池大小：自动
- 连接回收：3600 秒
- 健康检查：启用

### 3. 异步操作

所有数据库操作都是异步的：
- 不阻塞主线程
- 高并发支持
- 响应快速

## 数据迁移工具

### 功能

`migrate_to_database.py` 提供：
- ✅ 自动读取 JSON 文件
- ✅ 批量导入数据库
- ✅ 数据验证
- ✅ 错误处理
- ✅ 进度显示
- ✅ 重复检测

### 使用

```bash
cd agent
python migrate_to_database.py
```

输出示例：
```
============================================================
Data Migration Tool: JSON to Database
============================================================

Database type: sqlite
Database URL: sqlite+aiosqlite:///./data/db.sqlite3

Do you want to migrate data from JSON files to database? (yes/no): yes

Starting migration...

Found 10 conversation files to migrate
Migrated conversation: abc-123-def
Migrated conversation: xyz-456-uvw
...

Migration completed!
- Migrated: 10
- Skipped: 0
- Total: 10

============================================================
Migration completed successfully!
============================================================
```

## 备份和恢复

### SQLite

**备份**：
```bash
# 直接复制文件
cp data/db.sqlite3 data/db.sqlite3.backup

# 或使用 sqlite3
sqlite3 data/db.sqlite3 ".backup 'data/db.backup'"
```

**恢复**：
```bash
cp data/db.sqlite3.backup data/db.sqlite3
```

### MySQL

**备份**：
```bash
mysqldump -u webuser -p safedb > backup.sql
```

**恢复**：
```bash
mysql -u webuser -p safedb < backup.sql
```

## 常见问题

### Q1: 数据库连接失败？

**SQLite**：
```bash
# 检查文件权限
ls -l data/db.sqlite3

# 创建数据目录
mkdir -p data
```

**MySQL**：
```bash
# 检查 MySQL 服务
systemctl status mysql

# 检查连接
mysql -u webuser -p -h localhost safedb

# 检查用户权限
mysql> SHOW GRANTS FOR 'webuser'@'localhost';
```

### Q2: 表不存在？

应用启动时会自动创建表。如果手动创建：

```python
from app.db.database import db_manager, Base
import asyncio

async def create_tables():
    await db_manager.initialize()
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
```

### Q3: 如何切换数据库？

修改 `.env`：
```bash
# SQLite
DB_TYPE=sqlite

# 或 MySQL
DB_TYPE=mysql
```

重启应用即可。

### Q4: 旧数据如何处理？

JSON 文件不会被删除，可以：
- 保留作为备份
- 迁移后手动删除
- 保留一份存档

## 文件结构

```
agent/
├── app/
│   ├── db/
│   │   └── database.py          # 数据库管理
│   ├── services/
│   │   └── conversation_service.py  # 会话服务（数据库版）
│   └── models/
│       └── conversation.py      # 数据模型
├── data/
│   ├── db.sqlite3              # SQLite 数据库
│   └── conversations/          # 旧 JSON 文件（可选保留）
├── migrate_to_database.py      # 迁移工具
├── .env                        # 配置文件
└── requirements.txt            # 依赖列表
```

## 生产环境部署

### 1. MySQL 准备

```sql
-- 创建数据库
CREATE DATABASE safedb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'Webuser@123';

-- 授权
GRANT ALL PRIVILEGES ON safedb.* TO 'webuser'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 配置

`.env`：
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=webuser
DB_PASSWORD=Webuser@123
DB_DATABASE=safedb
```

### 3. 启动

```bash
python main.py
```

### 4. 监控

```sql
-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';

-- 查看表大小
SELECT 
    table_name,
    table_rows,
    ROUND(data_length/1024/1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'safedb';
```

## 总结

✅ **已完成**：
- 数据库模型设计
- 连接管理实现
- 会话服务重写
- 数据迁移工具
- 配置文件更新

✅ **优势**：
- 生产级数据库存储
- 支持高并发
- 数据一致性保证
- 易于备份恢复
- 支持复杂查询

✅ **向后兼容**：
- 保留 JSON 文件
- 提供迁移工具
- 无缝切换数据库

现在会话数据安全存储在数据库中！🎉
