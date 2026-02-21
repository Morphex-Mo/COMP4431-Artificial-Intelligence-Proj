from typing import Dict
import os
import json
import traceback


def _read_credentials(json_path: str = "credentials.json", legacy_path: str = "credentials") -> Dict:
    """Read credentials with support for a structured JSON file containing multiple tokens.

    Return format:
    {
        "tokens": {"name": {"token": "...", "api_url": "https://...", "model": "..."}},
        "default": "name"
    }

    Backwards compatibility:
    - If `credentials.json` exists and is valid, use it.
    - Else if a legacy `credentials` file exists, accept JSON, KEY=VALUE, or a single-line token.
      A single token will be converted into a named token "deepseek-main".
    - If nothing found, return {}.
    """
    # Prefer structured JSON credentials
    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Normalize tokens into a dict keyed by name
            tokens = {}
            if isinstance(data.get("tokens"), list):
                for entry in data.get("tokens", []):
                    name = entry.get("name") or entry.get("id") or entry.get("key")
                    if not name:
                        continue
                    tokens[name] = {
                        "token": entry.get("token"), 
                        "api_url": entry.get("api_url"),
                        "model": entry.get("model")
                    }
            elif isinstance(data.get("tokens"), dict):
                for name, entry in data.get("tokens", {}).items():
                    if isinstance(entry, dict):
                        tokens[name] = {
                            "token": entry.get("token"), 
                            "api_url": entry.get("api_url"),
                            "model": entry.get("model")
                        }
            # If top-level looks like a single-token dict, accept common keys
            if not tokens and isinstance(data, dict):
                # keys like token/api_key/api_key_name
                if "token" in data or "api_key" in data:
                    tokens["deepseek-main"] = {
                        "token": data.get("token") or data.get("api_key"), 
                        "api_url": data.get("api_url"),
                        "model": data.get("model")
                    }

            result = {"tokens": tokens}
            if isinstance(data.get("default"), str):
                result["default"] = data.get("default")
            return result
    except Exception:
        # Fall through to legacy parsing
        pass

    # Legacy support: read the old `credentials` file
    if not os.path.exists(legacy_path):
        return {}

    try:
        with open(legacy_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        return {}

    if not content:
        return {}

    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # If it's a simple dict of keys, return as tokens if possible
            if "token" in data or "api_key" in data:
                return {"tokens": {"deepseek-main": {"token": data.get("token") or data.get("api_key"), "api_url": data.get("api_url")}}, "default": "deepseek-main"}
            # If user stored a tokens list/dict, try to normalize
            if "tokens" in data:
                return _read_credentials(json_path=legacy_path, legacy_path=legacy_path)
    except Exception:
        pass

    # KEY=VALUE lines
    kv = {}
    for line in content.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()

    if kv:
        # Common keys mapping
        token_val = kv.get("token") or kv.get("TOKEN") or kv.get("api_key") or kv.get("API_KEY")
        api_url = kv.get("api_url") or kv.get("API_URL")
        if token_val:
            return {"tokens": {"deepseek-main": {"token": token_val, "api_url": api_url}}, "default": "deepseek-main"}

    # If it's a single-line token (no key=val), accept it as a single token
    # treat the entire content as the token
    return {"tokens": {"deepseek-main": {"token": content, "api_url": None}}, "default": "deepseek-main"}


def generate_translation_and_advice(
    source_text: str,
    source_lang: str,
    target_lang: str,
    scenario: str,
    tone: str = "neutral",
    token_name: str = None,
) -> Dict[str, str]:
    """Construct a prompt and call LLM API (Ollama/Deepseek/etc) via OpenAI SDK.

    Behavior:
    - Support Ollama (local, free): http://localhost:11434/v1
    - Support Deepseek, OpenAI, and other OpenAI-compatible APIs
    - Prefer API_KEY from environment; fallback to credentials file
    - Prefer api_url from credentials or environment
    - Default to Ollama if no credentials found
    - Try to import OpenAI SDK. If not available, return helpful message
    - Always avoid raising exceptions to the caller; return safe strings.
    """

    try:
        s_text = source_text if isinstance(source_text, str) else ""
        s_lang = source_lang.strip() if isinstance(source_lang, str) and source_lang.strip() else "<unknown>"
        t_lang = target_lang.strip() if isinstance(target_lang, str) and target_lang.strip() else "<unknown>"
        scenario = scenario.strip() if isinstance(scenario, str) and scenario.strip() else "general"
        tone = tone.strip() if isinstance(tone, str) and tone.strip() else "neutral"

        # Map language codes to natural names for the prompt
        lang_names = {
            "zh": "Simplified Chinese",
            "en": "English",
            "ja": "Japanese"
        }
        s_lang_name = lang_names.get(s_lang, s_lang)
        t_lang_name = lang_names.get(t_lang, t_lang)

        if not s_text:
            return {
                "literal_translation": "[Literal Example] Source text not provided.",
                "natural_translation": [{"text": "[No Natural Expression]", "explanation": ""}],
                "advice": "[Tip] Source text not provided; please enter text to translate to get translation and cultural advice.",
            }

        # Build prompt and messages
        prompt = (
            "Act as a cross-cultural translation assistant. Output JSON data based on the following requirements.\n\n"
            "Input content:\n"
            f"Source Text: {s_text}\n"
            f"Source Language: {s_lang_name}\n"
            f"Target Language: {t_lang_name}\n"
            f"Scenario: {scenario}\n"
            f"Tone Preference: {tone}\n\n"
            "IMPORTANT TRANSLATION RULES:\n"
            f"1. ALL translations (literal_translation and natural_expressions.text) MUST be in {t_lang_name}.\n"
            f"2. Explanations and cultural advice should be in {s_lang_name}.\n"
            f"3. You are translating FROM {s_lang_name} TO {t_lang_name}.\n\n"
            "IMPORTANT CULTURAL CONTEXT:\n"
            "- First, identify if the source text is a cultural idiom or greeting with non-literal meaning.\n"
            "- Chinese greetings like \"吃了吗？\" (Have you eaten?) or \"去哪儿？\" (Where are you going?) are NOT literal questions but equivalent to \"How are you?\" or \"Hello!\"\n"
            "- Japanese formal greetings like \"お疲れ様です\" are ritual phrases, not literal comments on tiredness.\n"
            "- Translate the ACTUAL INTENT and CULTURAL FUNCTION, not just the literal words.\n"
            f"- For 'natural_expressions', provide what a native {t_lang_name} speaker would ACTUALLY say in the same social context.\n\n"
            "Please return the following JSON structure (do not include Markdown code block markers, ensure valid JSON):\n"
            "{\n"
            f'  "literal_translation": "Word-for-word translation in {t_lang_name} (for reference only, may sound unnatural)",\n'
            '  "natural_expressions": [\n'
            f'    {{"text": "Natural expression in {t_lang_name} that a native speaker would ACTUALLY say", "explanation": "Why this expression is used and when it is appropriate (explain in {s_lang_name})"}},\n'
            f'    {{"text": "Alternative natural expression in {t_lang_name}", "explanation": "Context and usage notes (in {s_lang_name})"}},\n'
            f'    {{"text": "Another contextually appropriate option in {t_lang_name}", "explanation": "Situational guidance (in {s_lang_name})"}}\n'
            '  ],\n'
            f'  "cultural_advice": "Cultural advice (Markdown string, written in {s_lang_name}. Based on the \'{scenario}\' scenario and \'{tone}\' tone, provide deep cultural background analysis. Include: 1. The TRUE MEANING and social function of the source phrase (if it is an idiom/greeting); 2. How native speakers of {t_lang_name} express the same intent; 3. Cultural mindset differences; 4. Etiquette rules and potential misunderstandings; 5. Emotional reactions to expect. Use **bold** for emphasis, bullet points for clarity, ensure empty lines between sections, provide specific examples.)"\n'
            "}\n\n"
            f"Example for translating Chinese \"吃了吗？\" → English ({s_lang_name} → {t_lang_name}):\n"
            "{\n"
            '  "literal_translation": "Have you eaten?",\n'
            '  "natural_expressions": [\n'
            '    {"text": "How are you?", "explanation": "这是英语中最常见的问候语,相当于中文的\'吃了吗?\'的社交功能"},\n'
            '    {"text": "How\'s it going?", "explanation": "更随意的问候方式,适合朋友之间"},\n'
            '    {"text": "How\'s everything?", "explanation": "关心对方近况的友好问候"}\n'
            '  ],\n'
            '  "cultural_advice": "\'吃了吗?\'在中文里是传统问候语,并非真的询问是否用餐,而是表达关心..."\n'
            "}\n"
        )

        messages = [
            {"role": "system", "content": f"You are an expert cross-cultural translation assistant. You translate FROM {s_lang_name} TO {t_lang_name}. ALL translation outputs (literal_translation and natural_expressions.text) MUST be in {t_lang_name}. Explanations should be in {s_lang_name}. Always identify the TRUE social function of phrases before translating. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ]

        # Credentials: prefer environment variable; then structured credentials.json;
        # keep backward compatibility with legacy single-line `credentials`.
        creds = _read_credentials()

        # Choose token: environment variable overrides everything
        # Support multiple env var names for flexibility
        env_token = (
            os.environ.get("API_KEY") or 
            os.environ.get("OLLAMA_API_KEY") or 
            os.environ.get("OPENAI_API_KEY") or 
            os.environ.get("DEEPSEEK_API_KEY") or 
            os.environ.get("DEEPSEEK_API_KEY_0")
        )
        
        # Get API URL from environment
        env_api_url = (
            os.environ.get("API_URL") or
            os.environ.get("OLLAMA_API_URL") or
            os.environ.get("OPENAI_API_URL")
        )
        
        # Get model name from environment
        env_model = (
            os.environ.get("MODEL_NAME") or
            os.environ.get("OLLAMA_MODEL")
        )
        
        token = None
        api_url = None
        model_name = None
        
        if env_token:
            token = env_token
            api_url = env_api_url
            model_name = env_model
        else:
            # structured creds: {'tokens': {name: {token, api_url, model}}, 'default': name}
            tokens = creds.get("tokens") if isinstance(creds, dict) else None
            default_name = creds.get("default") if isinstance(creds, dict) else None
            if token_name and tokens and token_name in tokens:
                token = tokens[token_name].get("token")
                api_url = tokens[token_name].get("api_url")
                model_name = tokens[token_name].get("model")
            elif default_name and tokens and default_name in tokens:
                token = tokens[default_name].get("token")
                api_url = tokens[default_name].get("api_url")
                model_name = tokens[default_name].get("model")
            elif tokens:
                # pick the first available token
                first = next(iter(tokens.items()))
                token = first[1].get("token")
                api_url = first[1].get("api_url")
                model_name = first[1].get("model")

        # Set defaults: prefer Ollama (local, free)
        if not api_url:
            # allow top-level api_url in legacy kv formats
            if isinstance(creds, dict) and creds.get("api_url"):
                api_url = creds.get("api_url")
            else:
                # Default to Ollama local server
                api_url = "http://localhost:11434/v1"
        
        if not model_name:
            if isinstance(creds, dict) and creds.get("model"):
                model_name = creds.get("model")
            else:
                # Auto-detect model based on api_url
                if "localhost" in api_url or "11434" in api_url:
                    model_name = "qwen2.5:latest"  # Good multilingual Ollama model
                elif "deepseek" in api_url:
                    model_name = "deepseek-chat"
                else:
                    model_name = "gpt-3.5-turbo"  # Generic default
        
        # Ollama doesn't require API key, set dummy if using Ollama
        if not token:
            if "localhost" in api_url or "11434" in api_url:
                token = "ollama"  # Dummy token for Ollama
            else:
                token = None  # Will trigger missing credentials message

        # Try to call LLM API
        model_text = ""
        is_ollama = "localhost" in api_url or "11434" in api_url
        
        try:
            if token:
                # Use Ollama native API for better compatibility
                if is_ollama:
                    import requests
                    
                    # Remove /v1 suffix if present (use native Ollama API)
                    ollama_url = api_url.replace("/v1", "")
                    if not ollama_url.endswith("/api/chat"):
                        ollama_url = ollama_url.rstrip("/") + "/api/chat"
                    
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "stream": False,
                        "format": "json"  # Request JSON format from Ollama
                    }
                    
                    response = requests.post(ollama_url, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        model_text = result.get("message", {}).get("content", "")
                    else:
                        model_text = f"[Ollama Error] Status {response.status_code}: {response.text[:200]}"
                
                # Use OpenAI SDK for other APIs (Deepseek, OpenAI, etc)
                else:
                    from openai import OpenAI
                    
                    client = OpenAI(api_key=token, base_url=api_url)
                    
                    request_params = {
                        "model": model_name,
                        "messages": messages,
                        "stream": False,
                        "response_format": {"type": "json_object"}
                    }
                    
                    response = client.chat.completions.create(**request_params)
                    
                    try:
                        model_text = response.choices[0].message.content
                    except Exception:
                        try:
                            model_text = json.dumps(response)
                        except Exception:
                            model_text = str(response)
            else:
                model_text = "[Missing Credentials] API token not found. For Ollama (free): install Ollama and run 'ollama serve'. For other APIs: set API_KEY environment variable or credentials file."
        except ImportError as e:
            import_error = str(e)
            if is_ollama and "requests" in import_error:
                model_text = "[Module Not Installed] Please run: pip install requests"
            else:
                model_text = "[SDK Not Installed] Please run: pip install openai"
        except Exception as e:
            # Capture trace for debugging but do not raise
            error_msg = str(e)
            if "Connection" in error_msg or "connect" in error_msg.lower() or "timed out" in error_msg.lower():
                if is_ollama:
                    model_text = f"[Connection Error] Cannot connect to Ollama at {api_url}. Make sure Ollama is running. Try: ollama serve\n\nError: {error_msg}"
                else:
                    model_text = f"[Connection Error] Cannot connect to API at {api_url}. Check your network and API URL.\n\nError: {error_msg}"
            else:
                model_text = f"[API Call Error] {error_msg}"

        # If we got model_text from API, parse JSON
        if model_text and not model_text.startswith("[SDK Not Installed]") and not model_text.startswith("[Missing Credentials]") and not model_text.startswith("[Deepseek Call Error]"):
            # Debug: print raw output to console
            print(f"DEBUG: Raw model output:\n{model_text}\n" + "-"*20)

            try:
                # Clean up potential markdown markers
                clean_text = model_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                data = json.loads(clean_text.strip())
                
                literal = data.get("literal_translation", "") or "[No Literal Translation Output]"
                natural = data.get("natural_expressions", []) 
                if not natural:
                    natural = [{"text": "[No Natural Expression Output]", "explanation": ""}]
                advice = data.get("cultural_advice", "") or "[No Cultural Advice Output]"

                return {
                    "literal_translation": literal,
                    "natural_translation": natural, # List of dicts
                    "advice": advice,
                }
            except Exception as e:
                print(f"JSON Parsing failed: {e}")
                # parsing failed — continue to fallback
                pass

        # If we reach here, either SDK missing, token missing, API error, or parsing failed
        note = ""
        if model_text.startswith("[SDK Not Installed]"):
            note = "\n\n**Tip**: OpenAI SDK not installed. Please run `pip install openai`."
        elif model_text.startswith("[Missing Credentials]"):
            note = (
                "\n\n**Tip**: Using Ollama (Free & Local):\n"
                "1. Install: https://ollama.com/download\n"
                "2. Run: `ollama serve`\n"
                "3. Pull model: `ollama pull qwen2.5`\n\n"
                "Or use other API: set `API_KEY` environment variable or edit `credentials.json`"
            )
        elif model_text.startswith("[Connection Error]"):
            note = f"\n\n**Connection Error**: {model_text}"
        elif model_text.startswith("[API Call Error]"):
            note = f"\n\n**API Error**: {model_text}"

        # Fallback safe fake implementation
        literal = f"[Literal Example] ({s_lang} -> {t_lang}): {s_text}"
        # Natural needs to be a list now
        natural = [
            {"text": f"[Natural Expression Example] {s_text}", "explanation": f"(Scenario: {scenario}) This is an example of a more natural expression generated for the source text."}
        ]
        advice = (
            "【Cultural Advice Example】\n"
            "- Based on your selected scenario, remind the user to pay attention to polite language and local customs.\n"
            "- This will be generated by the large model based on source text and target culture in the future."
        ) + note

        return {
            "literal_translation": literal,
            "natural_translation": natural,
            "advice": advice,
        }
    except Exception as exc:
        # Ultimate fallback — never raise
        return {
            "literal_translation": "[Error] Cannot generate literal translation.",
            "natural_translation": [{"text": "[Error]", "explanation": f"Cannot generate natural translation: {str(exc)}"}],
            "advice": f"[Error] Exception during advice generation: {str(exc)}\n{traceback.format_exc()}",
        }
