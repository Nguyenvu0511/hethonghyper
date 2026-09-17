import re

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix fitness_reminder signature and body
fit_old = r'''async def fitness_reminder\(bot: Bot, user_telegram_id: str\):
    """Nhắc nhở tập thể dục lúc 17:00"""
    try:
        await bot.send_message\(
            user_telegram_id, 
            "🏃‍♂️ Đã 17:00. Thanh toán nợ Thể chất!\\n"
            "Môn Thể dục của cậu đang F đấy. Hãy đứng dậy tập ngay 45 phút rồi chụp ảnh mồ hôi ướt đẫm gửi tớ.\\n"
            "Nếu không nộp báo cáo, tối nay cắt mạng nghỉ chơi!"
        \)
    except Exception as e:
        logger.error\(f"Lỗi khi gửi fitness_reminder: \{e\}"\)'''

fit_new = r'''async def fitness_reminder(bot: Bot):
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
            logger.error(f"Lỗi khi gửi fitness_reminder: {e}")'''
content = re.sub(fit_old, fit_new, content)

# Fix daily_db_backup signature and body
db_old = r'''async def daily_db_backup\(bot: Bot, user_telegram_id: str\):
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
        logger.error\(f"Lỗi khi gửi file backup: \{e\}"\)'''

db_new = r'''async def daily_db_backup(bot: Bot):
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
            logger.error(f"Lỗi khi gửi file backup: {e}")'''
content = re.sub(db_old, db_new, content)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")