# -*- coding: utf-8 -*-
import re

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_target_func = False
target_funcs = ['wake_up_call', 'skincare_reminder', 'fitness_reminder']
current_func = None

for line in lines:
    # Fix signature
    if line.startswith('async def ') and '(bot: Bot, user_telegram_id: str):' in line:
        line = line.replace('(bot: Bot, user_telegram_id: str):', '(bot: Bot):')
        for tf in target_funcs:
            if tf in line:
                current_func = tf
                in_target_func = True
                new_lines.append(line)
                new_lines.append('    from src.database.db_manager import db\n')
                new_lines.append('    users = db.get_all_users()\n')
                new_lines.append('    for u in users:\n')
                new_lines.append('        user_id, telegram_id, username = u\n')
                break
        else:
            if 'daily_db_backup' in line:
                current_func = 'daily_db_backup'
                in_target_func = True
                new_lines.append(line)
                new_lines.append('    from src.database.db_manager import db\n')
                new_lines.append('    users = db.get_all_users()\n')
                new_lines.append('    if users:\n')
            else:
                new_lines.append(line)
        continue

    if in_target_func:
        if line.startswith('def ') or line.startswith('async def '):
            in_target_func = False
            current_func = None

    if in_target_func:
        # Shift body
        if not line.startswith('    """') and not line.strip() == '':
            line = '    ' + line
        
        # Replace variable
        if current_func in target_funcs:
            line = line.replace('user_telegram_id', 'telegram_id')
        elif current_func == 'daily_db_backup':
            line = line.replace('user_telegram_id', 'users[0][1]')

    new_lines.append(line)

# Also fix setup_scheduler
for i in range(len(new_lines)):
    if 'def setup_scheduler(bot: Bot, user_telegram_id: str):' in new_lines[i]:
        new_lines[i] = new_lines[i].replace('def setup_scheduler(bot: Bot, user_telegram_id: str):', 'def setup_scheduler(bot: Bot):')
    if 'args=[bot, user_telegram_id]' in new_lines[i]:
        new_lines[i] = new_lines[i].replace('args=[bot, user_telegram_id]', 'args=[bot]')

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Fix main_bot.py
with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    main_content = f.read()
main_content = re.sub(r'setup_scheduler\(bot, "ADMIN_TELEGRAM_ID_HERE"\)', 'setup_scheduler(bot)', main_content)
with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("Done")