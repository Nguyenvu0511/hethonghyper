# -*- coding: utf-8 -*-
with open('src/database/db_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_query = '''                SELECT task_id, category, title, description, target_time 
                FROM tasks 
                WHERE user_id = ? AND frequency = 'daily'
'''

new_query = '''                SELECT task_id, category, title, description, target_time 
                FROM tasks 
                WHERE user_id = ? AND frequency = 'daily'
                ORDER BY target_time ASC
'''

content = content.replace(old_query, new_query)

with open('src/database/db_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)