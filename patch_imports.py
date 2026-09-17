with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from src.ai.gemini_vision import evaluate_image_report", "from src.ai.evaluator import evaluate_image_report")

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)