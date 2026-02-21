"""
Ollama 诊断脚本 - 找出 502 错误的原因
"""

import requests
import json

print("=" * 60)
print("🔍 Ollama 诊断工具")
print("=" * 60)

# 测试 1: 检查 Ollama 服务
print("\n📡 测试 1: 检查 Ollama 服务...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("✅ Ollama 服务正常运行")
        data = response.json()
        models = data.get("models", [])
        print(f"   已安装 {len(models)} 个模型:")
        for model in models:
            print(f"   - {model['name']}")
    else:
        print(f"❌ Ollama 服务响应异常: {response.status_code}")
except Exception as e:
    print(f"❌ 无法连接 Ollama: {e}")
    exit(1)

# 测试 2: 使用 Ollama 原生 API
print("\n📡 测试 2: 测试 Ollama 原生 API...")
try:
    payload = {
        "model": "qwen2.5:latest",
        "messages": [
            {"role": "user", "content": "Say hello"}
        ],
        "stream": False
    }
    
    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        print("✅ Ollama 原生 API 正常")
        result = response.json()
        content = result.get("message", {}).get("content", "")
        print(f"   回复: {content[:100]}")
    else:
        print(f"❌ Ollama 原生 API 失败: {response.status_code}")
        print(f"   响应: {response.text[:200]}")
except Exception as e:
    print(f"❌ Ollama 原生 API 错误: {e}")

# 测试 3: 使用 OpenAI SDK 调用 Ollama (OpenAI-compatible API)
print("\n📡 测试 3: 测试 OpenAI 兼容 API...")
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key="ollama",  # dummy key
        base_url="http://localhost:11434/v1"
    )
    
    print("   正在调用 OpenAI 兼容接口...")
    response = client.chat.completions.create(
        model="qwen2.5:latest",
        messages=[
            {"role": "user", "content": "Say hello"}
        ],
        stream=False
    )
    
    print("✅ OpenAI 兼容 API 正常")
    print(f"   回复: {response.choices[0].message.content[:100]}")
    
except ImportError:
    print("⚠️  OpenAI SDK 未安装")
    print("   运行: pip install openai")
except Exception as e:
    print(f"❌ OpenAI 兼容 API 错误: {e}")
    import traceback
    print("\n详细错误:")
    traceback.print_exc()

# 测试 4: 测试带 JSON 格式要求的请求
print("\n📡 测试 4: 测试 JSON 格式响应...")
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )
    
    print("   正在请求 JSON 格式响应...")
    response = client.chat.completions.create(
        model="qwen2.5:latest",
        messages=[
            {"role": "user", "content": 'Say {"greeting": "hello"} in JSON format'}
        ],
        stream=False,
        # 注意：response_format 可能不被 Ollama 支持
        # response_format={"type": "json_object"}
    )
    
    print("✅ JSON 请求成功")
    print(f"   回复: {response.choices[0].message.content[:100]}")
    
except Exception as e:
    print(f"⚠️  JSON 格式请求失败: {e}")

print("\n" + "=" * 60)
print("诊断完成！")
print("=" * 60)
