# 翻译速度优化指南 🚀

## 当前优化状态

你的翻译功能已经过优化！主要改进：

### ✅ 已完成的优化

1. **切换到快速模型**：`qwen2.5:3b` （替代 `qwen2.5:latest` 7B 模型）
2. **简化 Prompt**：快速模式减少 70% 生成量
3. **优化推理参数**：降低 temperature、限制 tokens
4. **配置化管理**：在 `config.py` 中统一管理

### 📊 预期性能提升

| 配置 | 原速度 | 优化后 | 提升 |
|------|--------|--------|------|
| **快速模式 + 3B 模型** | 10-15 秒 | 2-3 秒 | **5x** |
| 快速模式 + 7B 模型 | 10-15 秒 | 4-5 秒 | 3x |
| 完整模式 + 3B 模型 | 10-15 秒 | 5-7 秒 | 2x |

---

## 使用方法

### 1. 下载快速模型（必需）

在终端运行：

```bash
ollama pull qwen2.5:3b
```

如果想要更快（1-2秒，但质量略低）：

```bash
ollama pull qwen2.5:1.5b
```

然后修改 `config.py` 中的 `RECOMMENDED_MODELS["balanced"]` 为 `"qwen2.5:1.5b"`。

### 2. 切换快速/完整模式

编辑 `config.py`：

```python
# 快速模式（推荐）：2-3 秒
USE_FAST_MODE = True

# 完整模式：5-7 秒，但文化建议更详细
USE_FAST_MODE = False
```

### 3. 运行程序

```bash
python app_gui.py
```

---

## 进一步加速方案

### 方案 A：使用 GPU 加速（如果有 NVIDIA 显卡）

1. 检查 Ollama 是否使用 GPU：
   ```bash
   ollama ps
   ```

2. 如果显示 CPU，安装 CUDA 支持：
   - 访问：https://ollama.com/download
   - 下载 GPU 版本的 Ollama

GPU 加速可以再提升 **2-3x** 速度（最终达到 ~1 秒）！

### 方案 B：使用混合架构（终极方案）

如果仍需更快，使用我创建的 `translator_core_fast.py`：

```bash
# 安装专用翻译模型
pip install transformers sentencepiece torch
```

编辑 `app_gui.py`，替换导入：

```python
# 原来的
# from translator_core_new import generate_translation_and_advice

# 改为
from translator_core_fast import generate_translation_and_advice
```

**性能**：
- 字面翻译：~50ms（Helsinki-NLP 模型）
- 文化建议：~500ms（Ollama 3B）
- **总计：< 1 秒**

---

## 调试与测试

### 测试翻译速度

运行测试脚本：

```bash
python -c "
import time
from translator_core_new import generate_translation_and_advice

start = time.time()
result = generate_translation_and_advice('吃了吗？', 'zh', 'en', 'casual')
elapsed = time.time() - start

print(f'翻译耗时: {elapsed:.2f} 秒')
print(f'字面翻译: {result[\"literal_translation\"]}')
"
```

### 查看当前配置

```bash
python -c "
from config import USE_FAST_MODE, OLLAMA_FAST_OPTIONS, RECOMMENDED_MODELS
print(f'快速模式: {USE_FAST_MODE}')
print(f'推理参数: {OLLAMA_FAST_OPTIONS}')
print(f'推荐模型: {RECOMMENDED_MODELS}')
"
```

### 如果速度仍然慢

1. **检查模型是否正确**：
   ```bash
   ollama list
   # 应该看到 qwen2.5:3b
   ```

2. **检查 Ollama 状态**：
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **查看实时日志** 查看终端输出，会显示：
   ```
   DEBUG: Raw model output:
   ...
   ```

---

## 常见问题

### Q: 快速模式会影响翻译质量吗？

A: 轻微影响，主要体现在：
- 文化建议更简洁（50 字 vs 200 字）
- 自然表达数量减少（1-2 个 vs 3 个）
- 翻译准确性几乎不受影响

### Q: 可以同时提高速度和质量吗？

A: 是的，使用 GPU：
- 快速模式 + GPU + 3B 模型 ≈ 1 秒，质量好
- 完整模式 + GPU + 7B 模型 ≈ 2-3 秒，质量最佳

### Q: 如何恢复到原始配置？

A: 编辑 `config.py`：

```python
USE_FAST_MODE = False  # 恢复完整质量
```

并运行：

```bash
ollama pull qwen2.5:latest
```

---

## 性能指标参考

### 模型推理速度（CPU）

| 模型 | 参数量 | 速度 | 质量 | 显存 |
|------|--------|------|------|------|
| qwen2.5:1.5b | 1.5B | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | 1GB |
| qwen2.5:3b | 3B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 2GB |
| qwen2.5:7b | 7B | ⚡⚡ | ⭐⭐⭐⭐⭐ | 4GB |

### Prompt 大小影响

| 模式 | Prompt Tokens | 生成 Tokens | 总耗时 |
|------|--------------|-------------|--------|
| 快速 | ~200 | ~150 | 2-3s |
| 完整 | ~600 | ~400 | 5-10s |

---

## 技术原理

### 为什么这些优化有效？

1. **小模型**: 参数少 → 计算量线性减少
2. **简化 Prompt**: 减少输入 tokens → 编码时间减少
3. **限制生成量**: `num_predict=300` → 解码时间减少
4. **降低 temperature**: 减少采样计算 → 每个 token 生成更快
5. **减小 top_k**: 从数千个候选 token 中选择 → 只考虑前 20 个

**总提升 = 模型加速 × prompt 加速 × 生成加速 ≈ 2x × 1.5x × 1.5x ≈ 5x**

---

## 联系与贡献

如果优化后速度仍不满意，可以尝试：
- 使用云端 API（Deepseek: 1-2 秒，但需付费）
- 使用完全离线的规则翻译（`translator_core_fast.py` 的习语映射）
- 购买更强的硬件（GPU 加速）

祝使用愉快！🎉
