# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the functions manually and perfectly
import re

content = re.sub(
r'''async def wake_up_call\(bot: Bot, user_telegram_id: str\):
    """Báo thức lúc 5:30 sáng"""
    try:
        await bot.send_message\(
            user_telegram_id, 
            "🌅 Chào buổi sáng! Đã 5:30 rồi.\\n"
            "Hãy ra khỏi giường, chụp một bức ảnh ngoài trời và gửi cho tớ để điểm danh nhé!\\n"
            "Cậu có 10 phút. Không làm là trừ EXP!"
        \)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi wake_up_call: \{e\}"\)''',
r'''async def wake_up_call(bot: Bot):
    """Báo thức lúc 5:30 sáng"""
    from src.database.db_manager import db
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "🌅 Chào buổi sáng! Đã 5:30 rồi.\\n"
                "Hãy ra khỏi giường, chụp một bức ảnh ngoài trời và gửi cho tớ để điểm danh nhé!\\n"
                "Cậu có 10 phút. Không làm là trừ EXP!"
            )
        except Exception as e:
            logger.error(f"Lỗi khi gửi wake_up_call: {e}")''', content)

content = re.sub(
r'''async def skincare_reminder\(bot: Bot, user_telegram_id: str\):
    """Nhắc nhở Skincare lúc 22:30"""
    try:
        await bot.send_message\(
            user_telegram_id, 
            "💆‍♂️ Đã 22:30. Đã đến giờ bảo dưỡng 'Giao diện'.\\n"
            "Hãy đi rửa mặt, thoa toner và kem dưỡng. Đừng quên đi ngủ sớm nhé!"
        \)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi skincare_reminder: \{e\}"\)''',
r'''async def skincare_reminder(bot: Bot):
    """Nhắc nhở Skincare lúc 22:30"""
    from src.database.db_manager import db
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "💆‍♂️ Đã 22:30. Đã đến giờ bảo dưỡng 'Giao diện'.\\n"
                "Hãy đi rửa mặt, thoa toner và kem dưỡng. Đừng quên đi ngủ sớm nhé!"
            )
        except Exception as e:
            logger.error(f"Lỗi khi gửi skincare_reminder: {e}")''', content)

content = re.sub(
r'''async def fitness_reminder\(bot: Bot, user_telegram_id: str\):
    """Nhắc nhở tập thể dục lúc 17:00"""
    try:
        await bot.send_message\(
            user_telegram_id, 
            "🏃‍♂️ Đã 17:00. Thanh toán nợ Thể chất!\\n"
            "Môn Thể dục của cậu đang F đấy. Hãy đứng dậy tập ngay 45 phút rồi chụp ảnh mồ hôi ướt đẫm gửi tớ.\\n"
            "Nếu không nộp báo cáo, tối nay cắt mạng nghỉ chơi!"
        \)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi fitness_reminder: \{e\}"\)''',
r'''async def fitness_reminder(bot: Bot):
    """Nhắc nhở tập thể dục lúc 17:00"""
    from src.database.db_manager import db
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        try:
            await bot.send_message(
                telegram_id, 
                "🏃‍♂️ Đã 17:00. Thanh toán nợ Thể chất!\\n"
                "Môn Thể dục của cậu đang F đấy. Hãy đứng dậy tập ngay 45 phút rồi chụp ảnh mồ hôi ướt đẫm gửi tớ.\\n"
                "Nếu không nộp báo cáo, tối nay cắt mạng nghỉ chơi!"
            )
        except Exception as e:
            logger.error(f"Lỗi khi gửi fitness_reminder: {e}")''', content)

content = re.sub(
r'''async def daily_db_backup\(bot: Bot, user_telegram_id: str\):
    """Gửi file database qua Telegram lúc 23:59 mỗi ngày để backup"""
    try:
        db_path = os.path.join\(os.path.dirname\(os.path.dirname\(os.path.dirname\(__file__\)\)\), 'data', 'learning_system.db'\)
        if os.path.exists\(db_path\):
            file = FSInputFile\(db_path, filename="learning_system_backup.db"\)
            await bot.send_document\(
                user_telegram_id, 
                document=file, 
                caption="💾 \*\*BACKUP DATABASE TỰ ĐỘNG\*\* 💾\\nĐây là toàn bộ dữ liệu của cậu tính đến thời điểm hiện tại. Hãy giữ tin nhắn này cẩn thận, nếu VPS sập thì dùng file này để khôi phục!",
                parse_mode="Markdown"
            \)
            logger.info\("Đã gửi file backup database qua Telegram."\)
        else:
            logger.error\("Không tìm thấy file database để backup!"\)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi file backup: \{e\}"\)''',
r'''async def daily_db_backup(bot: Bot):
    """Gửi file database qua Telegram lúc 23:59 mỗi ngày để backup"""
    from src.database.db_manager import db
    users = db.get_all_users()
    if users:
        try:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'learning_system.db')
            if os.path.exists(db_path):
                file = FSInputFile(db_path, filename="learning_system_backup.db")
                await bot.send_document(
                    users[0][1], 
                    document=file, 
                    caption="💾 **BACKUP DATABASE TỰ ĐỘNG** 💾\\nĐây là toàn bộ dữ liệu của cậu tính đến thời điểm hiện tại. Hãy giữ tin nhắn này cẩn thận, nếu VPS sập thì dùng file này để khôi phục!",
                    parse_mode="Markdown"
                )
                logger.info("Đã gửi file backup database qua Telegram.")
            else:
                logger.error("Không tìm thấy file database để backup!")
        except Exception as e:
            logger.error(f"Lỗi khi gửi file backup: {e}")''', content)

content = re.sub(r'def setup_scheduler\(bot: Bot, user_telegram_id: str\):', 'def setup_scheduler(bot: Bot):', content)
content = re.sub(r"scheduler\.add_job\(wake_up_call, 'cron', hour=5, minute=30, args=\[bot, user_telegram_id\]\)", "scheduler.add_job(wake_up_call, 'cron', hour=5, minute=30, args=[bot])", content)
content = re.sub(r"scheduler\.add_job\(skincare_reminder, 'cron', hour=22, minute=30, args=\[bot, user_telegram_id\]\)", "scheduler.add_job(skincare_reminder, 'cron', hour=22, minute=30, args=[bot])", content)
content = re.sub(r"scheduler\.add_job\(fitness_reminder, 'cron', hour=17, minute=0, args=\[bot, user_telegram_id\]\)", "scheduler.add_job(fitness_reminder, 'cron', hour=17, minute=0, args=[bot])", content)
content = re.sub(r"scheduler\.add_job\(daily_db_backup, 'cron', hour=23, minute=59, args=\[bot, user_telegram_id\]\)", "scheduler.add_job(daily_db_backup, 'cron', hour=23, minute=59, args=[bot])", content)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

main_content = re.sub(r'setup_scheduler\(bot, "ADMIN_TELEGRAM_ID_HERE"\)', 'setup_scheduler(bot)', main_content)

with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("Done")