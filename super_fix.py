import sys

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

def replace_func(content, func_name, user_var):
    start = content.find(f'async def {func_name}(bot: Bot, {user_var}: str):')
    if start == -1: return content
    end = content.find('async def ', start + 10)
    if end == -1:
        end = content.find('def setup_scheduler', start)
    
    old_body = content[start:end]
    
    # We want to change the signature
    new_body = old_body.replace(f'async def {func_name}(bot: Bot, {user_var}: str):', f'async def {func_name}(bot: Bot):')
    
    # Insert the loop right after the docstring
    doc_end = new_body.find('"""')
    doc_end = new_body.find('"""', doc_end + 3) + 3
    
    loop_code = f"\n    from src.database.db_manager import db\n    users = db.get_all_users()\n    for u in users:\n        user_id, {user_var}, username = u"
    
    # We must indent EVERYTHING after doc_end by 4 spaces
    rest = new_body[doc_end:]
    rest_lines = rest.split('\n')
    new_rest = []
    for line in rest_lines:
        if line.strip() == '':
            new_rest.append(line)
        else:
            new_rest.append('    ' + line)
            
    new_body = new_body[:doc_end] + loop_code + '\n'.join(new_rest)
    
    return content.replace(old_body, new_body)

content = replace_func(content, 'wake_up_call', 'user_telegram_id')
content = replace_func(content, 'skincare_reminder', 'user_telegram_id')
content = replace_func(content, 'fitness_reminder', 'user_telegram_id')

# Now for daily_db_backup
start = content.find(f'async def daily_db_backup(bot: Bot, user_telegram_id: str):')
end = content.find('from datetime import datetime', start)
old_body = content[start:end]
new_body = old_body.replace(f'async def daily_db_backup(bot: Bot, user_telegram_id: str):', f'async def daily_db_backup(bot: Bot):')
doc_end = new_body.find('"""')
doc_end = new_body.find('"""', doc_end + 3) + 3

loop_code = f"\n    from src.database.db_manager import db\n    users = db.get_all_users()\n    if users:\n        user_telegram_id = users[0][1]"

rest = new_body[doc_end:]
rest_lines = rest.split('\n')
new_rest = []
for line in rest_lines:
    if line.strip() == '':
        new_rest.append(line)
    else:
        new_rest.append('    ' + line)

new_body = new_body[:doc_end] + loop_code + '\n'.join(new_rest)
content = content.replace(old_body, new_body)

# Finally setup_scheduler
content = content.replace('def setup_scheduler(bot: Bot, user_telegram_id: str):', 'def setup_scheduler(bot: Bot):')
content = content.replace('args=[bot, user_telegram_id]', 'args=[bot]')

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    main = f.read()
main = main.replace('setup_scheduler(bot, "ADMIN_TELEGRAM_ID_HERE")', 'setup_scheduler(bot)')
with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(main)
