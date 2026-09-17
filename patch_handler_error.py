# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''        else:
            await msg.edit_text("❌ Lỗi sinh lịch trình từ AI.")'''

new_code = '''        else:
            err = plan.get('error', 'Không có error') if plan else 'Plan is None'
            raw = plan.get('raw_text', '') if plan else ''
            import html
            await msg.edit_text(f"❌ Lỗi sinh lịch trình từ AI.\\nLỗi: {html.escape(err)}\\nRaw: {html.escape(raw)[:1000]}", parse_mode="HTML")'''

content = content.replace(old_code, new_code)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)