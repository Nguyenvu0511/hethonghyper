# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''        import html
        msg_text = "📋 <b>BẢNG NHIỆM VỤ HÀNG NGÀY CỦA CẬU:</b>\\n\\n"
        
        for t in tasks:'''

new_code = '''        import html
        import os
        import json
        from datetime import datetime
        
        now = datetime.now()
        weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        today_weekday = weekday_names[now.weekday()]
        
        timetable_today = ""
        if os.path.exists("data/last_schedule.json"):
            with open("data/last_schedule.json", "r", encoding="utf-8") as f:
                schedule = json.load(f)
                for item in schedule:
                    if item.get("weekday") == today_weekday:
                        # Extract class name and time for cleaner display
                        raw_info = item.get('raw_info', '')
                        # e.g. "Chủ Nhật (13/09) | EE 301 I | Kỹ Thuật Điện Nâng Cao | 07:00-09:00"
                        parts = [p.strip() for p in raw_info.split('|')]
                        if len(parts) >= 4:
                            time_str = parts[-1]
                            subj_str = parts[-2]
                            timetable_today += f"🏫 <b>{time_str}</b> - {subj_str}\\n"
                        else:
                            timetable_today += f"🏫 {raw_info}\\n"
                            
        msg_text = f"📅 <b>LỊCH HỌC TRÊN TRƯỜNG ({today_weekday}):</b>\\n"
        if timetable_today:
            msg_text += timetable_today
        else:
            msg_text += "<i>Hôm nay không có tiết học nào trên trường.</i>\\n"
            
        msg_text += "\\n📋 <b>BẢNG NHIỆM VỤ HÀNG NGÀY CỦA CẬU:</b>\\n"
        
        for t in tasks:'''

content = content.replace(old_code, new_code)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)