import os
import html
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from src.database.db_manager import db

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Xử lý lệnh /start, đăng ký user vào cơ sở dữ liệu"""
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    # Đăng ký user
    db.add_user(telegram_id, username)
    
    await message.answer(
        f"Chào {username}! Tớ là Người Thầy Ảo 🤖.\n"
        f"Tớ sẽ giám sát quá trình học tập và rèn luyện Thân - Tâm - Trí của cậu.\n"
        f"Thành công = Ý chí! Cậu đã sẵn sàng chưa?\n\n"
        f"Sử dụng lệnh /status để xem tiến độ hôm nay."
    )

@router.message(Command("status"))
async def command_status_handler(message: Message) -> None:
    """Xử lý lệnh /status, hiển thị nhiệm vụ cần làm"""
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if not user_id:
            await message.answer("Cậu chưa đăng ký. Hãy gõ /start trước nhé.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        
        if not tasks:
            await message.answer("Hôm nay cậu chưa có nhiệm vụ nào được giao. Hãy nghỉ ngơi hoặc tự ôn tập nhé!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        stats = db.get_user_stats(user_id)
        exp, level, streak, last_active = stats if stats else (0, 1, 0, "Chưa rõ")
        
        import html
        msg_text = f"👤 <b>HỒ SƠ CỦA CẬU</b>\n"
        msg_text += f"🏆 Level: <b>{level}</b> | ✨ EXP: <b>{exp}</b>\n"
        msg_text += f"🔥 Chuỗi duy trì: <b>{streak} ngày</b>\n\n"
        msg_text += "📋 <b>CHI TIẾT NHIỆM VỤ HÔM NAY:</b>\n\n"
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "✅" if task_id in completed_task_ids else "▫️"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> [{html.escape(category)}] - {target_time}\n"
            task_info += f"📌 {html.escape(title)}\n"
            task_info += f"📝 <i>{html.escape(description)}</i>\n\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
        msg_text += "<b>Hãy gửi ảnh chụp bằng chứng bài tập vào đây để Tớ chấm điểm nhé!</b>"
        if msg_text:
            await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await message.answer(f"🚨 Lỗi hệ thống khi chạy /status:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")

from src.ai.evaluator import evaluate_text_report, evaluate_image_report
from src.ai.strategy_planner import generate_daily_quiz

@router.message(Command("quiz"))
async def command_quiz_handler(message: Message) -> None:
    """Xử lý lệnh /quiz, sinh bài tập cho môn học hổng kiến thức"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Sử dụng lệnh: /quiz [Tên môn học]\nVí dụ: /quiz Toán Cao Cấp")
        return
        
    subject = args[1]
    msg = await message.answer(f"Đang biên soạn bài tập rèn luyện cho môn {subject}...")
    quiz_content = generate_daily_quiz(subject)
    await msg.edit_text(f"📝 **BÀI TẬP RÈN LUYỆN: {subject}** 📝\n\n{quiz_content}\n\n📸 Hãy giải ra giấy, chụp ảnh lại và gửi vào đây để tớ chấm nhé!", parse_mode="Markdown")

from src.scraper.mydtu_scraper import crawl_student_scores, crawl_new_announcements
from src.ai.strategy_planner import generate_academic_advice, summarize_announcement

@router.message(Command("check_news"))
async def command_check_news_handler(message: Message, bot: Bot) -> None:
    """Xử lý lệnh /check_news, quét 3 thông báo mới nhất từ MyDTU thủ công"""
    msg = await message.answer("🔍 Đang truy cập MyDTU để lấy 3 thông báo mới nhất... (sẽ mất khoảng 30s-1p)")
    
    try:
        new_items = await crawl_new_announcements(fetch_top_3=True)
        
        if new_items is None:
            await msg.edit_text("❌ Lỗi: Không thể truy cập MyDTU hoặc giải Captcha thất bại. Vui lòng thử lại sau.")
            return
            
        if not new_items:
            await msg.edit_text("✅ Trường hiện tại không có thông báo nào!")
            return
            
        await msg.edit_text(f"🚨 **PHÁT HIỆN {len(new_items)} THÔNG BÁO MỚI NHẤT** 🚨\nĐang tiến hành phân tích nội dung...")
        
        telegram_id = str(message.from_user.id)
        from src.database.db_manager import db
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        for item in new_items:
            summary = summarize_announcement(item['content'])
            safe_summary = summary.replace('<', '&lt;').replace('>', '&gt;')
            announcement_msg = f"📌 <b>{item['title']}</b>\n\n{safe_summary}\n\nChi tiết: <a href='{item['url']}'>Link MyDTU</a>"
            
            try:
                await bot.send_message(telegram_id, announcement_msg, parse_mode="HTML")
                # Đánh dấu đã đọc để cronjob không quét lại nữa
                db.mark_announcement_seen(item['id'], item['title'])
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Lỗi gửi thông báo (ID: {item['id']}): {e}")
                
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Lỗi trong check_news: {e}")
        await msg.edit_text("❌ Có lỗi xảy ra trong quá trình quét thông báo.")

@router.message(Command("update_scores"))
async def command_update_scores_handler(message: Message) -> None:
    """Xử lý lệnh /update_scores, cào bảng điểm và phân tích chiến lược Bằng Đỏ"""
    msg = await message.answer("Đang thâm nhập vào MyDTU để lấy bảng điểm mới nhất. Cậu vui lòng chờ khoảng 30 giây...")
    
    # 1. Cào điểm
    from src.scraper.mydtu_scraper import crawl_timetable
    scores = await crawl_student_scores()
    timetable = await crawl_timetable()
    
    if not scores:
        await msg.edit_text("❌ Lỗi: Không thể lấy được bảng điểm. Có thể MyDTU đang bảo trì hoặc có thông báo KHẨN chặn trình duyệt.")
        return
        
    # 2. Xử lý dữ liệu điểm để nạp cho AI
    # Lưu vào database thì làm sau (do cần user_id), tạm thời tóm tắt cho AI phân tích ngay
    records_text = ""
    for item in scores:
        records_text += f"- {item['ten_mon']} (TC: {item['so_tin_chi']}): Điểm tổng kết {item['diem_tong_ket']} -> Điểm chữ: {item['diem_chu']}\n"
        
    await msg.edit_text("✅ Đã lấy được bảng điểm! Đang gửi cho AI phân tích lộ trình Bằng Đỏ...")
    
    # 3. Xin lời khuyên AI (Bây giờ trả về JSON)
    import asyncio
    ai_result = await asyncio.to_thread(generate_academic_advice, records_text, target="Bằng Đỏ")
    
    if isinstance(ai_result, dict):
        advice = ai_result.get("advice", "Lỗi sinh lời khuyên.")
        roadmap = ai_result.get("roadmap", [])
        daily_tasks = ai_result.get("daily_tasks", [])
        
        # Lấy user_id
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if user_id:
            # Xóa task và roadmap cũ
            db.clear_old_tasks_and_roadmap(user_id)
            
            # Lưu roadmap mới
            for rm in roadmap:
                db.insert_roadmap(user_id, rm.get("subject_name", ""), rm.get("target_level", ""), rm.get("end_date", ""))
                
            # Lưu daily tasks mới
            for tk in daily_tasks:
                db.add_task(user_id, tk.get("category", "Học thuật"), tk.get("title", ""), tk.get("description", ""), "daily", tk.get("target_time", "20:00"))
    else:
        advice = str(ai_result)
    
    # Telegram Markdown rất dễ lỗi nếu AI sinh ra unclosed tags, nên chuyển sang text thường
    safe_advice = advice.replace("**", "").replace("*", "-").replace("_", "")
    
    # Telegram giới hạn 4096 ký tự/tin nhắn
    max_length = 4000
    if len(safe_advice) > max_length:
        parts = [safe_advice[i:i+max_length] for i in range(0, len(safe_advice), max_length)]
        await msg.edit_text(f"📊 BÁO CÁO PHÂN TÍCH ĐIỂM SỐ 📊\n\n{parts[0]}")
        for part in parts[1:]:
            await message.answer(part)
    else:
        await msg.edit_text(f"📊 BÁO CÁO PHÂN TÍCH ĐIỂM SỐ 📊\n\n{safe_advice}")
        
    await message.answer("✅ Đã lưu Lộ trình học và Nhiệm vụ hàng ngày vào cơ sở dữ liệu! Gõ /tasks để xem danh sách nhiệm vụ của cậu.")


@router.message(Command("tasks"))
async def command_tasks_handler(message: Message) -> None:
    """Liệt kê nhiệm vụ hàng ngày của user"""
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        if not user_id:
            await message.answer("Cậu chưa đăng ký. Hãy gõ /start.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        if not tasks:
            await message.answer("Cậu chưa có nhiệm vụ nào. Hãy gõ /update_scores để AI lên lịch trình nhé!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        
        import html
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
                    wd = item.get("weekday")
                    if not wd and "(" in item.get("raw_info", ""):
                        wd = item.get("raw_info").split("(")[0].strip()
                    if wd == today_weekday:
                        # Extract class name and time for cleaner display
                        raw_info = item.get('raw_info', '')
                        # e.g. "Chủ Nhật (13/09) | EE 301 I | Kỹ Thuật Điện Nâng Cao | 07:00-09:00"
                        parts = [p.strip() for p in raw_info.split('|')]
                        if len(parts) >= 4:
                            time_str = parts[-1]
                            subj_str = parts[-2]
                            timetable_today += f"🏫 <b>{time_str}</b> - {subj_str}\n"
                        else:
                            timetable_today += f"🏫 {raw_info}\n"
                            
        msg_text = f"📅 <b>LỊCH HỌC TRÊN TRƯỜNG ({today_weekday}):</b>\n"
        if timetable_today:
            msg_text += timetable_today
        else:
            msg_text += "<i>Hôm nay không có tiết học nào trên trường.</i>\n"
            
        msg_text += "\n📋 <b>BẢNG NHIỆM VỤ HÀNG NGÀY CỦA CẬU:</b>\n"
        
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "✅" if task_id in completed_task_ids else "▫️"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> | {target_time} - {html.escape(title)}\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
        msg_text += "\nNhớ gõ <code>/done &lt;ID_Nhiệm_vụ&gt;</code> khi hoàn thành nhé!"
        if msg_text:
            await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await message.answer(f"🚨 Lỗi hệ thống khi chạy /tasks:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")

@router.message(Command("done"))
async def command_done_handler(message: Message) -> None:
    """Đánh dấu hoàn thành nhiệm vụ"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Sử dụng lệnh: `/done <ID>`\nVí dụ: `/done 1`", parse_mode="Markdown")
        return
        
    try:
        task_id = int(args[1])
    except ValueError:
        await message.answer("ID nhiệm vụ phải là một con số!")
        return
        
    telegram_id = str(message.from_user.id)
    user_id = db.get_user_id(telegram_id)
    
    # Lấy thông tin task để chắc chắn nó tồn tại
    task = db.get_task_by_id(task_id)
    if not task or task[1] != user_id:
        await message.answer("Không tìm thấy nhiệm vụ này của cậu!")
        return
        
    db.log_daily_progress(user_id, task_id, "completed", "text", "Điểm danh qua lệnh /done", "Tốt")
    db.check_and_update_streak(user_id, is_active=True)
    leveled_up, new_level = db.add_exp(user_id, 10)
    
    reply_msg = f"🎉 Giỏi lắm! Cậu đã hoàn thành nhiệm vụ: **{task[3]}**!\n✨ Nhận được +10 EXP."
    if leveled_up:
        reply_msg += f"\n🏆 CHÚC MỪNG! Cậu đã thăng cấp lên Level {new_level}!"
        
    await message.answer(reply_msg, parse_mode="Markdown")

@router.message(F.photo)
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
    m = re.search(r'\b(\d+)\b', caption)
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
    prompt_context = f"Nhiệm vụ: {task_category}\nChi tiết nhiệm vụ: {task_desc}\nCaption của user: {caption}"
    
    import asyncio
    from src.ai.evaluator import evaluate_image_report
    status, feedback = await asyncio.to_thread(evaluate_image_report, prompt_context, file_path)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    if status.upper() == "PASSED" and task_id:
        db.log_daily_progress(user_id, task_id, "completed", "photo", "Đã nộp ảnh bằng chứng hợp lệ.", feedback)
        db.check_and_update_streak(user_id, is_active=True)
        leveled_up, new_level = db.add_exp(user_id, 20) # Ảnh được +20 EXP
        
        reply_msg = f"✅ **KẾT QUẢ: [PASSED]**\n\nTuyệt vời! Nhiệm vụ **{task_category}** đã được đánh dấu HOÀN THÀNH.\n✨ Nhận được +20 EXP!\n"
        if leveled_up:
            reply_msg += f"🏆 CHÚC MỪNG! Cậu đã thăng cấp lên Level {new_level}!\n"
        reply_msg += f"\n**Nhận xét của AI:**\n{feedback}"
        
        await msg.edit_text(reply_msg, parse_mode="Markdown")
    else:
        await msg.edit_text(f"Kết quả: [{status.upper()}]\n\nNhận xét của AI:\n{feedback}")
sage(Command("scores"))
async def command_scores_handler(message: Message) -> None:
    """Xử lý lệnh /scores, xem lại bảng điểm đã lưu mà không cần cào lại"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scores_output.json")
    
    if not os.path.exists(file_path):
        await message.answer("❌ Chưa có dữ liệu bảng điểm. Cậu hãy chạy lệnh /update_scores ít nhất 1 lần để hệ thống cào điểm về nhé!")
        return
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            scores = json.load(f)
            
        if not scores:
            await message.answer("Bảng điểm hiện tại đang trống.")
            return
            
        res = "🎓 <b>BẢNG ĐIỂM CỦA CẬU (BẢN LƯU GẦN NHẤT)</b> 🎓\n\n"
        
        # Nhóm theo trạng thái điểm
        passed = []
        failed = []
        studying = []
        
        import html
        for item in scores:
            diem_chu = item.get("diem_chu", "Chưa có")
            ten_mon = html.escape(item['ten_mon'])
            
            # Cảnh báo môn học điểm thấp (kéo tụt GPA)
            if diem_chu in ["D", "D+", "C-"]:
                text = f"🔴 <b>{ten_mon} ({item['so_tin_chi']} TC): {item['diem_tong_ket']} ({diem_chu})</b> <i>(Cảnh báo kéo tụt GPA, cần cân nhắc học cải thiện!)</i>"
                passed.append(text)
            else:
                text = f"▪️ {ten_mon} ({item['so_tin_chi']} TC): {item['diem_tong_ket']} ({diem_chu})"
                
                if diem_chu == "F":
                    failed.append(text)
                elif diem_chu == "Chưa có":
                    studying.append(text)
                else:
                    passed.append(text)
                
        if failed:
            res += "❌ <b>BÁO ĐỘNG (RỚT MÔN):</b>\n" + "\n".join(failed) + "\n\n"
        if studying:
            res += "⏳ <b>ĐANG HỌC KỲ NÀY:</b>\n" + "\n".join(studying) + "\n\n"
        if passed:
            res += "✅ <b>ĐÃ QUA MÔN:</b>\n" + "\n".join(passed) + "\n\n"
            
        res += "<i>💡 Ghi chú: Để cập nhật điểm số mới nhất từ trường, hãy dùng lệnh /update_scores</i>"
        
        # Gửi theo từng phần nếu quá dài
        max_length = 4000
        if len(res) > max_length:
            parts = [res[i:i+max_length] for i in range(0, len(res), max_length)]
            for part in parts:
                await message.answer(part, parse_mode="HTML")
        else:
            await message.answer(res, parse_mode="HTML")
            
    except Exception as e:
        await message.answer(f"❌ Lỗi khi đọc file bảng điểm: {e}")


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
                    wd = item.get("weekday")
                    if not wd and "(" in item.get("raw_info", ""):
                        wd = item.get("raw_info").split("(")[0].strip()
                    if wd == today_weekday:
                        timetable_today += f"- {item.get('raw_info')}\n"
        
        records_text = ""
        if os.path.exists("scores_output.json"):
            with open("scores_output.json", "r", encoding="utf-8") as f:
                scores = json.load(f)
                for item in scores:
                    if item['diem_chu'] in ['F', 'D', 'D+', 'C-']:
                        records_text += f"- Môn yếu: {item['ten_mon']} (Điểm: {item['diem_chu']})\n"
        
        import asyncio
        plan = await asyncio.to_thread(generate_daily_plan, records_text, timetable_today, f"{today_weekday} {now.strftime('%d/%m')}")
        
        if plan and plan.get("daily_tasks"):
            db.clear_old_tasks_and_roadmap(user_id)
            for t in plan["daily_tasks"]:
                db.add_task(user_id, t.get("category", "Học thuật"), t.get("title", ""), t.get("description", ""), "daily", t.get("target_time", "20:00"))
            await msg.edit_text(f"✅ Đã lên lịch trình động cho **{today_weekday}** thành công! Gõ /tasks để xem ngay.")
        else:
            err = plan.get('error', 'Không có error') if plan else 'Plan is None'
            raw = plan.get('raw_text', '') if plan else ''
            import html
            await msg.edit_text(f"❌ Lỗi sinh lịch trình từ AI.\nLỗi: {html.escape(err)}\nRaw: {html.escape(raw)[:1000]}", parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await msg.edit_text(f"🚨 Lỗi hệ thống:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")


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
        
    msg_text = "📅 <b>LỊCH HỌC TUẦN NÀY CỦA CẬU:</b>\n\n"
    
    # Gom nhóm theo thứ
    from collections import defaultdict
    days = defaultdict(list)
    for item in schedule:
        wd = item.get("weekday")
        if not wd and "(" in item.get("raw_info", ""):
            wd = item.get("raw_info").split("(")[0].strip()
        elif not wd:
            wd = "Không rõ"
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
            msg_text += f"<b>{d}:</b>\n"
            for t in days[d]:
                msg_text += f"{t}\n"
            msg_text += "\n"
            
    await message.answer(msg_text, parse_mode="HTML")

@router.message(F.text)
async def text_handler(message: Message) -> None:
    """Xử lý tin nhắn text thông thường (tóm tắt sách, tâm sự)"""
    text = message.text.lower()
    
    if text.startswith("/"):
        return # Bỏ qua các lệnh
        
    msg = await message.answer("Đang phân tích báo cáo của cậu...")
    
    # Chấm điểm bằng AI
    import asyncio
    status, feedback = await asyncio.to_thread(evaluate_text_report, "Tóm tắt sách / Báo cáo chung", message.text)
    
    await msg.edit_text(f"Kết quả: [{status.upper()}]\n\nNhận xét:\n{feedback}")



