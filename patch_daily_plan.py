# -*- coding: utf-8 -*-
import re

with open('src/ai/strategy_planner.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def generate_daily_plan(records_text, timetable_today, date_str):
    """
    Sinh danh sách nhiệm vụ HÔM NAY dựa trên lịch học thực tế của hôm nay và điểm số.
    """
    prompt = f"""
    Bạn là Bot Kỷ Luật. Nhiệm vụ của bạn là vạch ra lịch trình (daily tasks) cho học sinh trong HÔM NAY ({date_str}).
    
    1. Dưới đây là các môn học yếu kém cần cày cuốc (F, D, C-):
    {records_text}
    
    2. Dưới đây là lịch học TRÊN TRƯỜNG của học sinh trong HÔM NAY:
    {timetable_today if timetable_today else 'Hôm nay học sinh được nghỉ học trên trường, toàn thời gian rảnh rỗi.'}
    
    Yêu cầu:
    Tạo ra 3-5 nhiệm vụ trong ngày HÔM NAY.
    TUYỆT ĐỐI KHÔNG xếp nhiệm vụ trùng với khung giờ học trên trường.
    Hãy chèn xen kẽ: 1 nhiệm vụ thể dục/chạy bộ, 1-2 nhiệm vụ tự học sâu (Deep Work) cho các môn yếu kém.
    
    BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON, KHÔNG CÓ COMMENTS:
    {{
      "daily_tasks": [
         {{"category": "Học thuật / Thể chất", "title": "Tên nhiệm vụ ngắn gọn", "description": "Mô tả chi tiết", "target_time": "Giờ dự kiến (VD: 20:00)"}}
      ]
    }}
    """
    import time
    import json
    for attempt in range(3):
        try:
            response_text = ai_client.generate_text(prompt, is_json=True)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                response_text = response_text[start_idx:end_idx+1]
            return json.loads(response_text, strict=False)
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
                continue
            logger.error(f"Lỗi khi sinh Daily Plan: {e}")
            return {"daily_tasks": []}
'''

content += "\n" + new_func

with open('src/ai/strategy_planner.py', 'w', encoding='utf-8') as f:
    f.write(content)