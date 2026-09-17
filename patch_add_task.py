# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(
    'db.save_task(user_id, "daily", t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), t.get("target_time", "20:00"))',
    'db.add_task(user_id, t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), "daily", t.get("target_time", "20:00"))'
)
with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(
    'db.save_task(user_id, "daily", t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), t.get("target_time", "20:00"))',
    'db.add_task(user_id, t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), "daily", t.get("target_time", "20:00"))'
)
with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)