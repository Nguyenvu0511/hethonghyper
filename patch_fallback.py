# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# In command_tasks_handler
old_tasks = '''                for item in schedule:
                    if item.get("weekday") == today_weekday:
'''
new_tasks = '''                for item in schedule:
                    wd = item.get("weekday")
                    if not wd and "(" in item.get("raw_info", ""):
                        wd = item.get("raw_info").split("(")[0].strip()
                    if wd == today_weekday:
'''
content = content.replace(old_tasks, new_tasks)

# In command_lichhoc_handler
old_lichhoc = '''    for item in schedule:
        wd = item.get("weekday", "Không rõ")
'''
new_lichhoc = '''    for item in schedule:
        wd = item.get("weekday")
        if not wd and "(" in item.get("raw_info", ""):
            wd = item.get("raw_info").split("(")[0].strip()
        elif not wd:
            wd = "Không rõ"
'''
content = content.replace(old_lichhoc, new_lichhoc)

# In command_plan_today_handler
old_plan = '''                for item in schedule:
                    if item.get("weekday") == today_weekday:
'''
new_plan = '''                for item in schedule:
                    wd = item.get("weekday")
                    if not wd and "(" in item.get("raw_info", ""):
                        wd = item.get("raw_info").split("(")[0].strip()
                    if wd == today_weekday:
'''
content = content.replace(old_plan, new_plan)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)