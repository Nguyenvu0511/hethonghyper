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
from src.utils.excel_generator import generate_tasks_excel
from aiogram.types import FSInputFile

async def morning_tasks_reminder(bot: Bot):
    """Gửi danh sách nhiệm vụ lúc 6:00 sáng cho tất cả user bằng Excel"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        tasks = db.get_daily_tasks(user_id)
        if tasks:
            completed_task_ids = db.get_completed_tasks_today(user_id)
            file_path = f"data/morning_tasks_{telegram_id}.xlsx"
            generate_tasks_excel(tasks, completed_task_ids, file_path)
            
            msg = f"🌅 <b>CHÀO BUỔI SÁNG {username}!</b>\n\nĐây là file Excel báo cáo nhiệm vụ học tập hôm nay của cậu. Hãy tải về xem và nhớ gõ <code>/done &lt;ID&gt;</code> khi làm xong nhé! Chúc một ngày năng suất!"
            try:
                excel_doc = FSInputFile(file_path, filename="Nhiem_vu_buoi_sang.xlsx")
                await bot.send_document(telegram_id, excel_doc, caption=msg, parse_mode="HTML")
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Lỗi gửi morning tasks Excel: {e}")

async def evening_tasks_check(bot: Bot):
    """Kiểm tra tiến độ lúc 23:30 tối và gửi báo cáo tổng kết"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        tasks = db.get_daily_tasks(user_id)
        if tasks:
            completed_task_ids = db.get_completed_tasks_today(user_id)
            file_path = f"data/evening_tasks_{telegram_id}.xlsx"
            generate_tasks_excel(tasks, completed_task_ids, file_path)
            
            percent = (len(completed_task_ids) / len(tasks)) * 100 if len(tasks) > 0 else 100
            
            msg = f"🌙 <b>23:30 RỒI! BÁO CÁO TỔNG KẾT NGÀY:</b>\n\nCậu đã hoàn thành <b>{len(completed_task_ids)}/{len(tasks)}</b> nhiệm vụ (<b>{percent:.1f}%</b>).\nChi tiết trạng thái Xanh/Cam đã được tô màu trong file Excel bên dưới. Hãy kiểm điểm lại bản thân trước khi đi ngủ nhé!"
            try:
                excel_doc = FSInputFile(file_path, filename="Bao_cao_cuoi_ngay.xlsx")
                await bot.send_document(telegram_id, excel_doc, caption=msg, parse_mode="HTML")
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Lỗi gửi evening tasks Excel: {e}")

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

from datetime import datetime, timedelta

async def check_upcoming_deadlines(bot: Bot):
    """Kiểm tra và nhắc nhở các task sắp tới deadline (15 phút)"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        tasks = db.get_daily_tasks(user_id)
        completed_task_ids = db.get_completed_tasks_today(user_id)
        
        if not tasks:
            continue
            
        now = datetime.now()
        target_time = now + timedelta(minutes=15)
        target_time_str = target_time.strftime("%H:%M")
        
        for t in tasks:
            task_id, category, title, description, time_str = t
            if task_id in completed_task_ids:
                continue
                
            if time_str == target_time_str:
                import html
                title_safe = html.escape(title)
                cat_safe = html.escape(category)
                msg = f"🚨 <b>BÁO ĐỘNG ĐỎ! CHUẨN BỊ DEADLINE!</b> 🚨\n\nChỉ còn 15 phút nữa là đến giờ làm nhiệm vụ:\n📌 <b>[{cat_safe}]</b> {title_safe}\n⏰ Thời gian: {time_str}\n\nHãy chuẩn bị sẵn sàng ngay bây giờ! Đừng để trễ hẹn!"
                try:
                    await bot.send_message(telegram_id, msg, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Lỗi gửi nhắc nhở deadline: {e}")

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
    
    # Lên lịch 23:30 tối kiểm tra tasks và gửi báo cáo cuối ngày
    scheduler.add_job(evening_tasks_check, 'cron', hour=23, minute=30, args=[bot])
    
    # Lên lịch 22:30 tối hàng ngày
    scheduler.add_job(skincare_reminder, 'cron', hour=22, minute=30, args=[bot, user_telegram_id])
    
    # Lên lịch 23:59 đêm để backup Database
    scheduler.add_job(daily_db_backup, 'cron', hour=23, minute=59, args=[bot, user_telegram_id])
    
    # Kiểm tra deadline mỗi 5 phút
    scheduler.add_job(check_upcoming_deadlines, 'cron', minute='*/5', args=[bot])
    
    scheduler.start()
    logger.info("Đã khởi động Scheduler (Cron jobs).")
    return scheduler
