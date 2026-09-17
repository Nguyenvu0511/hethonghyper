# -*- coding: utf-8 -*-
import re

with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_morning = r'''async def morning_tasks_reminder\(bot: Bot\):\n    """Gửi danh sách nhiệm vụ lúc 6:00 sáng cho tất cả user"""\n    users = db\.get_all_users\(\)\n    for u in users:\n        user_id, telegram_id, username = u\n        tasks = db\.get_daily_tasks\(user_id\)'''

new_morning = '''async def morning_tasks_reminder(bot: Bot):
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
                            timetable_today += f"- {item.get('raw_info')}\\n"
            
            # Đọc điểm
            records_text = ""
            if os.path.exists("scores_output.json"):
                with open("scores_output.json", "r", encoding="utf-8") as f:
                    scores = json.load(f)
                    for item in scores:
                        if item['diem_chu'] in ['F', 'D', 'D+', 'C-']:
                            records_text += f"- Môn yếu: {item['ten_mon']} (Điểm: {item['diem_chu']})\\n"
            
            if records_text:
                plan = generate_daily_plan(records_text, timetable_today, f"{today_weekday} {now.strftime('%d/%m')}")
                if plan and plan.get("daily_tasks"):
                    # Xóa tasks cũ và lưu tasks mới
                    db.clear_old_tasks_and_roadmap(user_id)
                    for t in plan["daily_tasks"]:
                        db.save_task(user_id, "daily", t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), t.get("target_time", "20:00"))
        except Exception as e:
            logger.error(f"Lỗi khi tự động lập kế hoạch sáng: {e}")
            
        tasks = db.get_daily_tasks(user_id)'''

content = re.sub(old_morning, new_morning, content)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)