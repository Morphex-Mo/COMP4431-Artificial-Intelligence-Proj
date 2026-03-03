"""
Fast Translation Core - 混合架构版本
使用专用翻译模型（~50ms）+ 迷你LLM生成文化建议（~500ms）
总延迟：< 1s
"""

from typing import Dict
import os
import json
import traceback

# 全局缓存翻译器和LLM
_translators = {}
_llm_client = None


def _get_translator(source_lang: str, target_lang: str):
    """获取或创建翻译器（懒加载 + 缓存）"""
    global _translators
    
    # 映射到 Helsinki-NLP 模型名称
    model_map = {
        "zh-en": "Helsinki-NLP/opus-mt-zh-en",
        "en-zh": "Helsinki-NLP/opus-mt-en-zh",
        "ja-en": "Helsinki-NLP/opus-mt-ja-en",
        "en-ja": "Helsinki-NLP/opus-mt-en-jap",
        "zh-ja": "Helsinki-NLP/opus-mt-zh-jap",
        "ja-zh": "Helsinki-NLP/opus-mt-jap-zh",
    }
    
    key = f"{source_lang}-{target_lang}"
    
    if key in _translators:
        return _translators[key]
    
    try:
        from transformers import pipeline
        model_name = model_map.get(key)
        
        if not model_name:
            return None
            
        print(f"Loading translation model: {model_name} (first time only)...")
        translator = pipeline("translation", model=model_name, device=-1)  # device=-1: CPU, 0: GPU
        _translators[key] = translator
        return translator
    except Exception as e:
        print(f"Failed to load translator: {e}")
        return None


def _get_llm_client():
    """获取 LLM 客户端（用于生成文化建议）"""
    global _llm_client
    
    if _llm_client:
        return _llm_client
    
    # 优先使用最快的本地方案
    api_url = os.environ.get("API_URL", "http://localhost:11434/v1")
    
    try:
        if "localhost" in api_url or "11434" in api_url:
            import requests
            _llm_client = {"type": "ollama", "url": api_url.replace("/v1", "")}
        else:
            from openai import OpenAI
            token = os.environ.get("API_KEY", "dummy")
            _llm_client = {"type": "openai", "client": OpenAI(api_key=token, base_url=api_url)}
        
        return _llm_client
    except Exception as e:
        print(f"LLM client init failed: {e}")
        return None


def _fast_translate(text: str, source_lang: str, target_lang: str) -> str:
    """快速翻译（50-200ms）"""
    translator = _get_translator(source_lang, target_lang)
    
    if not translator:
        return f"[Translation Model Not Available] {text}"
    
    try:
        result = translator(text, max_length=512)
        return result[0]["translation_text"]
    except Exception as e:
        return f"[Translation Error: {e}]"


def _generate_cultural_advice_only(
    source_text: str, 
    source_lang: str, 
    target_lang: str,
    scenario: str,
    tone: str
) -> str:
    """仅生成文化建议（简化版，~500ms）"""
    
    llm = _get_llm_client()
    if not llm:
        return "**文化建议功能暂不可用**\n\n请安装 Ollama 或配置 API 密钥。"
    
    lang_names = {
        "zh": "中文",
        "en": "英文", 
        "ja": "日文"
    }
    
    # 极简 prompt，只生成关键建议（减少 tokens）
    prompt = f"""简要分析以下内容的跨文化要点：

原文：{source_text}
语言方向：{lang_names.get(source_lang, source_lang)} → {lang_names.get(target_lang, target_lang)}
场景：{scenario}

用 {lang_names.get(source_lang, '中文')} 回答（50字以内）：
1. 这句话的社交功能是什么？
2. 目标文化中如何表达相同意图？
3. 一个关键礼仪提示。

直接输出建议，不要前缀。"""

    try:
        if llm["type"] == "ollama":
            import requests
            url = llm["url"].rstrip("/") + "/api/generate"
            
            # 使用更激进的参数加速
            payload = {
                "model": os.environ.get("MODEL_NAME", "qwen2.5:3b"),  # 使用 3B 小模型
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 降低随机性，加快采样
                    "top_p": 0.8,
                    "num_predict": 150,  # 限制最大生成长度
                }
            }
            
            response = requests.post(url, json=payload, timeout=5)  # 5秒超时
            
            if response.status_code == 200:
                return response.json().get("response", "")
                
        else:  # OpenAI-compatible API
            response = llm["client"].chat.completions.create(
                model=os.environ.get("MODEL_NAME", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content
            
    except Exception as e:
        return f"[文化建议生成失败: {e}]"
    
    return "[无法生成建议]"


def generate_translation_and_advice(
    source_text: str,
    source_lang: str,
    target_lang: str,
    scenario: str,
    tone: str = "neutral",
    token_name: str = None,
) -> Dict[str, str]:
    """
    快速翻译 + 文化建议（目标：< 1s）
    
    策略：
    1. 字面翻译用 Helsinki-NLP 模型（~50ms）
    2. 自然表达用改进的直译 + 常见表达模板（~10ms）  
    3. 文化建议用迷你 LLM 简化 prompt（~500ms）
    """
    
    try:
        if not source_text or not source_text.strip():
            return {
                "literal_translation": "",
                "natural_translation": [{"text": "", "explanation": ""}],
                "advice": "请输入要翻译的文本。",
            }
        
        s_text = source_text.strip()
        
        # 1. 快速字面翻译（50-200ms）
        literal = _fast_translate(s_text, source_lang, target_lang)
        
        # 2. 生成自然表达（使用预设模板 + 字面翻译微调，几乎0延迟）
        natural_expressions = _generate_natural_expressions(
            s_text, literal, source_lang, target_lang, scenario
        )
        
        # 3. 并行生成文化建议（可选，如果时间紧张可以禁用）
        advice = _generate_cultural_advice_only(
            s_text, source_lang, target_lang, scenario, tone
        )
        
        return {
            "literal_translation": literal,
            "natural_translation": natural_expressions,
            "advice": advice,
        }
        
    except Exception as exc:
        return {
            "literal_translation": "[错误]",
            "natural_translation": [{"text": "[错误]", "explanation": str(exc)}],
            "advice": f"处理出错：{traceback.format_exc()}",
        }


def _generate_natural_expressions(
    source_text: str,
    literal_translation: str, 
    source_lang: str,
    target_lang: str,
    scenario: str
) -> list:
    """
    基于规则和模板快速生成自然表达（不调用 LLM）
    
    这是一个简化版本，可以根据需要扩展规则库
    """
    
    # 常见习语/问候语映射（可扩展）
    idiom_map = {
        "zh-en": {
            "吃了吗": [
                {"text": "How are you?", "explanation": "标准英语问候，相当于中文'吃了吗'的社交功能"},
                {"text": "How's it going?", "explanation": "更随意的朋友间问候"},
            ],
            "去哪儿": [
                {"text": "Hi there!", "explanation": "英语中这种寒暄通常用简单问候替代"},
                {"text": "What's up?", "explanation": "年轻人常用的随意问候"},
            ],
            "辛苦了": [
                {"text": "Great job!", "explanation": "英语中对他人努力的认可"},
                {"text": "Thank you for your hard work!", "explanation": "正式场合的感谢表达"},
            ],
        },
        "zh-ja": {
            "吃了吗": [
                {"text": "お元気ですか？", "explanation": "日语标准问候"},
                {"text": "こんにちは", "explanation": "日常问候"},
            ],
        },
        # 可以继续添加其他语言对...
    }
    
    key = f"{source_lang}-{target_lang}"
    
    # 检查是否是常见习语
    for idiom, expressions in idiom_map.get(key, {}).items():
        if idiom in source_text:
            return expressions
    
    # 如果不是习语，返回基于字面翻译的自然表达
    return [
        {
            "text": literal_translation,
            "explanation": f"基于场景 '{scenario}' 的标准翻译"
        }
    ]
