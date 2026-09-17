# -*- coding: utf-8 -*-
import re

with open('src/ai/strategy_planner.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = r'''Hãy chèn xen kẽ: 1 nhiệm vụ thể dục/chạy bộ, 1-2 nhiệm vụ tự học sâu \(Deep Work\) cho các môn yếu kém\.'''

new_prompt = '''Hãy chèn xen kẽ các nhiệm vụ sau:
    - 1 nhiệm vụ thể chất (thể dục/chạy bộ).
    - Nhiệm vụ "Ôn bài / Làm bài tập" cho CHÍNH NHỮNG MÔN HỌC TRÊN TRƯỜNG ngày hôm nay (dựa vào lịch học hôm nay). Việc học môn trên trường phải được ưu tiên!
    - 1 nhiệm vụ "Tự học sâu (Deep Work)" để cải thiện các môn yếu kém (F, D, C-).'''

content = re.sub(old_prompt, new_prompt, content)

with open('src/ai/strategy_planner.py', 'w', encoding='utf-8') as f:
    f.write(content)