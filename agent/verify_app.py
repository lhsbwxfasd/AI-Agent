"""
验证应用启动和主要接口
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("1. 测试导入...")
    try:
        from app.models.user import User
        from app.services.auth_service import auth_service
        from app.services.knowledge_service import KnowledgeService
        from app.services.mcp_service import MCPService
        from app.core.llm import LLMService
        from app.core.agent import AgentService
        print("   ✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

def test_user_model():
    print("2. 测试用户模型...")
    try:
        from app.models.user import User
        user = User(
            id=1,
            username="test",
            hashed_password="hashed123",
            preferred_model="deepseek-chat"
        )
        assert user.preferred_model == "deepseek-chat"
        print("   ✅ 用户模型正常")
        return True
    except Exception as e:
        print(f"   ❌ 用户模型失败: {e}")
        return False

def test_auth_service():
    print("3. 测试认证服务...")
    try:
        from app.services.auth_service import auth_service
        
        user = auth_service.get_user("admin")
        assert user is not None
        assert user.preferred_model == "deepseek-chat"
        
        authenticated = auth_service.authenticate_user("admin", "admin123")
        assert authenticated is not None
        
        model = auth_service.get_user_preferred_model("admin")
        assert model == "deepseek-chat"
        
        print("   ✅ 认证服务正常")
        return True
    except Exception as e:
        print(f"   ❌ 认证服务失败: {e}")
        return False

def test_config():
    print("4. 测试配置...")
    try:
        from config import settings
        assert settings.deepseek_api_key is not None
        assert settings.deepseek_base_url is not None
        print(f"   ✅ 配置正常 (DeepSeek API 已配置)")
        return True
    except Exception as e:
        print(f"   ❌ 配置失败: {e}")
        return False

def test_knowledge_service():
    print("5. 测试知识库服务...")
    try:
        from app.services.knowledge_service import KnowledgeService
        ks = KnowledgeService()
        print("   ✅ 知识库服务初始化成功")
        return True
    except Exception as e:
        print(f"   ❌ 知识库服务失败: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("开始验证应用...")
    print("="*50 + "\n")
    
    tests = [
        test_imports,
        test_user_model,
        test_auth_service,
        test_config,
        test_knowledge_service
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"验证完成: {passed}/{total} 通过")
    print("="*50 + "\n")
    
    if passed == total:
        print("✅ 所有验证通过！应用可以正常启动。")
        print("\n启动命令:")
        print("  python main.py")
        print("\n或使用快速启动脚本:")
        print("  .\\start.ps1")
        return 0
    else:
        print("❌ 部分验证失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
