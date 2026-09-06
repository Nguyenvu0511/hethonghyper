import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

logger = logging.getLogger(__name__)

async def wake_up_call(bot: Bot, user_telegram_id: str):
    """Báo thức lúc 5:30 sáng"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "🌅 Chào buổi sáng! Đã 5:30 rồi.\n"
            "Hãy ra khỏi giường, chụp một bức ảnh ngoài trời và gửi cho tớ để điểm danh nhé!\n"
            "Cậu có 10 phút. Không làm là trừ EXP!"
        )
    except Exception as e:
        logger.error(f"Lỗi khi gửi wake_up_call: {e}")

async def skincare_reminder(bot: Bot, user_telegram_id: str):
    """Nhắc nhở Skincare lúc 22:30"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "💆‍♂️ Đã 22:30. Đã đến giờ bảo dưỡng 'Giao diện'.\n"
            "Hãy đi rửa mặt, thoa toner và kem dưỡng. Đừng quên đi ngủ sớm nhé!"
        )
    except Exception as e:
        logger.error(f"Lỗi khi gửi skincare_reminder: {e}")

async def fitness_reminder(bot: Bot, user_telegram_id: str):
    """Nhắc nhở tập thể dục lúc 17:00"""
    try:
        await bot.send_message(
            user_telegram_id, 
            "🏋️‍♂️ Đã 17:00. Thanh toán nợ Thể chất!\n"
            "Môn Thể dục của cậu đang F đấy. Hãy đứng dậy tập ngay 45 phút rồi chụp ảnh mồ hôi ướt đẫm gửi tớ.\n"
            "Nếu không nộp báo cáo, tối nay cắt mạng nghỉ chơi!"
        )
    except Exception as e:
        logger.error(f"Lỗi khi gửi fitness_reminder: {e}")

from src.database.db_manager import db

async def morning_tasks_reminder(bot: Bot):
    """Gửi danh sách nhiệm vụ lúc 6:00 sáng cho tất cả user"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        tasks = db.get_daily_tasks(user_id)
        if tasks:
            msg = f"🌅 **CHÀO BUỔI SÁNG {username}!**\nĐây là nhiệm vụ học tập hôm nay của cậu:\n\n"
            for t in tasks:
                task_id, category, title, description, target_time = t
                msg += f"▫️ **ID {task_id}** | {target_time} - {title}\n"
            msg += "\nNhớ gõ `/done <ID>` khi hoàn thành nhé! Chúc một ngày năng suất!"
            try:
                await bot.send_message(telegram_id, msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Lỗi gửi morning tasks: {e}")

async def evening_tasks_check(bot: Bot):
    """Kiểm tra tiến độ lúc 22:00 tối"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        # Lấy các task chưa làm (hiện tại chưa query tiến độ chi tiết, chỉ nhắc nhở chung)
        try:
            await bot.send_message(
                telegram_id, 
                "🌙 **22:00 RỒI!** Cậu đã hoàn thành hết các nhiệm vụ học thuật hôm nay chưa?\n"
                "Hãy gõ `/tasks` để kiểm tra lại và `/done <ID>` để điểm danh trước khi đi ngủ nhé!"
            )
        except Exception as e:
            logger.error(f"Lỗi gửi evening tasks: {e}")

from src.scraper.mydtu_scraper import crawl_new_announcements
from src.ai.strategy_planner import summarize_announcement

async def check_announcements_cron(bot: Bot):
    """Kiểm tra thông báo mới trên MyDTU lúc 12:00 và 18:00"""
    logger.info("Đang chạy Cron Job kiểm tra thông báo MyDTU...")
    try:
        new_items = await crawl_new_announcements()
        if not new_items:
            logger.info("Không có thông báo mới nào chưa đọc.")
            return

        users = db.get_all_users()
        for u in users:
            user_id, telegram_id, username = u
            
            await bot.send_message(
                telegram_id,
                f"🚨 **PHÁT HIỆN {len(new_items)} THÔNG BÁO MỚI TỪ MYDTU** 🚨\n"
                f"Đang tiến hành phân tích nội dung..."
            )
            
            for item in new_items:
                summary = summarize_announcement(item['content'])
                msg = f"📌 **{item['title']}**\n\n{summary}\n\nChi tiết: [Link MyDTU]({item['url']})"
                
                try:
                    await bot.send_message(telegram_id, msg, parse_mode="Markdown")
                    db.mark_announcement_seen(item['id'], item['title'])
                    # Sleep 1s to avoid telegram rate limit
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Lỗi gửi thông báo (ID: {item['id']}): {e}")

    except Exception as e:
        logger.error(f"Lỗi trong check_announcements_cron: {e}")

from aiogram.types import FSInputFile
import os

async def daily_db_backup(bot: Bot, user_telegram_id: str):
    """Gửi file database qua Telegram lúc 23:59 mỗi ngày để backup"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'learning_system.db')
        if os.path.exists(db_path):
            file = FSInputFile(db_path, filename="learning_system_backup.db")
            await bot.send_document(
                user_telegram_id, 
                document=file, 
                caption="💾 **BACKUP DATABASE TỰ ĐỘNG** 💾\nĐây là toàn bộ dữ liệu của cậu tính đến thời điểm hiện tại. Hãy giữ tin nhắn này cẩn thận, nếu VPS sập thì dùng file này để khôi phục!",
                parse_mode="Markdown"
            )
            logger.info("Đã gửi file backup database qua Telegram.")
        else:
            logger.error("Không tìm thấy file database để backup!")
    except Exception as e:
        logger.error(f"Lỗi khi gửi file backup: {e}")

def setup_scheduler(bot: Bot, user_telegram_id: str):
    """Khởi tạo và chạy Scheduler"""
    scheduler = AsyncIOScheduler(timezone='Asia/Ho_Chi_Minh')
    
    # Lên lịch 5:30 sáng hàng ngày
    scheduler.add_job(wake_up_call, 'cron', hour=5, minute=30, args=[bot, user_telegram_id])
    
    # Gửi tasks lúc 6:00
    scheduler.add_job(morning_tasks_reminder, 'cron', hour=6, minute=0, args=[bot])
    
    # Lên lịch 12:00 và 18:00 kiểm tra thông báo MyDTU
    scheduler.add_job(check_announcements_cron, 'cron', hour=12, minute=0, args=[bot])
    scheduler.add_job(check_announcements_cron, 'cron', hour=18, minute=0, args=[bot])
    
    # Lên lịch 17:00 chiều
    scheduler.add_job(fitness_reminder, 'cron', hour=17, minute=0, args=[bot, user_telegram_id])
    
    # Lên lịch 22:00 tối kiểm tra tasks
    scheduler.add_job(evening_tasks_check, 'cron', hour=22, minute=0, args=[bot])
    
    # Lên lịch 22:30 tối hàng ngày
    scheduler.add_job(skincare_reminder, 'cron', hour=22, minute=30, args=[bot, user_telegram_id])
    
    # Lên lịch 23:59 đêm để backup Database
    scheduler.add_job(daily_db_backup, 'cron', hour=23, minute=59, args=[bot, user_telegram_id])
    
    scheduler.start()
    logger.info("Đã khởi động Scheduler (Cron jobs).")
    return scheduler
