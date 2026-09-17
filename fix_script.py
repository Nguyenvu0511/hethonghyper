# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_fitness = False
in_backup = False

for line in lines:
    if line.startswith('async def fitness_reminder(bot: Bot, user_telegram_id: str):'):
        new_lines.append('async def fitness_reminder(bot: Bot):\\n')
        new_lines.append('    from src.database.db_manager import db\\n')
        new_lines.append('    users = db.get_all_users()\\n')
        new_lines.append('    for u in users:\\n')
        new_lines.append('        user_id, telegram_id, username = u\\n')
        in_fitness = True
        continue
    if in_fitness:
        if line.startswith('    try:'):
            new_lines.append('        try:\\n')
            continue
        if line.startswith('        await bot.send_message('):
            new_lines.append('            await bot.send_message(\\n')
            continue
        if line.strip() == 'user_telegram_id,':
            new_lines.append('                telegram_id, \\n')
            continue
        if line.startswith('        )'):
            new_lines.append('            )\\n')
            continue
        if line.startswith('    except Exception as e:'):
            new_lines.append('        except Exception as e:\\n')
            continue
        if line.startswith('        logger.error'):
            new_lines.append('            logger.error(f"Lỗi khi gửi fitness_reminder: {e}")\\n')
            in_fitness = False
            continue
        if line.startswith('            '):
            new_lines.append('    ' + line)
            continue

    if line.startswith('async def daily_db_backup(bot: Bot, user_telegram_id: str):'):
        new_lines.append('async def daily_db_backup(bot: Bot):\\n')
        new_lines.append('    from src.database.db_manager import db\\n')
        new_lines.append('    users = db.get_all_users()\\n')
        new_lines.append('    if users:\\n')
        in_backup = True
        continue
    if in_backup:
        if line.startswith('    try:'):
            new_lines.append('        try:\\n')
            continue
        if line.startswith('        db_path ='):
            new_lines.append('            ' + line.strip() + '\\n')
            continue
        if line.startswith('        if os.path.exists'):
            new_lines.append('            ' + line.strip() + '\\n')
            continue
        if line.startswith('            file ='):
            new_lines.append('                ' + line.strip() + '\\n')
            continue
        if line.startswith('            await bot.send_document('):
            new_lines.append('                await bot.send_document(\\n')
            continue
        if line.strip() == 'user_telegram_id,':
            new_lines.append('                    users[0][1], \\n')
            continue
        if line.strip().startswith('document='):
            new_lines.append('                    ' + line.strip() + '\\n')
            continue
        if line.strip().startswith('caption='):
            new_lines.append('                    ' + line.strip() + '\\n')
            continue
        if line.strip().startswith('parse_mode='):
            new_lines.append('                    ' + line.strip() + '\\n')
            continue
        if line.strip().startswith(')'):
            new_lines.append('                )\\n')
            continue
        if line.startswith('            logger.info('):
            new_lines.append('                logger.info("Đã gửi file backup database qua Telegram.")\\n')
            continue
        if line.startswith('        else:'):
            new_lines.append('            else:\\n')
            continue
        if line.startswith('            logger.error('):
            new_lines.append('                logger.error("Không tìm thấy file database để backup!")\\n')
            continue
        if line.startswith('    except Exception as e:'):
            new_lines.append('        except Exception as e:\\n')
            continue
        if line.startswith('        logger.error(f"Lỗi khi gửi file backup'):
            new_lines.append('            logger.error(f"Lỗi khi gửi file backup: {e}")\\n')
            in_backup = False
            continue

    new_lines.append(line)

# Also fix setup_scheduler
for i in range(len(new_lines)):
    if 'def setup_scheduler(bot: Bot, user_telegram_id: str):' in new_lines[i]:
        new_lines[i] = new_lines[i].replace('def setup_scheduler(bot: Bot, user_telegram_id: str):', 'def setup_scheduler(bot: Bot):')
    if 'args=[bot, user_telegram_id]' in new_lines[i]:
        new_lines[i] = new_lines[i].replace('args=[bot, user_telegram_id]', 'args=[bot]')

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)