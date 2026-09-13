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
    """Gửi danh sách nhiệm vụ lúc 6:00 sáng cho tất cả user"""
    from datetime import datetime
    import json
    import os
    from src.ai.strategy_planner import generate_daily_plan
    
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        
        # Tự động lập kế hoạch linh động cho HÔM NAY
        try:
            # Lấy thứ và ngày
            now = datetime.now()
            weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
            today_weekday = weekday_names[now.weekday()]
            
            # Đọc lịch
            timetable_today = ""
            if os.path.exists("data/last_schedule.json"):
                with open("data/last_schedule.json", "r", encoding="utf-8") as f:
                    schedule = json.load(f)
                    for item in schedule:
                        if item.get("weekday") == today_weekday:
                            timetable_today += f"- {item.get('raw_info')}\n"
            
            # Đọc điểm
            records_text = ""
            if os.path.exists("scores_output.json"):
                with open("scores_output.json", "r", encoding="utf-8") as f:
                    scores = json.load(f)
                    for item in scores:
                        if item['diem_chu'] in ['F', 'D', 'D+', 'C-']:
                            records_text += f"- Môn yếu: {item['ten_mon']} (Điểm: {item['diem_chu']})\n"
            
            if records_text:
                plan = generate_daily_plan(records_text, timetable_today, f"{today_weekday} {now.strftime('%d/%m')}")
                if plan and plan.get("daily_tasks"):
                    # Xóa tasks cũ và lưu tasks mới
                    db.clear_old_tasks_and_roadmap(user_id)
                    for t in plan["daily_tasks"]:
                        db.save_task(user_id, "daily", t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), t.get("target_time", "20:00"))
        except Exception as e:
            logger.error(f"Lỗi khi tự động lập kế hoạch sáng: {e}")
            
        tasks = db.get_daily_tasks(user_id)
        if tasks:
            completed_task_ids = db.get_completed_tasks_today(user_id)
            
            import html
            msg_text = f"🌅 <b>CHÀO BUỔI SÁNG {html.escape(username)}!</b>\nĐây là nhiệm vụ học tập hôm nay của cậu:\n\n"
            
            for t in tasks:
                task_id, category, title, description, target_time = t
                status_icon = "✅" if task_id in completed_task_ids else "▫️"
                
                task_info = f"{status_icon} <b>ID {task_id}</b> | {target_time} - {html.escape(title)}\n"
                
                if len(msg_text) + len(task_info) > 3500:
                    try:
                        await bot.send_message(telegram_id, msg_text, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Lỗi gửi morning tasks 1: {e}")
                    msg_text = ""
                    
                msg_text += task_info
                
            msg_text += "\nNhớ gõ <code>/done &lt;ID_Nhiệm_vụ&gt;</code> khi hoàn thành nhé! Chúc một ngày năng suất!"
            
            if msg_text:
                try:
                    await bot.send_message(telegram_id, msg_text, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Lỗi gửi morning tasks 2: {e}")

async def evening_tasks_check(bot: Bot):
    """Kiểm tra tiến độ lúc 23:30 tối và gửi báo cáo tổng kết"""
    users = db.get_all_users()
    for u in users:
        user_id, telegram_id, username = u
        tasks = db.get_daily_tasks(user_id)
        if tasks:
            completed_task_ids = db.get_completed_tasks_today(user_id)
            percent = (len(completed_task_ids) / len(tasks)) * 100 if len(tasks) > 0 else 100
            
            import html
            msg_text = f"🌙 <b>23:30 RỒI! BÁO CÁO TỔNG KẾT NGÀY:</b>\n\nCậu đã hoàn thành <b>{len(completed_task_ids)}/{len(tasks)}</b> nhiệm vụ (<b>{percent:.1f}%</b>).\n\n"
            
            for t in tasks:
                task_id, category, title, description, target_time = t
                if task_id not in completed_task_ids:
                    task_info = f"❌ <b>ID {task_id}</b> | {target_time} - {html.escape(title)}\n"
                    if len(msg_text) + len(task_info) > 3500:
                        try:
                            await bot.send_message(telegram_id, msg_text, parse_mode="HTML")
                        except Exception as e:
                            logger.error(f"Lỗi gửi evening tasks 1: {e}")
                        msg_text = ""
                    msg_text += task_info
            
            msg_text += "\nHãy kiểm điểm lại bản thân trước khi đi ngủ nhé!"
            
            if msg_text:
                try:
                    await bot.send_message(telegram_id, msg_text, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Lỗi gửi evening tasks 2: {e}")

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
