"""
测试 Ollama 连接和翻译功能

运行此脚本以验证 Ollama 是否正确配置
"""

from translator_core_new import generate_translation_and_advice

def test_ollama():
    print("=" * 60)
    print("🦙 Ollama 连接测试")
    print("=" * 60)
    
    # 测试翻译
    print("\n📝 测试翻译功能...")
    print("输入: 你好，世界")
    print("源语言: 中文 → 目标语言: 英文")
    print("场景: 日常")
    print("\n⏳ 正在调用 Ollama...")
    
    try:
        result = generate_translation_and_advice(
            source_text="你好，世界",
            source_lang="zh",
            target_lang="en",
            scenario="daily",
            tone="neutral"
        )
        
        print("\n" + "=" * 60)
        print("✅ 直译结果:")
        print("-" * 60)
        print(result.get("literal_translation", ""))
        
        print("\n" + "=" * 60)
        print("💬 自然表达:")
        print("-" * 60)
        natural = result.get("natural_translation", [])
        if isinstance(natural, list):
            for i, item in enumerate(natural, 1):
                if isinstance(item, dict):
                    print(f"\n{i}. {item.get('text', '')}")
                    if item.get('explanation'):
                        print(f"   说明: {item.get('explanation')}")
                else:
                    print(f"{i}. {item}")
        else:
            print(natural)
        
        print("\n" + "=" * 60)
        print("🌏 文化建议:")
        print("-" * 60)
        print(result.get("advice", ""))
        
        print("\n" + "=" * 60)
        print("✅ 测试成功！Ollama 工作正常！")
        print("=" * 60)
        
        # 检查是否是真实的 AI 输出
        advice = result.get("advice", "")
        if "[Error]" in advice or "[SDK Not Installed]" in advice or "[Missing Credentials]" in advice or "[Connection Error]" in advice:
            print("\n⚠️  警告: 检测到错误信息，请检查上方的建议内容")
            return False
        
        if "Cultural Advice Example" in advice or "[Literal Example]" in result.get("literal_translation", ""):
            print("\n⚠️  注意: 当前使用的是示例输出（未连接到 AI）")
            print("    请确保 Ollama 已安装并运行")
            return False
            
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {str(e)}")
        print("=" * 60)
        return False

def check_ollama_status():
    """检查 Ollama 服务状态"""
    import subprocess
    
    print("\n🔍 检查 Ollama 状态...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Ollama 已安装")
            print("\n已安装的模型:")
            print(result.stdout)
            return True
        else:
            print("⚠️  Ollama 命令执行失败")
            return False
    except FileNotFoundError:
        print("❌ Ollama 未安装")
        print("\n请访问 https://ollama.com/download 下载安装")
        return False
    except Exception as e:
        print(f"⚠️  检查失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 开始测试...\n")
    
    # 先检查 Ollama 状态
    ollama_ok = check_ollama_status()
    
    if not ollama_ok:
        print("\n💡 提示:")
        print("1. 安装 Ollama: https://ollama.com/download")
        print("2. 下载模型: ollama pull qwen2.5")
        print("3. 启动服务: ollama serve (如果需要)")
        print("4. 重新运行此测试")
    
    print("\n" + "=" * 60)
    
    # 测试翻译功能
    success = test_ollama()
    
    if success:
        print("\n🎉 恭喜！你的系统已经正确配置！")
        print("   现在可以运行主程序: python app_gui.py")
    else:
        print("\n💡 故障排除:")
        print("1. 确保 Ollama 正在运行: ollama serve")
        print("2. 确保已下载模型: ollama pull qwen2.5")
        print("3. 测试 Ollama: ollama run qwen2.5")
        print("4. 查看详细文档: OLLAMA_SETUP.md")
    
    print("\n")
