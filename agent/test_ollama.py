"""
测试 Ollama 模型集成
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ollama_connection():
    """测试 Ollama 服务连接"""
    print("1. 测试 Ollama 服务连接...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"   ✅ Ollama 服务正常，已安装 {len(models)} 个模型")
                for model in models:
                    print(f"      - {model['name']}")
                return True
            else:
                print(f"   ❌ Ollama 服务响应异常: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ 无法连接到 Ollama 服务: {e}")
        print("   请确保 Ollama 正在运行: ollama serve")
        return False

def test_config():
    """测试配置"""
    print("\n2. 测试配置...")
    try:
        from config import settings
        
        print(f"   Ollama Base URL: {settings.ollama_base_url}")
        
        if "deepseek-r1:7b" in settings.available_models:
            model_config = settings.available_models["deepseek-r1:7b"]
            print(f"   ✅ deepseek-r1:7b 模型已配置")
            print(f"      - 名称: {model_config['name']}")
            print(f"      - 提供者: {model_config['provider']}")
            print(f"      - 最大 tokens: {model_config['max_tokens']}")
            return True
        else:
            print("   ❌ deepseek-r1:7b 模型未配置")
            return False
    except Exception as e:
        print(f"   ❌ 配置测试失败: {e}")
        return False

async def test_llm_service():
    """测试 LLM 服务"""
    print("\n3. 测试 LLM 服务...")
    try:
        from app.core.llm import llm_service
        
        models = llm_service.get_available_models()
        print(f"   可用模型数量: {len(models)}")
        
        if "deepseek-r1:7b" in models:
            print("   ✅ deepseek-r1:7b 在可用模型列表中")
            
            # 测试获取 LLM 实例
            llm = llm_service._get_llm("deepseek-r1:7b")
            print(f"   ✅ LLM 实例创建成功")
            print(f"      - 模型: {llm.model_name}")
            print(f"      - Base URL: {llm.openai_api_base}")
            return True
        else:
            print("   ❌ deepseek-r1:7b 不在可用模型列表中")
            return False
    except Exception as e:
        print(f"   ❌ LLM 服务测试失败: {e}")
        return False

async def test_chat():
    """测试聊天功能"""
    print("\n4. 测试聊天功能...")
    try:
        from app.core.llm import llm_service
        
        print("   发送测试消息: '你好，请简单介绍一下你自己'")
        
        messages = [{"role": "user", "content": "你好，请简单介绍一下你自己"}]
        
        response = await llm_service.chat(
            messages=messages,
            model="deepseek-r1:7b"
        )
        
        print(f"   ✅ 收到响应:")
        print(f"      {response[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ 聊天测试失败: {e}")
        return False

async def main():
    print("\n" + "="*60)
    print("Ollama 模型集成测试")
    print("="*60)
    
    tests = [
        test_ollama_connection(),
        test_config(),
        test_llm_service(),
        test_chat()
    ]
    
    results = []
    for test in tests:
        if asyncio.iscoroutine(test):
            result = await test
        else:
            result = test
        results.append(result)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"测试完成: {passed}/{total} 通过")
    print("="*60 + "\n")
    
    if passed == total:
        print("✅ 所有测试通过！Ollama 模型集成成功。")
        print("\n使用方法:")
        print("1. 启动后端: python main.py")
        print("2. 启动前端: cd ../web && npm run dev")
        print("3. 在前端选择 'DeepSeek R1 7B (Ollama)' 模型")
        return 0
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        if results[0] == False:
            print("\n提示: 请确保 Ollama 服务正在运行")
            print("  启动命令: ollama serve")
            print("  拉取模型: ollama pull deepseek-r1:7b")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
