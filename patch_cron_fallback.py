# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''                    for item in schedule:
                        if item.get("weekday") == today_weekday:'''

new_code = '''                    for item in schedule:
                        wd = item.get("weekday")
                        if not wd and "(" in item.get("raw_info", ""):
                            wd = item.get("raw_info").split("(")[0].strip()
                        if wd == today_weekday:'''

content = content.replace(old_code, new_code)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)