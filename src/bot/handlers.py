import os
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
    
    response = "📋 **NHIỆM VỤ HÔM NAY:**\n\n"
    for t in tasks:
        task_id, category, title, description, target_time = t
        if task_id in completed_task_ids:
            response += f"✅ ~~[{category}] {title}~~\n"
        else:
            response += f"🔹 [{category}] {title}\n"
        response += f"   - Yêu cầu: {description}\n"
        if target_time:
            response += f"   - Deadline: {target_time}\n"
        response += "\n"
        
    response += "Nhớ gửi ảnh hoặc tóm tắt vào đây để tớ chấm điểm nhé. Không làm thì Pi-hole sẽ trảm Internet của cậu!"
    await message.answer(response, parse_mode="Markdown")

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
    """Xử lý lệnh /check_news, quét thông báo MyDTU thủ công"""
    msg = await message.answer("🔍 Đang truy cập MyDTU để săn thông báo mới... (sẽ mất khoảng 30s-1p)")
    
    try:
        new_items = await crawl_new_announcements()
        
        if new_items is None:
            await msg.edit_text("❌ Lỗi: Không thể truy cập MyDTU hoặc giải Captcha thất bại. Vui lòng thử lại sau.")
            return
            
        if not new_items:
            await msg.edit_text("✅ Trường hiện tại không có thông báo nào mới (hoặc cậu đã đọc hết rồi)!")
            return
            
        await msg.edit_text(f"🚨 **PHÁT HIỆN {len(new_items)} THÔNG BÁO MỚI** 🚨\nĐang tiến hành phân tích nội dung...")
        
        telegram_id = str(message.from_user.id)
        from src.database.db_manager import db
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        for item in new_items:
            summary = summarize_announcement(item['content'])
            announcement_msg = f"📌 **{item['title']}**\n\n{summary}\n\nChi tiết: [Link MyDTU]({item['url']})"
            
            try:
                await bot.send_message(telegram_id, announcement_msg, parse_mode="Markdown")
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
    scores = await crawl_student_scores()
    
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
    ai_result = generate_academic_advice(records_text, target="Bằng Đỏ")
    
    if isinstance(ai_result, dict):
        advice = ai_result.get("advice", "Lỗi sinh lời khuyên.")
        roadmap = ai_result.get("roadmap", [])
        daily_tasks = ai_result.get("daily_tasks", [])
        
        # Lấy user_id
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if user_id:
            # Xóa task và roadmap cũ
            db.clear_old_academic_tasks(user_id)
            
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
    
    res = "📋 **DANH SÁCH NHIỆM VỤ HÀNG NGÀY CỦA CẬU:**\n\n"
    for t in tasks:
        task_id, category, title, description, target_time = t
        if task_id in completed_task_ids:
            res += f"✅ ~~**ID: {task_id}** | {target_time} - {title}~~\n"
        else:
            res += f"🔹 **ID: {task_id}** | {target_time} - {title}\n"
        res += f"   _{description}_\n"
    
    res += "\n👉 Để đánh dấu hoàn thành, hãy gõ lệnh: `/done <ID_Nhiệm_vụ>`"
    await message.answer(res, parse_mode="Markdown")

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
    await message.answer(f"🎉 Giỏi lắm! Cậu đã hoàn thành nhiệm vụ: **{task[3]}**!", parse_mode="Markdown")

@router.message(F.photo)
async def photo_handler(message: Message, bot: Bot) -> None:
    """Xử lý khi người dùng gửi ảnh (bài tập, điểm danh)"""
    telegram_id = str(message.from_user.id)
    msg = await message.answer("Tớ đang nhìn ảnh của cậu... Chờ chút nhé!")
    
    # Lấy file ảnh
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", f"{photo.file_id}.jpg")
    await bot.download_file(file.file_path, destination=file_path)
    
    # Gửi cho AI chấm điểm (Giả định task_category hiện tại là Toán)
    status, feedback = evaluate_image_report("Bài tập", file_path)
    
    # Xóa ảnh tạm
    if os.path.exists(file_path):
        os.remove(file_path)
        
    await msg.edit_text(f"Kết quả: [{status.upper()}]\n\nNhận xét của AI:\n{feedback}")

import json
@router.message(Command("scores"))
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

@router.message(F.text)
async def text_handler(message: Message) -> None:
    """Xử lý tin nhắn text thông thường (tóm tắt sách, tâm sự)"""
    text = message.text.lower()
    
    if text.startswith("/"):
        return # Bỏ qua các lệnh
        
    msg = await message.answer("Đang phân tích báo cáo của cậu...")
    
    # Chấm điểm bằng AI
    status, feedback = evaluate_text_report("Tóm tắt sách / Báo cáo chung", message.text)
    
    await msg.edit_text(f"Kết quả: [{status.upper()}]\n\nNhận xét:\n{feedback}")

