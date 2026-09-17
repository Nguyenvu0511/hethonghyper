# -*- coding: utf-8 -*-
import re

with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_command = '''
@router.message(Command("plan_today"))
async def command_plan_today_handler(message: Message) -> None:
    """Tự động lập kế hoạch HÔM NAY dựa trên lịch học hiện tại."""
    msg = await message.answer("Đang phân tích lịch học hôm nay và điểm số để lên kế hoạch động...")
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        if not user_id:
            await msg.edit_text("Cậu chưa đăng ký. Hãy gõ /start.")
            return
            
        from datetime import datetime
        import json
        import os
        from src.ai.strategy_planner import generate_daily_plan
        
        now = datetime.now()
        weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        today_weekday = weekday_names[now.weekday()]
        
        timetable_today = ""
        if os.path.exists("data/last_schedule.json"):
            with open("data/last_schedule.json", "r", encoding="utf-8") as f:
                schedule = json.load(f)
                for item in schedule:
                    if item.get("weekday") == today_weekday:
                        timetable_today += f"- {item.get('raw_info')}\\n"
        
        records_text = ""
        if os.path.exists("scores_output.json"):
            with open("scores_output.json", "r", encoding="utf-8") as f:
                scores = json.load(f)
                for item in scores:
                    if item['diem_chu'] in ['F', 'D', 'D+', 'C-']:
                        records_text += f"- Môn yếu: {item['ten_mon']} (Điểm: {item['diem_chu']})\\n"
        
        import asyncio
        plan = await asyncio.to_thread(generate_daily_plan, records_text, timetable_today, f"{today_weekday} {now.strftime('%d/%m')}")
        
        if plan and plan.get("daily_tasks"):
            db.clear_old_tasks_and_roadmap(user_id)
            for t in plan["daily_tasks"]:
                db.save_task(user_id, "daily", t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), t.get("target_time", "20:00"))
            await msg.edit_text(f"✅ Đã lên lịch trình động cho **{today_weekday}** thành công! Gõ /tasks để xem ngay.")
        else:
            await msg.edit_text("❌ Lỗi sinh lịch trình từ AI.")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await msg.edit_text(f"🚨 Lỗi hệ thống:\\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")
'''

content += "\n" + new_command

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)