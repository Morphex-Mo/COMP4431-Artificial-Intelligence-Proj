# 跨文化智能翻译助手 - 桌面版 (Ollama 本地版)

基于 Qt 的桌面应用程序，不依赖浏览器，提供原生 GUI 体验。
# Cross-Cultural Translation Assistant (Desktop, Ollama Local)

[中文](#中文) | [English](#english)

---

## 中文

基于 Qt 的桌面应用，不依赖浏览器，提供原生 GUI 体验。
默认使用 **Ollama 免费本地 AI**，完整保留跨文化翻译与文化建议功能。
语音输入使用 **Vosk**，可离线运行。

### ✨ 功能特性

- 🖥️ 原生桌面应用，离线可用
- 🎨 清晰的多选项卡结果展示
- 🎤 Vosk 离线语音识别
- 🔊 pyttsx3 离线语音朗读
- ⚡ 异步翻译，不阻塞 UI
- 💰 默认免费本地模型，无需付费 API

### 🚀 快速开始

1. 安装依赖

```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

pip install PySide6>=6.8.0 pyttsx3==2.90 vosk>=0.3.45 requests
```

2. 安装并下载 Ollama 模型

```powershell
ollama pull qwen2.5
```

3. 运行桌面应用

```bash
python app_gui.py
```

### ⚙️ Ollama 配置（可选）

默认无需配置。如需切换模型或端口，可创建 `credentials.json`：

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

更多说明请见 [OLLAMA_SETUP.md](OLLAMA_SETUP.md) 与 [QUICKSTART_OLLAMA.md](QUICKSTART_OLLAMA.md)。

### ✅ 测试 Ollama

```bash
python test_ollama.py
```

### 🔧 常见问题

- 连接错误或 502：确认 Ollama 正在运行
```powershell
ollama list
ollama serve
```

### 💡 技术栈

- GUI：PyQt6
- 异步：QThread
- TTS：pyttsx3
- 语音识别：Vosk
- AI：Ollama 本地模型（默认）

### 📄 License

MIT License，详见 [LICENSE](LICENSE)。

---

## English

A Qt-based desktop app with native GUI (no browser required).
Uses **Ollama local AI by default** to keep cross-cultural translation and cultural advice fully available.
Voice input is powered by **Vosk** for offline speech recognition.

### ✨ Features

- 🖥️ Native desktop app, works offline
- 🎨 Clear tabbed results (literal, natural, cultural advice)
- 🎤 Offline speech recognition with Vosk
- 🔊 Offline TTS with pyttsx3
- ⚡ Async translation without UI blocking
- 💰 Free local model by default (no paid API required)

### 🚀 Quick Start

1. Install dependencies

```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

pip install PySide6>=6.8.0 pyttsx3==2.90 vosk>=0.3.45 requests
```

2. Install and download Ollama model

```powershell
ollama pull qwen2.5
```

3. Run the desktop app

```bash
python app_gui.py
```

### ⚙️ Ollama Config (Optional)

No config needed by default. To switch model or port, create `credentials.json`:

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

See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) and [QUICKSTART_OLLAMA.md](QUICKSTART_OLLAMA.md) for more details.

### ✅ Test Ollama

```bash
python test_ollama.py
```

### 🔧 Troubleshooting

- Connection error / 502: make sure Ollama is running
```powershell
ollama list
ollama serve
```

### 💡 Tech Stack

- GUI: PyQt6
- Async: QThread
- TTS: pyttsx3
- ASR: Vosk
- AI: Ollama local model (default)

### 📄 License

MIT License. See [LICENSE](LICENSE).
   - 🌏 文化建议：深入的文化背景分析
