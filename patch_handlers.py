# -*- coding: utf-8 -*-
import re

with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_handler = r'''scores = await crawl_student_scores\(\)
    
    if not scores:'''

new_handler = '''from src.scraper.mydtu_scraper import crawl_timetable
    scores = await crawl_student_scores()
    timetable = await crawl_timetable()
    
    if not scores:'''

content = re.sub(old_handler, new_handler, content)

old_records = r'''records_text = ""
    for item in scores:
        records_text \+= f"- {item\['ten_mon'\]} \(TC: {item\['so_tin_chi'\]}\): Điểm tổng kết {item\['diem_tong_ket'\]} -> Điểm chữ: {item\['diem_chu'\]}\\n"
        
    await msg.edit_text\("✅ Đã lấy được bảng điểm! Đang gửi cho AI phân tích lộ trình Bảng Đỏ..."\)'''

new_records = '''records_text = ""
    for item in scores:
        records_text += f"- {item['ten_mon']} (TC: {item['so_tin_chi']}): Điểm tổng kết {item['diem_tong_ket']} -> Điểm chữ: {item['diem_chu']}\\n"
    
    records_text += "\\n\\n[LỊCH HỌC TRÊN TRƯỜNG TUẦN NÀY]:\\n"
    if timetable:
        for t in timetable:
            records_text += f"- {t.get('raw_info', '')}\\n"
    else:
        records_text += "Không có lịch học hoặc không lấy được lịch.\\n"
        
    await msg.edit_text("✅ Đã lấy xong bảng điểm và lịch học! Đang gửi cho AI phân tích lộ trình Bảng Đỏ...")'''

content = re.sub(old_records, new_records, content)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)