# -*- coding: utf-8 -*-
import re

with open('src/ai/strategy_planner.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = r'''5\. Trích xuất danh sách các môn học có thể cần đưa vào LỘ TRÌNH học lại/cải thiện\.
    6\. Đề xuất các NHIỆM VỤ HÀNG NGÀY \(daily tasks\) cụ thể\.'''

new_prompt = '''5. Trích xuất danh sách các môn học có thể cần đưa vào LỘ TRÌNH học lại/cải thiện.
    6. Đề xuất các NHIỆM VỤ HÀNG NGÀY (daily tasks) cụ thể. LƯU Ý QUAN TRỌNG: Hãy xem kỹ [LỊCH HỌC TRÊN TRƯỜNG TUẦN NÀY] ở trên. Khi lên lịch target_time cho các nhiệm vụ, TUYỆT ĐỐI KHÔNG được xếp lịch nhiệm vụ trùng với giờ đang học trên lớp! Hãy xếp vào các khung giờ trống.'''

content = re.sub(old_prompt, new_prompt, content)

with open('src/ai/strategy_planner.py', 'w', encoding='utf-8') as f:
    f.write(content)