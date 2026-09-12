import os
import json
import httpx
import logging
import base64
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../..", "API_KEYS.txt"))

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class AIClient:
    def __init__(self):
        self.use_openai = bool(OPENAI_API_BASE and OPENAI_API_KEY)
        self.use_gemini = bool(not self.use_openai and GEMINI_API_KEY)
        
        if not self.use_openai and not self.use_gemini:
            logger.warning("Không có cấu hình AI nào được tìm thấy (OpenAI/WusRouter hoặc Gemini)!")

    def generate_text(self, prompt, is_json=False):
        if self.use_openai:
            return self._generate_openai_text(prompt, is_json)
        elif self.use_gemini:
            return self._generate_gemini_text(prompt, is_json)
        else:
            raise Exception("Chưa cấu hình API Key cho AI.")

    def _generate_openai_text(self, prompt, is_json=False):
        url = f"{OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Deepseek-v4-pro có thể không hỗ trợ response_format=json_object chuẩn OpenAI
        # nên ta cứ truyền vào system prompt hoặc user prompt
        payload = {
            "model": AI_MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if is_json:
            payload["response_format"] = {"type": "json_object"}
            
        with httpx.Client(timeout=180.0) as client:
            res = client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            
            # Loại bỏ <think>...</think> nếu có (đặc thù của dòng DeepSeek R1)
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            return content

    def _generate_gemini_text(self, prompt, is_json=False):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if is_json:
            payload["generationConfig"] = {"responseMimeType": "application/json"}
            
        with httpx.Client(timeout=60.0) as client:
            res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def generate_vision(self, prompt, image_path):
        # Ưu tiên dùng Gemini cho ảnh vì DeepSeek R1 không có vision
        if self.use_gemini:
            return self._generate_gemini_vision(prompt, image_path)
        elif self.use_openai:
            return self._generate_openai_vision(prompt, image_path)
        else:
            raise Exception("Chưa cấu hình API Key cho AI.")

    def _generate_openai_vision(self, prompt, image_path):
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
            
        url = f"{OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": AI_MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
        with httpx.Client(timeout=60.0) as client:
            res = client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    def _generate_gemini_vision(self, prompt, image_path):
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
                ]
            }]
        }
        with httpx.Client(timeout=60.0) as client:
            res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

ai_client = AIClient()
