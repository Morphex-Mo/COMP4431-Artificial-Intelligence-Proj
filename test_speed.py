"""
翻译速度测试脚本
快速验证优化效果
"""

import time
from translator_core_new import generate_translation_and_advice

# 测试用例
test_cases = [
    ("吃了吗？", "zh", "en", "casual"),
    ("How are you?", "en", "zh", "casual"),
    ("お疲れ様です", "ja", "zh", "business"),
]

print("=" * 60)
print("翻译速度测试")
print("=" * 60)

total_time = 0
results = []

for i, (text, src, tgt, scenario) in enumerate(test_cases, 1):
    print(f"\n测试 {i}/3: '{text}' ({src} → {tgt})")
    print("-" * 40)
    
    start = time.time()
    result = generate_translation_and_advice(text, src, tgt, scenario)
    elapsed = time.time() - start
    
    total_time += elapsed
    results.append((text, elapsed, result))
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📝 字面翻译: {result['literal_translation']}")
    
    if result['natural_translation']:
        first_natural = result['natural_translation'][0]
        print(f"💬 自然表达: {first_natural['text']}")
    
    # 速度评级
    if elapsed < 2:
        rating = "⚡⚡⚡⚡⚡ 极快"
    elif elapsed < 3:
        rating = "⚡⚡⚡⚡ 很快"
    elif elapsed < 5:
        rating = "⚡⚡⚡ 快"
    elif elapsed < 8:
        rating = "⚡⚡ 一般"
    else:
        rating = "⚡ 较慢"
    
    print(f"评分: {rating}")

print("\n" + "=" * 60)
print(f"总耗时: {total_time:.2f} 秒")
print(f"平均耗时: {total_time/len(test_cases):.2f} 秒/次")
print("=" * 60)

# 性能评估
avg_time = total_time / len(test_cases)

print("\n📊 性能评估:")
if avg_time < 2:
    print("✅ 优秀！速度已达到最优水平。")
elif avg_time < 3:
    print("✅ 良好！速度满足实时交互需求。")
    print("💡 提示: 如需更快，可尝试 qwen2.5:1.5b 模型")
elif avg_time < 5:
    print("⚠️  可接受，但有优化空间。")
    print("💡 建议:")
    print("   1. 确认使用 qwen2.5:3b 模型（运行: ollama pull qwen2.5:3b）")
    print("   2. 检查 config.py 中 USE_FAST_MODE = True")
else:
    print("❌ 速度较慢，需要优化。")
    print("💡 建议:")
    print("   1. 检查 Ollama 是否运行: curl http://localhost:11434")
    print("   2. 切换到 3B 模型: ollama pull qwen2.5:3b")
    print("   3. 启用快速模式: 编辑 config.py 设置 USE_FAST_MODE = True")
    print("   4. 考虑使用 GPU 加速或 translator_core_fast.py")

# 配置检查
print("\n🔧 当前配置:")
try:
    from config import USE_FAST_MODE, OLLAMA_FAST_OPTIONS
    print(f"   快速模式: {'✅ 已启用' if USE_FAST_MODE else '❌ 未启用'}")
    print(f"   Token 限制: {OLLAMA_FAST_OPTIONS.get('num_predict', 'N/A')}")
    print(f"   Temperature: {OLLAMA_FAST_OPTIONS.get('temperature', 'N/A')}")
except ImportError:
    print("   ⚠️  无法读取配置文件")

print("\n" + "=" * 60)
print("测试完成！查看 SPEED_OPTIMIZATION.md 了解更多优化方案。")
print("=" * 60)
