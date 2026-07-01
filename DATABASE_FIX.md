# 数据库问题修复说明

## 问题原因

错误：`'>' not supported between instances of 'NoneType' and 'int'`

**原因**：SQLite 不支持 MySQL 的连接池参数（pool_pre_ping, pool_recycle），传递 None 导致比较错误。

## 已修复

### 1. database.py - 分离配置

```python
if settings.db_type == "mysql":
    # MySQL 使用连接池参数
    self.engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    # SQLite 不使用连接池参数
    self.engine = create_async_engine(
        settings.database_url,
        echo=settings.debug
    )
```

### 2. migrate_to_database.py - 改进时间戳处理

处理各种时间戳格式：
- ISO 字符串
- datetime 对象
- None 值

## 现在请按顺序执行

### 步骤1：测试数据库

```bash
cd agent
python test_database.py
```

预期输出：
```
============================================================
Database Test Script
============================================================

1. Initializing database...
   ✅ Database initialized successfully

2. Testing conversation insert...
   ✅ Conversation inserted successfully

3. Testing conversation query...
   ✅ Found conversation: Test Conversation

4. Testing message insert...
   ✅ Message inserted successfully

5. Testing message query...
   ✅ Found 1 message(s)

6. Cleaning up test data...
   ✅ Test data cleaned up

7. Closing database connection...
   ✅ Connection closed

============================================================
All tests passed! Database is working correctly.
============================================================
```

### 步骤2：迁移数据（如果有旧数据）

```bash
python migrate_to_database.py
```

### 步骤3：启动应用

```bash
python main.py
```

## 验证数据库

### SQLite

```bash
# 查看数据库文件
ls -l data/db.sqlite3

# 查询数据
sqlite3 data/db.sqlite3 "SELECT * FROM conversations;"
sqlite3 data/db.sqlite3 "SELECT * FROM messages;"
```

### MySQL

```bash
mysql -u webuser -p safedb
mysql> SELECT * FROM conversations;
mysql> SELECT * FROM messages;
```

## 如果仍有问题

### 检查依赖

```bash
pip list | grep -E "sqlalchemy|aiomysql|aiosqlite"
```

应该看到：
- sqlalchemy (2.0.23)
- aiomysql (0.2.0)
- aiosqlite (0.20.0)
- pymysql (1.1.0)

### 检查配置

```bash
cat .env | grep DB_
```

应该看到：
```
DB_TYPE=sqlite
DB_SQLITE_PATH=./data/db.sqlite3
```

### 查看详细错误

修改 `.env`：
```bash
DEBUG=True
```

重新运行，查看详细日志。

## 完成标志

当看到以下日志时，表示成功：

```
INFO - Database initialized: sqlite
INFO - Database initialized successfully
INFO - Starting Enterprise Agent Backend v1.0.0
```

现在请运行 `python test_database.py` 测试数据库！
