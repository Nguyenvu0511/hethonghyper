# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace wake_up_call
old_wake = '''async def wake_up_call(bot: Bot, user_telegram_id: str):
    """Báo thức lúc 5:30 sáng"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "🌅 Chào buổi sáng! Đã 5:30 rồi.\\n"
            "Hãy thức dậy, rửa mặt và chuẩn bị tinh thần thép cho ngày hôm nay! Đợi một chút, tớ đang vạch định kế hoạch..."
        )
    except Exception as e:
        logger.error(f"Lỗi khi gọi wake_up_call: {e}")'''

new_wake = '''async def wake_up_call(bot: Bot):
    """Báo thức lúc 5:30 sáng"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "🌅 Chào buổi sáng! Đã 5:30 rồi.\\nHãy thức dậy, rửa mặt và chuẩn bị tinh thần thép cho ngày hôm nay! Đợi một chút, tớ đang vạch định kế hoạch..."
            )
        except Exception as e:
            logger.error(f"Lỗi khi gọi wake_up_call cho {telegram_id}: {e}")'''

# Replace skincare
old_skin = '''async def skincare_reminder(bot: Bot, user_telegram_id: str):
    """Nhắc nhở Skincare lúc 22:30"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "💆‍♂️ Đã 22:30. Đã đến giờ bảo dưỡng 'Giao diện'.\\n"
            "Hãy đi rửa mặt, thoa toner và kem dưỡng. Đừng quên đi ngủ sớm nhé!"
        )
    except Exception as e:
        logger.error(f"Lỗi khi gọi skincare_reminder: {e}")'''

new_skin = '''async def skincare_reminder(bot: Bot):
    """Nhắc nhở Skincare lúc 22:30"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "💆‍♂️ Đã 22:30. Đã đến giờ bảo dưỡng 'Giao diện'.\\nHãy đi rửa mặt, thoa toner và kem dưỡng. Đừng quên đi ngủ sớm nhé!"
            )
        except Exception as e:
            pass'''

# Replace fitness
old_fit = '''async def fitness_reminder(bot: Bot, user_telegram_id: str):
    """Nhắc nhở tập thể dục lúc 17:00"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "🏃‍♂️ Đã 17:00. Thanh toán nợ Thể chất!\\n"
            "Môn Thể dục của cậu đang F đấy. Hãy đứng dậy tập ngay 45 phút rồi chụp ảnh mồ hôi ướt đẫm gửi tớ.\\n"
            "Nếu không nộp báo cáo, tối nay cắt mạng nghỉ chơi!"
        )
    except Exception as e:
        logger.error(f"Lỗi khi gọi fitness_reminder: {e}")'''

new_fit = '''async def fitness_reminder(bot: Bot):
    """Nhắc nhở tập thể dục lúc 17:00"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "🏃‍♂️ Đã 17:00. Đứng dậy vận động thôi! Cố gắng duy trì sức khỏe để cày cuốc tốt hơn nhé!"
            )
        except Exception as e:
            pass'''

# Replace db backup
old_backup = '''async def daily_db_backup(bot: Bot, user_telegram_id: str):
    """Tự động backup DB lúc 23:59"""
    try:
        doc = FSInputFile("data/study_bot.db")
        await bot.send_document(user_telegram_id, doc, caption="💾 Database Backup tự động cuối ngày.")
    except Exception as e:
        logger.error(f"Lỗi khi gửi backup: {e}")'''

new_backup = '''async def daily_db_backup(bot: Bot):
    """Tự động backup DB lúc 23:59"""
    users = db.get_all_users()
    # Send only to the first user or admin (we just pick the first one)
    if users:
        try:
            doc = FSInputFile("data/study_bot.db")
            await bot.send_document(users[0][1], doc, caption="💾 Database Backup tự động cuối ngày.")
        except Exception as e:
            pass'''

content = content.replace(old_wake, new_wake).replace(old_skin, new_skin).replace(old_fit, new_fit).replace(old_backup, new_backup)

# Fix setup_scheduler signature
content = content.replace("def setup_scheduler(bot: Bot, user_telegram_id: str):", "def setup_scheduler(bot: Bot):")

# Fix args inside setup_scheduler
content = content.replace("args=[bot, user_telegram_id]", "args=[bot]")

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

main_content = main_content.replace('setup_scheduler(bot, "ADMIN_TELEGRAM_ID_HERE")', 'setup_scheduler(bot)')
main_content = main_content.replace('setup_scheduler(bot, user_telegram_id)', 'setup_scheduler(bot)') # just in case

with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(main_content)