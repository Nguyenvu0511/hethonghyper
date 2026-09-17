import re

with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace tasks handler
tasks_old = r'''@router.message\(Command\("tasks"\)\)\nasync def command_tasks_handler\(message: Message\) -> None:\n.*?error_msg = traceback.format_exc\(\)\n\s+await message.answer\(f"?? L?i h? th?ng khi ch?y /tasks:\\n<pre>{html.escape\(error_msg\)}</pre>", parse_mode="HTML"\)'''
tasks_new = '''@router.message(Command("tasks"))
async def command_tasks_handler(message: Message) -> None:
    \"\"\"Li?t kê nhi?m v? hàng ngày c?a user\"\"\"
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        if not user_id:
            await message.answer("C?u chua dang ký. Hãy gõ /start.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        if not tasks:
            await message.answer("C?u chua có nhi?m v? nào. Hãy gõ /update_scores d? AI lên l?ch trình nhé!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        
        msg_text = "?? <b>B?NG NHI?M V? HÀNG NGÀY C?A C?U:</b>\\n\\n"
        
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "?" if task_id in completed_task_ids else "??"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> | {target_time} - {html.escape(title)}\\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
        msg_text += "\\nNh? gõ <code>/done &lt;ID_Nhi?m_v?&gt;</code> khi hoàn thành nhé!"
        if msg_text:
            await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        await message.answer(f"?? L?i h? th?ng khi ch?y /tasks:\\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")'''

content = re.sub(tasks_old, tasks_new, content, flags=re.DOTALL)

# Replace status handler
status_old = r'''@router.message\(Command\("status"\)\)\nasync def command_status_handler\(message: Message\) -> None:\n.*?error_msg = traceback.format_exc\(\)\n\s+await message.answer\(f"?? L?i h? th?ng khi ch?y /status:\\n<pre>{html.escape\(error_msg\)}</pre>", parse_mode="HTML"\)'''
status_new = '''@router.message(Command("status"))
async def command_status_handler(message: Message) -> None:
    \"\"\"X? lý l?nh /status, hi?n th? nhi?m v? c?n làm\"\"\"
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if not user_id:
            await message.answer("C?u chua dang ký. Hãy gõ /start tru?c nhé.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        if not tasks:
            await message.answer("Hôm nay c?u chua có nhi?m v? nào du?c giao. Hãy ngh? ngoi ho?c t? ôn t?p nhé!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        
        msg_text = "?? <b>CHI TI?T NHI?M V? HÔM NAY:</b>\\n\\n"
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "?" if task_id in completed_task_ids else "??"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> [{html.escape(category)}] - {target_time}\\n"
            task_info += f"?? {html.escape(title)}\\n"
            task_info += f"?? <i>{html.escape(description)}</i>\\n\\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
        msg_text += "<b>Hãy g?i ?nh ch?p b?ng ch?ng bài t?p vào dây d? T? ch?m di?m nhé!</b>"
        if msg_text:
            await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        await message.answer(f"?? L?i h? th?ng khi ch?y /status:\\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")'''

content = re.sub(status_old, status_new, content, flags=re.DOTALL)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
