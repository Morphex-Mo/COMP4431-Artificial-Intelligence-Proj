# 🦙 Ollama 免费本地AI设置指南

**Ollama = 完全免费 + 无限使用 + 保留所有跨文化翻译功能！**

---

## 🎯 为什么选择 Ollama？

✅ **完全免费** - 无需付费API
✅ **无限使用** - 没有请求限制
✅ **保护隐私** - 数据不上传到云端
✅ **保留AI功能** - 文化建议、场景分析等功能完整
✅ **离线运行** - 不需要网络连接
✅ **多语言支持** - 中文、英文、日文都很好

---

## 📦 第一步：安装 Ollama

### Windows

1. 访问 [https://ollama.com/download](https://ollama.com/download)
2. 下载 Windows 版本（约 300 MB）
3. 双击安装包，按提示安装
4. 安装完成后，Ollama 会自动在后台运行

### macOS

```bash
# 方法1: 下载安装包
# 访问 https://ollama.com/download

# 方法2: 使用 Homebrew
brew install ollama
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 🚀 第二步：下载AI模型

打开终端（PowerShell或CMD），运行以下命令：

### 推荐模型：Qwen2.5（最佳中文支持）

```powershell
ollama pull qwen2.5
```

**模型大小**: ~4.7 GB  
**下载时间**: 5-15分钟（取决于网速）  
**优点**: 
- 🇨🇳 中文理解最佳
- 🇬🇧 英文流畅
- 🇯🇵 日文良好
- 💡 文化理解深刻

### 其他可选模型

```powershell
# Llama 3.2（通用型，英文好）
ollama pull llama3.2

# Gemma 2（Google出品，速度快）
ollama pull gemma2

# DeepSeek R1（数学和推理强）
ollama pull deepseek-r1:7b
```

**💡 提示**: 首次使用推荐 `qwen2.5`，它对中文和跨文化翻译效果最好。

---

## ⚙️ 第三步：启动 Ollama 服务

### Windows

Ollama 安装后会自动启动。如果需要手动启动：

```powershell
# 检查是否在运行
ollama list

# 如果没有运行，启动服务
ollama serve
```

### macOS / Linux

```bash
# 启动服务（在后台运行）
ollama serve &

# 或者使用系统服务
brew services start ollama  # macOS
systemctl start ollama      # Linux
```

---

## 🔧 第四步：配置项目

### 方法1: 使用配置文件（推荐）

1. **复制示例配置**:
```powershell
Copy-Item credentials.example.json credentials.json
```

2. **编辑 `credentials.json`**:
```json
{
  "tokens": [
    {
      "name": "ollama-local",
      "token": "ollama",
      "api_url": "http://localhost:11434/v1",
      "model": "qwen2.5:latest"
    }
  ],
  "default": "ollama-local"
}
```

### 方法2: 使用环境变量

```powershell
# Windows PowerShell
$env:API_URL = "http://localhost:11434/v1"
$env:API_KEY = "ollama"
$env:MODEL_NAME = "qwen2.5:latest"

# 或者永久设置（系统属性 -> 环境变量）
```

### 方法3: 什么都不配置

如果你不创建 `credentials.json` 也不设置环境变量，程序会**自动使用 Ollama 默认配置**！

---

## 🎮 第五步：运行程序

```powershell
# 激活虚拟环境
.venv\Scripts\activate

# 运行桌面版
python app_gui.py

# 或运行Web版
python app.py
```

程序启动后，直接使用翻译功能即可！Ollama 会在后台处理所有AI请求。

---

## ✅ 验证安装

### 测试 Ollama 是否正常工作

```powershell
# 查看已安装的模型
ollama list

# 测试对话（按 Ctrl+D 或输入 /bye 退出）
ollama run qwen2.5
>>> 你好，请用英文翻译：我想去旅游
```

如果能正常回复，说明 Ollama 工作正常！

### 在应用中测试

1. 打开翻译助手
2. 输入文本："我想去东京旅游"
3. 选择"中文→英文"，场景"旅游"
4. 点击"翻译并给出文化建议"

如果能看到翻译结果和文化建议，说明配置成功！🎉

---

## 🔍 常见问题

### ❓ 下载模型很慢怎么办？

**解决方法**：
1. 使用国内镜像：
```powershell
$env:OLLAMA_MIRRORS = "https://ollama.mirror.zx"
ollama pull qwen2.5
```

2. 或者在网速好的时候下载，下载一次后就可以离线使用

### ❓ 提示"Connection Error"无法连接

**排查步骤**：

1. **检查 Ollama 是否在运行**：
```powershell
ollama list
```
如果提示错误，运行：
```powershell
ollama serve
```

2. **检查端口**：
```powershell
# 测试 API 是否可访问
curl http://localhost:11434/api/tags
```

3. **防火墙问题**：
   - 确保防火墙允许本地端口 11434

### ❓ 模型回复很慢

**原因**: 模型对硬件要求较高

**优化方法**：

1. **使用更小的模型**：
```powershell
# 使用 1.5B 参数的小模型（更快，但质量稍低）
ollama pull qwen2.5:1.5b
```

2. **修改配置使用小模型**：
```json
{
  "model": "qwen2.5:1.5b"
}
```

3. **硬件建议**：
   - **最低**: 8GB RAM（使用 1.5b-3b 模型）
   - **推荐**: 16GB RAM（使用 7b 模型）
   - **最佳**: 32GB RAM + GPU（使用 14b+ 模型）

### ❓ 想切换不同的模型

**非常简单**：

1. **下载新模型**：
```powershell
ollama pull llama3.2
```

2. **修改配置**：
```json
{
  "model": "llama3.2:latest"
}
```

3. **重启应用即可**

---

## 📊 模型对比推荐

| 模型 | 大小 | 中文 | 英文 | 日文 | 速度 | 推荐度 |
|------|------|------|------|------|------|--------|
| qwen2.5 | 4.7GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ 最推荐 |
| qwen2.5:1.5b | 1GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💻 低配机 |
| llama3.2 | 2GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 🌍 英文优先 |
| gemma2 | 5GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⚡ 平衡型 |
| deepseek-r1:7b | 4.1GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 🧠 推理强 |

---

## 🎯 快速命令速查

```powershell
# 查看已安装模型
ollama list

# 下载模型
ollama pull qwen2.5

# 删除模型（释放空间）
ollama rm llama3.2

# 查看模型信息
ollama show qwen2.5

# 启动服务
ollama serve

# 测试对话
ollama run qwen2.5

# 查看日志
ollama logs
```

---

## 🚀 高级配置（可选）

### 使用GPU加速

如果你有NVIDIA显卡：

1. 确保安装了CUDA（Ollama会自动检测）
2. Ollama会自动使用GPU，无需配置
3. 运行时可以看到GPU使用率提升

### 调整内存限制

```powershell
# 设置最大使用内存（单位：GB）
$env:OLLAMA_MAX_LOADED_MODELS = 1
$env:OLLAMA_NUM_PARALLEL = 1
```

### 使用自定义端口

```powershell
# 修改默认端口
$env:OLLAMA_HOST = "127.0.0.1:8080"
ollama serve
```

然后在 `credentials.json` 中更新：
```json
{
  "api_url": "http://localhost:8080/v1"
}
```

---

## 💡 最佳实践

1. **首次使用**：先下载 `qwen2.5`，它综合表现最好
2. **性能优化**：如果电脑配置较低，使用 `qwen2.5:1.5b`
3. **自动启动**：将 Ollama 设为开机自启，使用时更方便
4. **定期更新**：模型会不断改进，定期运行 `ollama pull` 更新

---

## 🆚 对比其他方案

| 方案 | 费用 | 功能完整性 | 隐私 | 网络要求 | 难度 |
|------|------|-----------|------|----------|------|
| **Ollama** | ✅ 免费 | ✅ 完整 | ✅ 本地 | ✅ 离线 | ⭐⭐ 简单 |
| Deepseek API | ❌ 付费 | ✅ 完整 | ⚠️ 云端 | ❌ 需要 | ⭐ 最简单 |
| OpenAI API | ❌ 昂贵 | ✅ 完整 | ⚠️ 云端 | ❌ 需要 | ⭐ 最简单 |
| deep-translator | ✅ 免费 | ❌ 基础 | ✅ 云端 | ❌ 需要 | ⭐ 最简单 |
| Argos Translate | ✅ 免费 | ❌ 基础 | ✅ 本地 | ✅ 离线 | ⭐⭐⭐ 复杂 |

---

## 🎉 完成！

现在你已经成功配置了免费的本地AI翻译系统！

**享受无限次的跨文化翻译服务吧！** 🌍✨

有问题？查看项目 [README.md](README.md) 或提交 Issue。
