"""
预置知识库初始化脚本
用于初始化企业常用知识库内容
"""
import asyncio
import sys
import os
from pathlib import Path

# 设置 HuggingFace 镜像（解决网络问题）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.knowledge_service import knowledge_service
from loguru import logger


# 预置知识库内容
PRESET_KNOWLEDGE = [
    {
        "content": """公司简介
我们是一家专注于人工智能技术研发的创新企业，致力于为企业提供智能化的解决方案。
公司成立于2020年，总部位于北京，在上海、深圳设有分公司。
主要业务包括：AI咨询服务、智能客服系统、数据分析平台、企业级Agent解决方案。
公司愿景：让AI赋能每一个企业。
核心价值观：创新、诚信、合作、共赢。""",
        "metadata": {"source": "company_info", "category": "公司介绍"}
    },
    {
        "content": """产品服务
1. 智能客服系统：基于大语言模型的智能对话系统，支持多轮对话、知识库检索、情感分析。
2. 数据分析平台：企业级数据分析解决方案，支持实时数据处理、可视化报表、预测分析。
3. AI咨询服务：提供AI战略规划、技术选型、团队建设等全方位咨询服务。
4. 企业级Agent：支持知识库、MCP工具、流式响应的企业级AI助手平台。

技术特点：
- 支持多种大模型（GPT-4、Claude等）
- 企业私有知识库集成
- MCP协议工具扩展
- 流式响应提升体验
- 完善的权限管理""",
        "metadata": {"source": "products", "category": "产品服务"}
    },
    {
        "content": """技术架构
后端技术栈：
- 框架：FastAPI
- 异步运行时：asyncio + uvicorn
- 向量数据库：ChromaDB
- LLM集成：LangChain
- 认证：JWT + OAuth2
- 日志：loguru

前端技术栈：
- 框架：React/Vue
- 状态管理：Redux/Pinia
- UI组件：Ant Design/Element Plus
- 实时通信：WebSocket/SSE

部署架构：
- 容器化：Docker + Docker Compose
- 反向代理：Nginx
- 负载均衡：Nginx/Kubernetes
- 监控：Prometheus + Grafana""",
        "metadata": {"source": "tech_stack", "category": "技术架构"}
    },
    {
        "content": """开发规范
代码规范：
- Python：遵循PEP 8规范
- JavaScript：遵循ES6+规范
- 使用类型注解提高代码可读性
- 编写单元测试保证代码质量

Git工作流：
- 主分支：main（生产环境）
- 开发分支：develop（开发环境）
- 功能分支：feature/xxx（新功能开发）
- 修复分支：fix/xxx（bug修复）

提交规范：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关""",
        "metadata": {"source": "dev_standards", "category": "开发规范"}
    },
    {
        "content": """常见问题FAQ
Q1: 如何获取API密钥？
A: 登录管理后台，在"API管理"页面申请API密钥。

Q2: 支持哪些模型？
A: 目前支持GPT-4、GPT-3.5-Turbo、Claude-3-Opus、Claude-3-Sonnet等主流模型。

Q3: 如何集成知识库？
A: 通过知识库管理API上传文档，系统会自动进行向量化处理。

Q4: 支持哪些文件格式？
A: 支持PDF、DOCX、TXT等常见文本格式。

Q5: 如何设置模型偏好？
A: 在用户设置中选择偏好模型，系统会记住您的选择。

Q6: 对话历史保存多久？
A: 对话历史永久保存，您可以随时查看和管理。

Q7: 支持多用户吗？
A: 支持，每个用户的数据相互隔离，确保隐私安全。

Q8: 如何部署到生产环境？
A: 参考部署文档，使用Docker Compose或Kubernetes进行部署。""",
        "metadata": {"source": "faq", "category": "常见问题"}
    },
    {
        "content": """使用指南
快速开始：
1. 注册账号并登录
2. 获取API密钥
3. 选择模型开始对话
4. 上传知识库文档（可选）
5. 配置MCP工具（可选）

高级功能：
- 会话管理：创建、编辑、删除会话
- 知识库：上传文档、向量检索
- 模型切换：根据需求选择不同模型
- 工具调用：通过MCP协议调用外部工具
- 流式响应：实时获取AI回复

最佳实践：
- 合理使用知识库提升回答准确性
- 根据任务复杂度选择合适的模型
- 定期清理不需要的会话
- 善用工具调用扩展AI能力""",
        "metadata": {"source": "user_guide", "category": "使用指南"}
    },
    {
        "content": """安全与隐私
数据安全：
- 所有数据传输采用HTTPS加密
- 敏感信息采用AES-256加密存储
- 定期进行安全审计和渗透测试

隐私保护：
- 严格遵守相关法律法规
- 用户数据所有权归用户所有
- 不会未经授权使用用户数据
- 提供数据导出和删除功能

访问控制：
- 基于角色的权限管理
- API密钥认证
- 操作日志审计
- 异常行为监控

合规性：
- 符合GDPR要求
- 符合网络安全法要求
- 定期进行合规性审查""",
        "metadata": {"source": "security", "category": "安全隐私"}
    },
    {
        "content": """技术支持
支持渠道：
- 在线文档：docs.example.com
- 技术论坛：forum.example.com
- 邮件支持：support@example.com
- 电话支持：400-XXX-XXXX（工作时间）

服务时间：
- 在线支持：7x24小时
- 邮件响应：24小时内
- 电话支持：工作日9:00-18:00

SLA保障：
- 系统可用性：99.9%
- 响应时间：< 100ms
- 数据备份：每日自动备份""",
        "metadata": {"source": "support", "category": "技术支持"}
    }
]


async def init_knowledge_base():
    """初始化知识库"""
    logger.info("开始初始化知识库...")
    
    try:
        # 批量添加文档
        documents = [item["content"] for item in PRESET_KNOWLEDGE]
        metadatas = [item["metadata"] for item in PRESET_KNOWLEDGE]
        
        result = await knowledge_service.add_documents(
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"知识库初始化完成：{result}")
        
        # 获取集合信息
        info = await knowledge_service.get_collection_info()
        logger.info(f"当前知识库信息：{info}")
        
        return result
        
    except Exception as e:
        logger.error(f"知识库初始化失败：{str(e)}")
        raise


async def main():
    """主函数"""
    try:
        await init_knowledge_base()
        logger.success("知识库初始化成功！")
    except Exception as e:
        logger.error(f"初始化失败：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
