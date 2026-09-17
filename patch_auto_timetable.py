# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_job_func = '''
async def auto_update_timetable(bot: Bot):
    """Tự động cào lịch học tuần mới vào tối Chủ Nhật"""
    try:
        from src.scraper.mydtu_scraper import crawl_timetable
        import json
        logger.info("Chạy cronjob: Tự động cập nhật lịch học tuần mới...")
        timetable = await crawl_timetable()
        if timetable:
            with open("data/last_schedule.json", "w", encoding="utf-8") as f:
                json.dump(timetable, f, ensure_ascii=False, indent=2)
            logger.info("Đã cập nhật lịch học tuần mới thành công!")
    except Exception as e:
        logger.error(f"Lỗi khi tự động cập nhật lịch học: {e}")

'''

# add func before setup_scheduler
content = content.replace('def setup_scheduler(bot: Bot, user_telegram_id: str):', new_job_func + 'def setup_scheduler(bot: Bot, user_telegram_id: str):')

# add job
job_code = "    # Cập nhật lịch học tuần mới vào 22:00 tối Chủ Nhật\n    scheduler.add_job(auto_update_timetable, 'cron', day_of_week='sun', hour=22, minute=0, args=[bot])\n\n    scheduler.start()"
content = content.replace("    scheduler.start()", job_code)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)