# -*- coding: utf-8 -*-
with open('src/ai/client.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''        if is_json:
            payload["response_format"] = {"type": "json_object"}'''

new_code = '''        if is_json and "gemini" not in AI_MODEL_NAME.lower():
            payload["response_format"] = {"type": "json_object"}'''

content = content.replace(old_code, new_code)

with open('src/ai/client.py', 'w', encoding='utf-8') as f:
    f.write(content)