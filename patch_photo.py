with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_str = '@router.message(F.photo)'
end_str = 'async def command_scores_handler(message: Message) -> None:'
start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx) - 24 # to keep the @router.message for scores

old_handler = content[start_idx:end_idx]

new_handler = '''@router.message(F.photo)
async def photo_handler(message: Message, bot: Bot) -> None:
    """Xử lý khi người dùng gửi ảnh (bài tập, điểm danh)"""
    telegram_id = str(message.from_user.id)
    user_id = db.get_user_id(telegram_id)
    msg = await message.answer("Tớ đang nhìn ảnh của cậu... Chờ chút nhé!")
    
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", f"{photo.file_id}.jpg")
    await bot.download_file(file.file_path, destination=file_path)
    
    caption = message.caption or ""
    task_category = "Chưa rõ"
    task_desc = "Cậu hãy dựa vào caption của user hoặc giờ giấc hiện tại để tự phán đoán xem user đang muốn nộp bài gì."
    task_id = None
    
    import re
    # Check if user typed a task ID in caption (e.g. "58", "done 58")
    m = re.search(r'\\b(\\d+)\\b', caption)
    if m:
        t_id = int(m.group(1))
        task = db.get_task_by_id(t_id)
        if task and task[1] == user_id:
            task_id = t_id
            task_category = f"[{task[2]}] {task[3]}"
            task_desc = task[4]
    
    # If no task ID in caption, guess based on time
    import datetime
    if not task_id:
        now = datetime.datetime.now().time()
        if now.hour >= 5 and now.hour < 8:
            task_category = "Điểm danh buổi sáng"
            task_desc = "Chụp ảnh phong cảnh ngoài trời, ban công, đường phố hoặc ánh sáng mặt trời để chứng minh đã dậy khỏi giường."
        elif now.hour >= 16 and now.hour < 19:
            task_category = "Thể dục thể thao"
            task_desc = "Chụp ảnh mồ hôi, cảnh đang chạy bộ, phòng gym, hoặc hoạt động thể thao."
        elif now.hour >= 22 or now.hour < 2:
            task_category = "Skincare / Chuẩn bị ngủ"
            task_desc = "Chụp ảnh bồn rửa mặt, kem dưỡng da, hoặc chỗ ngủ."
            
    # Send to AI
    prompt_context = f"Nhiệm vụ: {task_category}\\nChi tiết nhiệm vụ: {task_desc}\\nCaption của user: {caption}"
    
    import asyncio
    from src.ai.gemini_vision import evaluate_image_report
    status, feedback = await asyncio.to_thread(evaluate_image_report, prompt_context, file_path)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    if status.upper() == "PASSED" and task_id:
        db.log_daily_progress(user_id, task_id, "completed", "photo", "Đã nộp ảnh bằng chứng hợp lệ.", feedback)
        await msg.edit_text(f"✅ **KẾT QUẢ: [PASSED]**\\n\\nTuyệt vời! Nhiệm vụ **{task_category}** đã được đánh dấu HOÀN THÀNH. Tớ đã cộng EXP cho cậu!\\n\\n**Nhận xét của AI:**\\n{feedback}", parse_mode="Markdown")
    else:
        await msg.edit_text(f"Kết quả: [{status.upper()}]\\n\\nNhận xét của AI:\\n{feedback}")
'''

content = content.replace(old_handler, new_handler)

with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")