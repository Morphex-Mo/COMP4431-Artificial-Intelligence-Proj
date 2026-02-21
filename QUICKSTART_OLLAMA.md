# 🚀 快速开始：5分钟设置免费AI翻译

**不想看长文档？按这3步操作！**

---

## 步骤1: 安装 Ollama（2分钟）

访问 [https://ollama.com/download](https://ollama.com/download)，下载并安装。

**Windows**: 双击安装包即可  
**macOS**: `brew install ollama`  
**Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

---

## 步骤2: 下载AI模型（5-10分钟）

打开终端，运行：

```powershell
ollama pull qwen2.5
```

等待下载完成（约4.7GB）。

---

## 步骤3: 运行程序

```powershell
# 激活虚拟环境（如果有）
.venv\Scripts\activate

# 运行程序
python app_gui.py
```

**就这么简单！** 🎉

程序会自动检测并使用本地Ollama，无需任何配置文件！

---

## ✅ 验证是否成功

1. 在程序中输入："你好"
2. 选择"中文→英文"
3. 点击"翻译"
4. 如果看到翻译结果和文化建议，说明成功了！

---

## ⚠️ 遇到问题？

### 提示"Connection Error"

运行以下命令启动 Ollama：

```powershell
ollama serve
```

保持这个窗口打开，然后重新运行程序。

### 想用其他模型？

```powershell
# 更快的小模型（1GB）
ollama pull qwen2.5:1.5b

# 英文更好的模型（2GB）
ollama pull llama3.2
```

然后创建 `credentials.json`：

```json
{
  "tokens": [{"name": "ollama", "token": "ollama", "api_url": "http://localhost:11434/v1", "model": "llama3.2:latest"}],
  "default": "ollama"
}
```

---

## 📚 需要更多帮助？

查看详细文档：
- [Ollama完整设置指南](OLLAMA_SETUP.md)
- [项目README](README.md)

---

**享受免费无限的AI翻译！** 🌍✨
