import re

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace signatures
content = re.sub(r'async def wake_up_call\(bot: Bot, user_telegram_id: str\):', 'async def wake_up_call(bot: Bot):', content)
content = re.sub(r'async def skincare_reminder\(bot: Bot, user_telegram_id: str\):', 'async def skincare_reminder(bot: Bot):', content)
content = re.sub(r'async def fitness_reminder\(bot: Bot, user_telegram_id: str\):', 'async def fitness_reminder(bot: Bot):', content)
content = re.sub(r'async def daily_db_backup\(bot: Bot, user_telegram_id: str\):', 'async def daily_db_backup(bot: Bot):', content)

# For wake_up_call, replace user_telegram_id with looping
wake_target = r'''    try:
        await bot.send_message\(
            user_telegram_id,'''
wake_rep = r'''    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id,'''
content = re.sub(wake_target, wake_rep, content)

# For skincare_reminder
skin_target = r'''    try:
        await bot.send_message\(
            user_telegram_id,'''
content = re.sub(skin_target, wake_rep, content)

# For fitness_reminder
fit_target = r'''    try:
        await bot.send_message\(
            user_telegram_id,'''
content = re.sub(fit_target, wake_rep, content)

# For db backup
db_target = r'''    try:
        doc = FSInputFile\("data/study_bot.db"\)
        await bot.send_document\(user_telegram_id, doc, caption="💾 Database Backup tự động cuối ngày."\)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi backup: \{e\}"\)'''

db_rep = r'''    users = db.get_all_users()
    if users:
        try:
            doc = FSInputFile("data/study_bot.db")
            await bot.send_document(users[0][1], doc, caption="💾 Database Backup tự động cuối ngày.")
        except Exception as e:
            logger.error(f"Lỗi khi gửi backup: {e}")'''
content = re.sub(db_target, db_rep, content)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)