# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
async def weekly_timetable_sync(bot: Bot):
    """Tự động cào lịch học mới vào lúc 23:00 tối Chủ Nhật hàng tuần"""
    logger.info("Bắt đầu tự động đồng bộ lịch học tuần mới...")
    from src.scraper.mydtu_scraper import crawl_timetable
    try:
        await crawl_timetable()
        logger.info("Đã đồng bộ lịch học tuần mới thành công!")
    except Exception as e:
        logger.error(f"Lỗi khi đồng bộ lịch học tuần mới: {e}")
'''
# add new_func before setup_scheduler
content = content.replace("def setup_scheduler(bot: Bot, user_telegram_id: str):", new_func + "\ndef setup_scheduler(bot: Bot, user_telegram_id: str):")

# add job to setup_scheduler
job_code = "    # Cập nhật lịch học tuần mới vào 23:00 tối Chủ Nhật\n    scheduler.add_job(weekly_timetable_sync, 'cron', day_of_week='sun', hour=23, minute=0, args=[bot])\n\n    # Lên lịch 5:30"
content = content.replace("# Lên lịch 5:30", job_code)
# Windows issue with unicode in script
with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)