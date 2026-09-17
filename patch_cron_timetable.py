# -*- coding: utf-8 -*-
with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''            import html
            msg_text = f"🌅 <b>CHÀO BUỔI SÁNG {html.escape(username)}!</b>\\nĐây là nhiệm vụ học tập hôm nay của cậu:\\n\\n"'''

new_code = '''            import html
            
            timetable_display = ""
            if timetable_today:
                for line in timetable_today.split("\\n"):
                    if line.strip():
                        parts = [p.strip() for p in line.replace("- ", "").split("|")]
                        if len(parts) >= 4:
                            time_str = parts[-1]
                            subj_str = parts[-2]
                            timetable_display += f"🏫 <b>{time_str}</b> - {subj_str}\\n"
                        else:
                            timetable_display += f"🏫 {line}\\n"
            
            msg_text = f"🌅 <b>CHÀO BUỔI SÁNG {html.escape(username)}!</b>\\n"
            if timetable_display:
                msg_text += f"\\n📅 <b>LỊCH HỌC TRÊN TRƯỜNG:</b>\\n{timetable_display}\\n"
            else:
                msg_text += "\\n📅 <b>LỊCH HỌC TRÊN TRƯỜNG:</b>\\n<i>Hôm nay không có tiết học nào trên trường.</i>\\n\\n"
                
            msg_text += "📋 <b>BẢNG NHIỆM VỤ HÀNG NGÀY CỦA CẬU:</b>\\n"
'''

content = content.replace(old_code, new_code)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)