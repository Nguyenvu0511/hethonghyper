# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_handler = '''
@router.message(Command("lichhoc"))
async def command_lichhoc_handler(message: Message) -> None:
    """Xem toàn bộ lịch học trong tuần"""
    import os
    import json
    
    if not os.path.exists("data/last_schedule.json"):
        await message.answer("Chưa có dữ liệu lịch học. Hãy chạy lệnh /update_scores để lấy dữ liệu nhé!")
        return
        
    with open("data/last_schedule.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)
        
    if not schedule:
        await message.answer("Tuần này cậu không có lịch học trên trường.")
        return
        
    msg_text = "📅 <b>LỊCH HỌC TUẦN NÀY CỦA CẬU:</b>\\n\\n"
    
    # Gom nhóm theo thứ
    from collections import defaultdict
    days = defaultdict(list)
    for item in schedule:
        wd = item.get("weekday", "Không rõ")
        raw_info = item.get("raw_info", "")
        parts = [p.strip() for p in raw_info.split('|')]
        if len(parts) >= 4:
            time_str = parts[-1]
            subj_str = parts[-2]
            room_str = parts[-3] if len(parts) >= 5 else ""
            days[wd].append(f"⏰ {time_str} - {subj_str} ({room_str})")
        else:
            days[wd].append(f"📌 {raw_info}")
            
    # Thứ tự in
    order = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    for d in order:
        if d in days:
            msg_text += f"<b>{d}:</b>\\n"
            for t in days[d]:
                msg_text += f"{t}\\n"
            msg_text += "\\n"
            
    await message.answer(msg_text, parse_mode="HTML")
'''

content = content.replace('@router.message(F.text)', new_handler + '\n@router.message(F.text)')

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)