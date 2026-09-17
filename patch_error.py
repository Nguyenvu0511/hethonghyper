# -*- coding: utf-8 -*-
with open('src/ai/strategy_planner.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''            return {"daily_tasks": []}'''
new_code = '''            return {"error": str(e), "raw_text": response_text if 'response_text' in locals() else ""}'''
content = content.replace(old_code, new_code)

with open('src/ai/strategy_planner.py', 'w', encoding='utf-8') as f:
    f.write(content)