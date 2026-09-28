import os
import html
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from src.database.db_manager import db

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Xá»­ lÃ½ lá»‡nh /start, Ä‘Äƒng kÃ½ user vÃ o cÆ¡ sá»Ÿ dá»¯ liá»‡u"""
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    # ÄÄƒng kÃ½ user
    db.add_user(telegram_id, username)
    
    await message.answer(
        f"ChÃ o {username}! Tá»› lÃ  NgÆ°á»i Tháº§y áº¢o ðŸ¤–.\n"
        f"Tá»› sáº½ giÃ¡m sÃ¡t quÃ¡ trÃ¬nh há»c táº­p vÃ  rÃ¨n luyá»‡n ThÃ¢n - TÃ¢m - TrÃ­ cá»§a cáº­u.\n"
        f"ThÃ nh cÃ´ng = Ã chÃ­! Cáº­u Ä‘Ã£ sáºµn sÃ ng chÆ°a?\n\n"
        f"Sá»­ dá»¥ng lá»‡nh /status Ä‘á»ƒ xem tiáº¿n Ä‘á»™ hÃ´m nay."
    )

@router.message(Command("status"))
async def command_status_handler(message: Message) -> None:
    """Xá»­ lÃ½ lá»‡nh /status, hiá»ƒn thá»‹ nhiá»‡m vá»¥ cáº§n lÃ m"""
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if not user_id:
            await message.answer("Cáº­u chÆ°a Ä‘Äƒng kÃ½. HÃ£y gÃµ /start trÆ°á»›c nhÃ©.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        
        if not tasks:
            await message.answer("HÃ´m nay cáº­u chÆ°a cÃ³ nhiá»‡m vá»¥ nÃ o Ä‘Æ°á»£c giao. HÃ£y nghá»‰ ngÆ¡i hoáº·c tá»± Ã´n táº­p nhÃ©!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        stats = db.get_user_stats(user_id)
        exp, level, streak, last_active = stats if stats else (0, 1, 0, "ChÆ°a rÃµ")
        
        import html
        msg_text = f"ðŸ‘¤ <b>Há»’ SÆ  Cá»¦A Cáº¬U</b>\n"
        msg_text += f"ðŸ† Level: <b>{level}</b> | âœ¨ EXP: <b>{exp}</b>\n"
        msg_text += f"ðŸ”¥ Chuá»—i duy trÃ¬: <b>{streak} ngÃ y</b>\n\n"
        msg_text += "ðŸ“‹ <b>CHI TIáº¾T NHIá»†M Vá»¤ HÃ”M NAY:</b>\n\n"
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = []
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "âœ…" if task_id in completed_task_ids else "â–«ï¸"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> [{html.escape(category)}] - {target_time}\n"
            task_info += f"ðŸ“Œ {html.escape(title)}\n"
            task_info += f"ðŸ“ <i>{html.escape(description)}</i>\n\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
            # Náº¿u chÆ°a xong vÃ  KHÃ”NG yÃªu cáº§u chá»¥p áº£nh, hiá»ƒn thá»‹ nÃºt Báº¥m
            if task_id not in completed_task_ids:
                if "XÃ¡c thá»±c chá»‘ng gian láº­n" not in (description or ""):
                    keyboard.append([InlineKeyboardButton(text=f"âœ… Xong: {title[:20]}", callback_data=f"done_{task_id}")])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None

        msg_text += "<b>HÃ£y gá»­i áº£nh chá»¥p báº±ng chá»©ng bÃ i táº­p vÃ o Ä‘Ã¢y (kÃ¨m ID á»Ÿ pháº§n caption) Ä‘á»ƒ Tá»› cháº¥m Ä‘iá»ƒm nhÃ©!</b>"
        if msg_text:
            if markup:
                await message.answer(msg_text, parse_mode="HTML", reply_markup=markup)
            else:
                await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await message.answer(f"ðŸš¨ Lá»—i há»‡ thá»‘ng khi cháº¡y /status:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")

from src.ai.evaluator import evaluate_text_report, evaluate_image_report
from src.ai.strategy_planner import generate_daily_quiz

@router.message(Command("quiz"))
async def command_quiz_handler(message: Message) -> None:
    """Xá»­ lÃ½ lá»‡nh /quiz, sinh bÃ i táº­p cho mÃ´n há»c há»•ng kiáº¿n thá»©c"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Sá»­ dá»¥ng lá»‡nh: /quiz [TÃªn mÃ´n há»c]\nVÃ­ dá»¥: /quiz ToÃ¡n Cao Cáº¥p")
        return
        
    subject = args[1]
    msg = await message.answer(f"Äang biÃªn soáº¡n bÃ i táº­p rÃ¨n luyá»‡n cho mÃ´n {subject}...")
    quiz_content = generate_daily_quiz(subject)
    await msg.edit_text(f"ðŸ“ **BÃ€I Táº¬P RÃˆN LUYá»†N: {subject}** ðŸ“\n\n{quiz_content}\n\nðŸ“¸ HÃ£y giáº£i ra giáº¥y, chá»¥p áº£nh láº¡i vÃ  gá»­i vÃ o Ä‘Ã¢y Ä‘á»ƒ tá»› cháº¥m nhÃ©!", parse_mode="Markdown")

from src.scraper.mydtu_scraper import crawl_student_scores, crawl_new_announcements
from src.ai.strategy_planner import generate_academic_advice, summarize_announcement

@router.message(Command("check_news"))
async def command_check_news_handler(message: Message, bot: Bot) -> None:
    """Xá»­ lÃ½ lá»‡nh /check_news, quÃ©t 3 thÃ´ng bÃ¡o má»›i nháº¥t tá»« MyDTU thá»§ cÃ´ng"""
    msg = await message.answer("ðŸ” Äang truy cáº­p MyDTU Ä‘á»ƒ láº¥y 3 thÃ´ng bÃ¡o má»›i nháº¥t... (sáº½ máº¥t khoáº£ng 30s-1p)")
    
    try:
        new_items = await crawl_new_announcements(fetch_top_3=True)
        
        if new_items is None:
            await msg.edit_text("âŒ Lá»—i: KhÃ´ng thá»ƒ truy cáº­p MyDTU hoáº·c giáº£i Captcha tháº¥t báº¡i. Vui lÃ²ng thá»­ láº¡i sau.")
            return
            
        if not new_items:
            await msg.edit_text("âœ… TrÆ°á»ng hiá»‡n táº¡i khÃ´ng cÃ³ thÃ´ng bÃ¡o nÃ o!")
            return
            
        await msg.edit_text(f"ðŸš¨ **PHÃT HIá»†N {len(new_items)} THÃ”NG BÃO Má»šI NHáº¤T** ðŸš¨\nÄang tiáº¿n hÃ nh phÃ¢n tÃ­ch ná»™i dung...")
        
        telegram_id = str(message.from_user.id)
        from src.database.db_manager import db
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        for item in new_items:
            summary = summarize_announcement(item['content'])
            safe_summary = summary.replace('<', '&lt;').replace('>', '&gt;')
            announcement_msg = f"ðŸ“Œ <b>{item['title']}</b>\n\n{safe_summary}\n\nChi tiáº¿t: <a href='{item['url']}'>Link MyDTU</a>"
            
            try:
                await bot.send_message(telegram_id, announcement_msg, parse_mode="HTML")
                # ÄÃ¡nh dáº¥u Ä‘Ã£ Ä‘á»c Ä‘á»ƒ cronjob khÃ´ng quÃ©t láº¡i ná»¯a
                db.mark_announcement_seen(item['id'], item['title'])
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Lá»—i gá»­i thÃ´ng bÃ¡o (ID: {item['id']}): {e}")
                
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Lá»—i trong check_news: {e}")
        await msg.edit_text("âŒ CÃ³ lá»—i xáº£y ra trong quÃ¡ trÃ¬nh quÃ©t thÃ´ng bÃ¡o.")

@router.message(Command("update_scores"))
async def command_update_scores_handler(message: Message) -> None:
    """Xá»­ lÃ½ lá»‡nh /update_scores, cÃ o báº£ng Ä‘iá»ƒm vÃ  phÃ¢n tÃ­ch chiáº¿n lÆ°á»£c Báº±ng Äá»"""
    msg = await message.answer("Äang thÃ¢m nháº­p vÃ o MyDTU Ä‘á»ƒ láº¥y báº£ng Ä‘iá»ƒm má»›i nháº¥t. Cáº­u vui lÃ²ng chá» khoáº£ng 30 giÃ¢y...")
    
    # 1. CÃ o Ä‘iá»ƒm
    from src.scraper.mydtu_scraper import crawl_timetable
    scores = await crawl_student_scores()
    timetable = await crawl_timetable()
    
    if not scores:
        await msg.edit_text("âŒ Lá»—i: KhÃ´ng thá»ƒ láº¥y Ä‘Æ°á»£c báº£ng Ä‘iá»ƒm. CÃ³ thá»ƒ MyDTU Ä‘ang báº£o trÃ¬ hoáº·c cÃ³ thÃ´ng bÃ¡o KHáº¨N cháº·n trÃ¬nh duyá»‡t.")
        return
        
    # 2. Xá»­ lÃ½ dá»¯ liá»‡u Ä‘iá»ƒm Ä‘á»ƒ náº¡p cho AI
    # LÆ°u vÃ o database thÃ¬ lÃ m sau (do cáº§n user_id), táº¡m thá»i tÃ³m táº¯t cho AI phÃ¢n tÃ­ch ngay
    records_text = ""
    for item in scores:
        records_text += f"- {item['ten_mon']} (TC: {item['so_tin_chi']}): Äiá»ƒm tá»•ng káº¿t {item['diem_tong_ket']} -> Äiá»ƒm chá»¯: {item['diem_chu']}\n"
        
    await msg.edit_text("âœ… ÄÃ£ láº¥y Ä‘Æ°á»£c báº£ng Ä‘iá»ƒm! Äang gá»­i cho AI phÃ¢n tÃ­ch lá»™ trÃ¬nh Báº±ng Äá»...")
    
    # 3. Xin lá»i khuyÃªn AI (BÃ¢y giá» tráº£ vá» JSON)
    import asyncio
    ai_result = await asyncio.to_thread(generate_academic_advice, records_text, target="Báº±ng Äá»")
    
    if isinstance(ai_result, dict):
        advice = ai_result.get("advice", "Lá»—i sinh lá»i khuyÃªn.")
        roadmap = ai_result.get("roadmap", [])
        daily_tasks = ai_result.get("daily_tasks", [])
        
        # Láº¥y user_id
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        
        if user_id:
            # XÃ³a task vÃ  roadmap cÅ©
            db.clear_old_tasks_and_roadmap(user_id)
            
            # LÆ°u roadmap má»›i
            for rm in roadmap:
                db.insert_roadmap(user_id, rm.get("subject_name", ""), rm.get("target_level", ""), rm.get("end_date", ""))
                
            # LÆ°u daily tasks má»›i
            for tk in daily_tasks:
                db.add_task(user_id, tk.get("category", "Há»c thuáº­t"), tk.get("title", ""), tk.get("description", ""), "daily", tk.get("target_time", "20:00"))
    else:
        advice = str(ai_result)
    
    # Telegram Markdown ráº¥t dá»… lá»—i náº¿u AI sinh ra unclosed tags, nÃªn chuyá»ƒn sang text thÆ°á»ng
    safe_advice = advice.replace("**", "").replace("*", "-").replace("_", "")
    
    # Telegram giá»›i háº¡n 4096 kÃ½ tá»±/tin nháº¯n
    max_length = 4000
    if len(safe_advice) > max_length:
        parts = [safe_advice[i:i+max_length] for i in range(0, len(safe_advice), max_length)]
        await msg.edit_text(f"ðŸ“Š BÃO CÃO PHÃ‚N TÃCH ÄIá»‚M Sá» ðŸ“Š\n\n{parts[0]}")
        for part in parts[1:]:
            await message.answer(part)
    else:
        await msg.edit_text(f"ðŸ“Š BÃO CÃO PHÃ‚N TÃCH ÄIá»‚M Sá» ðŸ“Š\n\n{safe_advice}")
        
    await message.answer("âœ… ÄÃ£ lÆ°u Lá»™ trÃ¬nh há»c vÃ  Nhiá»‡m vá»¥ hÃ ng ngÃ y vÃ o cÆ¡ sá»Ÿ dá»¯ liá»‡u! GÃµ /tasks Ä‘á»ƒ xem danh sÃ¡ch nhiá»‡m vá»¥ cá»§a cáº­u.")


@router.message(Command("tasks"))
async def command_tasks_handler(message: Message) -> None:
    """Liá»‡t kÃª nhiá»‡m vá»¥ hÃ ng ngÃ y cá»§a user"""
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        if not user_id:
            await message.answer("Cáº­u chÆ°a Ä‘Äƒng kÃ½. HÃ£y gÃµ /start.")
            return
            
        tasks = db.get_daily_tasks(user_id)
        if not tasks:
            await message.answer("Cáº­u chÆ°a cÃ³ nhiá»‡m vá»¥ nÃ o. HÃ£y gÃµ /update_scores Ä‘á»ƒ AI lÃªn lá»‹ch trÃ¬nh nhÃ©!")
            return
            
        completed_task_ids = db.get_completed_tasks_today(user_id)
        
        import html
        import os
        import json
        from datetime import datetime
        
        now = datetime.now()
        weekday_names = ["Thá»© Hai", "Thá»© Ba", "Thá»© TÆ°", "Thá»© NÄƒm", "Thá»© SÃ¡u", "Thá»© Báº£y", "Chá»§ Nháº­t"]
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
                        # e.g. "Chá»§ Nháº­t (13/09) | EE 301 I | Ká»¹ Thuáº­t Äiá»‡n NÃ¢ng Cao | 07:00-09:00"
                        parts = [p.strip() for p in raw_info.split('|')]
                        if len(parts) >= 4:
                            time_str = parts[-1]
                            subj_str = parts[-2]
                            timetable_today += f"ðŸ« <b>{time_str}</b> - {subj_str}\n"
                        else:
                            timetable_today += f"ðŸ« {raw_info}\n"
                            
        msg_text = f"ðŸ“… <b>Lá»ŠCH Há»ŒC TRÃŠN TRÆ¯á»œNG ({today_weekday}):</b>\n"
        if timetable_today:
            msg_text += timetable_today
        else:
            msg_text += "<i>HÃ´m nay khÃ´ng cÃ³ tiáº¿t há»c nÃ o trÃªn trÆ°á»ng.</i>\n"
            
        msg_text += "\nðŸ“‹ <b>Báº¢NG NHIá»†M Vá»¤ HÃ€NG NGÃ€Y Cá»¦A Cáº¬U:</b>\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = []
        for t in tasks:
            task_id, category, title, description, target_time = t
            status_icon = "âœ…" if task_id in completed_task_ids else "â–«ï¸"
            
            task_info = f"{status_icon} <b>ID {task_id}</b> | {target_time} - {html.escape(title)}\n"
            
            if len(msg_text) + len(task_info) > 3500:
                await message.answer(msg_text, parse_mode="HTML")
                msg_text = ""
                
            msg_text += task_info
            
            if task_id not in completed_task_ids:
                if "XÃ¡c thá»±c chá»‘ng gian láº­n" not in (description or ""):
                    keyboard.append([InlineKeyboardButton(text=f"âœ… Xong: {title[:20]}", callback_data=f"done_{task_id}")])
            
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
            
        msg_text += "\nNhá»› gÃµ <code>/done &lt;ID_Nhiá»‡m_vá»¥&gt;</code> hoáº·c báº¥m nÃºt á»Ÿ dÆ°á»›i (vá»›i cÃ¡c task khÃ´ng cáº§n áº£nh) khi hoÃ n thÃ nh nhÃ©!"
        if msg_text:
            if markup:
                await message.answer(msg_text, parse_mode="HTML", reply_markup=markup)
            else:
                await message.answer(msg_text, parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await message.answer(f"ðŸš¨ Lá»—i há»‡ thá»‘ng khi cháº¡y /tasks:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")

@router.message(Command("done"))
async def command_done_handler(message: Message, bot: Bot) -> None:
    """ÄÃ¡nh dáº¥u hoÃ n thÃ nh nhiá»‡m vá»¥"""
    if message.photo:
        await photo_handler(message, bot)
        return
        
    text = message.text or message.caption
    if not text:
        return
    args = text.split()
    if len(args) < 2:
        await message.answer("Sá»­ dá»¥ng lá»‡nh: `/done <ID>`\nVÃ­ dá»¥: `/done 1`", parse_mode="Markdown")
        return
        
    try:
        task_id = int(args[1])
    except ValueError:
        await message.answer("ID nhiá»‡m vá»¥ pháº£i lÃ  má»™t con sá»‘!")
        return
        
    telegram_id = str(message.from_user.id)
    user_id = db.get_user_id(telegram_id)
    
    # Láº¥y thÃ´ng tin task Ä‘á»ƒ cháº¯c cháº¯n nÃ³ tá»“n táº¡i
    task = db.get_task_by_id(task_id)
    if not task or task[1] != user_id:
        await message.answer("KhÃ´ng tÃ¬m tháº¥y nhiá»‡m vá»¥ nÃ y cá»§a cáº­u!")
        return
        
    description = task[4] or ""
    if "XÃ¡c thá»±c chá»‘ng gian láº­n" in description:
        await message.answer("âš ï¸ Nhiá»‡m vá»¥ nÃ y yÃªu cáº§u **XÃ¡c thá»±c báº±ng hÃ¬nh áº£nh**! Cáº­u khÃ´ng thá»ƒ dÃ¹ng lá»‡nh `/done`. HÃ£y chá»¥p má»™t bá»©c áº£nh thá»a mÃ£n yÃªu cáº§u vÃ  gá»­i cho tá»› (Nhá»› ghi ID nhiá»‡m vá»¥ vÃ o pháº§n chÃº thÃ­ch áº£nh nhÃ©).", parse_mode="Markdown")
        return
        
    db.log_daily_progress(user_id, task_id, "completed", "text", "Äiá»ƒm danh qua lá»‡nh /done", "Tá»‘t")
    db.check_and_update_streak(user_id, is_active=True)
    leveled_up, new_level = db.add_exp(user_id, 10)
    
    reply_msg = f"ðŸŽ‰ Giá»i láº¯m! Cáº­u Ä‘Ã£ hoÃ n thÃ nh nhiá»‡m vá»¥: **{task[3]}**!\nâœ¨ Nháº­n Ä‘Æ°á»£c +10 EXP."
    if leveled_up:
        reply_msg += f"\nðŸ† CHÃšC Má»ªNG! Cáº­u Ä‘Ã£ thÄƒng cáº¥p lÃªn Level {new_level}!"
        
    await message.answer(reply_msg, parse_mode="Markdown")

from aiogram.types import CallbackQuery

@router.callback_query(F.data.startswith("done_"))
async def process_done_callback(callback: CallbackQuery):
    """Xá»­ lÃ½ khi user báº¥m nÃºt 'HoÃ n thÃ nh' trÃªn tin nháº¯n"""
    task_id = int(callback.data.split("_")[1])
    telegram_id = str(callback.from_user.id)
    user_id = db.get_user_id(telegram_id)
    
    task = db.get_task_by_id(task_id)
    if not task or task[1] != user_id:
        await callback.answer("KhÃ´ng tÃ¬m tháº¥y nhiá»‡m vá»¥ nÃ y!", show_alert=True)
        return
        
    description = task[4] or ""
    if "XÃ¡c thá»±c chá»‘ng gian láº­n" in description:
        await callback.answer("âš ï¸ Nhiá»‡m vá»¥ nÃ y yÃªu cáº§u chá»¥p áº£nh xÃ¡c thá»±c! HÃ£y gá»­i áº£nh nhÃ©.", show_alert=True)
        return
        
    completed_task_ids = db.get_completed_tasks_today(user_id)
    if task_id in completed_task_ids:
        await callback.answer("Nhiá»‡m vá»¥ nÃ y Ä‘Ã£ hoÃ n thÃ nh rá»“i!", show_alert=True)
        return
        
    db.log_daily_progress(user_id, task_id, "completed", "text", "Äiá»ƒm danh qua nÃºt báº¥m", "Tá»‘t")
    db.check_and_update_streak(user_id, is_active=True)
    leveled_up, new_level = db.add_exp(user_id, 10)
    
    reply_msg = f"ðŸŽ‰ Giá»i láº¯m! Cáº­u Ä‘Ã£ hoÃ n thÃ nh nhiá»‡m vá»¥: **{task[3]}**!\nâœ¨ Nháº­n Ä‘Æ°á»£c +10 EXP."
    if leveled_up:
        reply_msg += f"\nðŸ† CHÃšC Má»ªNG! Cáº­u Ä‘Ã£ thÄƒng cáº¥p lÃªn Level {new_level}!"
        
    await callback.message.answer(reply_msg, parse_mode="Markdown")
    await callback.answer("ÄÃ£ ghi nháº­n hoÃ n thÃ nh!")

@router.message(F.photo)
async def photo_handler(message: Message, bot: Bot) -> None:
    """Xá»­ lÃ½ khi ngÆ°á»i dÃ¹ng gá»­i áº£nh (bÃ i táº­p, Ä‘iá»ƒm danh)"""
    telegram_id = str(message.from_user.id)
    user_id = db.get_user_id(telegram_id)
    msg = await message.answer("Tá»› Ä‘ang nhÃ¬n áº£nh cá»§a cáº­u... Chá» chÃºt nhÃ©!")
    
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", f"{photo.file_id}.jpg")
    await bot.download_file(file.file_path, destination=file_path)
    
    caption = message.caption or ""
    task_category = "ChÆ°a rÃµ"
    task_desc = "Cáº­u hÃ£y dá»±a vÃ o caption cá»§a user hoáº·c giá» giáº¥c hiá»‡n táº¡i Ä‘á»ƒ tá»± phÃ¡n Ä‘oÃ¡n xem user Ä‘ang muá»‘n ná»™p bÃ i gÃ¬."
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
        search_category = None
        if now.hour >= 5 and now.hour < 8:
            search_category = "Äiá»ƒm danh buá»•i sÃ¡ng"
        elif now.hour >= 16 and now.hour < 19:
            search_category = "Thá»ƒ dá»¥c thá»ƒ thao"
        elif now.hour >= 22 or now.hour < 2:
            search_category = "Skincare / Chuáº©n bá»‹ ngá»§"
            
        if search_category:
            tasks = db.get_daily_tasks(user_id)
            for t in tasks:
                t_id, cat, t_title, t_desc, t_time = t
                if cat == search_category:
                    task_id = t_id
                    task_category = f"[{cat}] {t_title}"
                    task_desc = t_desc
                    break
                    
        if not task_id:
            task_category = search_category or "Nhiá»‡m vá»¥ chÆ°a rÃµ"
            task_desc = "Dá»±a vÃ o bá»‘i cáº£nh, Ä‘Ã¡nh giÃ¡ áº£nh chá»¥p. (LÆ°u Ã½: Nhiá»‡m vá»¥ nÃ y khÃ´ng cÃ³ trong há»‡ thá»‘ng, sinh viÃªn khÃ´ng Ä‘Æ°á»£c cá»™ng EXP)."
            
    # Send to AI
    prompt_context = f"Nhiá»‡m vá»¥: {task_category}\nChi tiáº¿t nhiá»‡m vá»¥: {task_desc}\nCaption cá»§a user: {caption}"
    
    import asyncio
    from src.ai.evaluator import evaluate_image_report
    status, feedback = await asyncio.to_thread(evaluate_image_report, prompt_context, file_path)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    if status.upper() in ["COMPLETED", "PASSED"] and task_id:
        db.log_daily_progress(user_id, task_id, "completed", "photo", "ÄÃ£ ná»™p áº£nh báº±ng chá»©ng há»£p lá»‡.", feedback)
        db.check_and_update_streak(user_id, is_active=True)
        leveled_up, new_level = db.add_exp(user_id, 20) # áº¢nh Ä‘Æ°á»£c +20 EXP
        
        reply_msg = f"âœ… **Káº¾T QUáº¢: [PASSED]**\n\nTuyá»‡t vá»i! Nhiá»‡m vá»¥ **{task_category}** Ä‘Ã£ Ä‘Æ°á»£c Ä‘Ã¡nh dáº¥u HOÃ€N THÃ€NH.\nâœ¨ Nháº­n Ä‘Æ°á»£c +20 EXP!\n"
        if leveled_up:
            reply_msg += f"ðŸ† CHÃšC Má»ªNG! Cáº­u Ä‘Ã£ thÄƒng cáº¥p lÃªn Level {new_level}!\n"
        reply_msg += f"\n**Nháº­n xÃ©t cá»§a AI:**\n{feedback}"
        
        await msg.edit_text(reply_msg, parse_mode="Markdown")
    else:
        await msg.edit_text(f"Káº¿t quáº£: [{status.upper()}]\n\nNháº­n xÃ©t cá»§a AI:\n{feedback}")

@router.message(Command("scores"))
async def command_scores_handler(message: Message) -> None:
    """Xá»­ lÃ½ lá»‡nh /scores, xem láº¡i báº£ng Ä‘iá»ƒm Ä‘Ã£ lÆ°u mÃ  khÃ´ng cáº§n cÃ o láº¡i"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scores_output.json")
    
    if not os.path.exists(file_path):
        await message.answer("âŒ ChÆ°a cÃ³ dá»¯ liá»‡u báº£ng Ä‘iá»ƒm. Cáº­u hÃ£y cháº¡y lá»‡nh /update_scores Ã­t nháº¥t 1 láº§n Ä‘á»ƒ há»‡ thá»‘ng cÃ o Ä‘iá»ƒm vá» nhÃ©!")
        return
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            scores = json.load(f)
            
        if not scores:
            await message.answer("Báº£ng Ä‘iá»ƒm hiá»‡n táº¡i Ä‘ang trá»‘ng.")
            return
            
        res = "ðŸŽ“ <b>Báº¢NG ÄIá»‚M Cá»¦A Cáº¬U (Báº¢N LÆ¯U Gáº¦N NHáº¤T)</b> ðŸŽ“\n\n"
        
        # NhÃ³m theo tráº¡ng thÃ¡i Ä‘iá»ƒm
        passed = []
        failed = []
        studying = []
        
        import html
        for item in scores:
            diem_chu = item.get("diem_chu", "ChÆ°a cÃ³")
            ten_mon = html.escape(item['ten_mon'])
            
            # Cáº£nh bÃ¡o mÃ´n há»c Ä‘iá»ƒm tháº¥p (kÃ©o tá»¥t GPA)
            if diem_chu in ["D", "D+", "C-"]:
                text = f"ðŸ”´ <b>{ten_mon} ({item['so_tin_chi']} TC): {item['diem_tong_ket']} ({diem_chu})</b> <i>(Cáº£nh bÃ¡o kÃ©o tá»¥t GPA, cáº§n cÃ¢n nháº¯c há»c cáº£i thiá»‡n!)</i>"
                passed.append(text)
            else:
                text = f"â–ªï¸ {ten_mon} ({item['so_tin_chi']} TC): {item['diem_tong_ket']} ({diem_chu})"
                
                if diem_chu == "F":
                    failed.append(text)
                elif diem_chu == "ChÆ°a cÃ³":
                    studying.append(text)
                else:
                    passed.append(text)
                
        if failed:
            res += "âŒ <b>BÃO Äá»˜NG (Rá»šT MÃ”N):</b>\n" + "\n".join(failed) + "\n\n"
        if studying:
            res += "â³ <b>ÄANG Há»ŒC Ká»² NÃ€Y:</b>\n" + "\n".join(studying) + "\n\n"
        if passed:
            res += "âœ… <b>ÄÃƒ QUA MÃ”N:</b>\n" + "\n".join(passed) + "\n\n"
            
        res += "<i>ðŸ’¡ Ghi chÃº: Äá»ƒ cáº­p nháº­t Ä‘iá»ƒm sá»‘ má»›i nháº¥t tá»« trÆ°á»ng, hÃ£y dÃ¹ng lá»‡nh /update_scores</i>"
        
        # Gá»­i theo tá»«ng pháº§n náº¿u quÃ¡ dÃ i
        max_length = 4000
        if len(res) > max_length:
            parts = [res[i:i+max_length] for i in range(0, len(res), max_length)]
            for part in parts:
                await message.answer(part, parse_mode="HTML")
        else:
            await message.answer(res, parse_mode="HTML")
            
    except Exception as e:
        await message.answer(f"âŒ Lá»—i khi Ä‘á»c file báº£ng Ä‘iá»ƒm: {e}")


@router.message(Command("plan_today"))
async def command_plan_today_handler(message: Message) -> None:
    """Tá»± Ä‘á»™ng láº­p káº¿ hoáº¡ch HÃ”M NAY dá»±a trÃªn lá»‹ch há»c hiá»‡n táº¡i."""
    msg = await message.answer("Äang phÃ¢n tÃ­ch lá»‹ch há»c hÃ´m nay vÃ  Ä‘iá»ƒm sá»‘ Ä‘á»ƒ lÃªn káº¿ hoáº¡ch Ä‘á»™ng...")
    try:
        telegram_id = str(message.from_user.id)
        user_id = db.get_user_id(telegram_id)
        if not user_id:
            await msg.edit_text("Cáº­u chÆ°a Ä‘Äƒng kÃ½. HÃ£y gÃµ /start.")
            return
            
        from datetime import datetime
        import json
        import os
        from src.ai.strategy_planner import generate_daily_plan
        
        now = datetime.now()
        weekday_names = ["Thá»© Hai", "Thá»© Ba", "Thá»© TÆ°", "Thá»© NÄƒm", "Thá»© SÃ¡u", "Thá»© Báº£y", "Chá»§ Nháº­t"]
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
                        records_text += f"- MÃ´n yáº¿u: {item['ten_mon']} (Äiá»ƒm: {item['diem_chu']})\n"
        
        import asyncio
        plan = await asyncio.to_thread(generate_daily_plan, records_text, timetable_today, f"{today_weekday} {now.strftime('%d/%m')}")
        
        if plan and plan.get("daily_tasks"):
            db.clear_old_tasks_and_roadmap(user_id)
            for t in plan["daily_tasks"]:
                db.add_task(user_id, t.get("category", "Há»c thuáº­t"), t.get("title", ""), t.get("description", ""), "daily", t.get("target_time", "20:00"))
            await msg.edit_text(f"âœ… ÄÃ£ lÃªn lá»‹ch trÃ¬nh Ä‘á»™ng cho **{today_weekday}** thÃ nh cÃ´ng! GÃµ /tasks Ä‘á»ƒ xem ngay.")
        else:
            err = plan.get('error', 'KhÃ´ng cÃ³ error') if plan else 'Plan is None'
            raw = plan.get('raw_text', '') if plan else ''
            import html
            await msg.edit_text(f"âŒ Lá»—i sinh lá»‹ch trÃ¬nh tá»« AI.\nLá»—i: {html.escape(err)}\nRaw: {html.escape(raw)[:1000]}", parse_mode="HTML")
            
    except Exception as e:
        import traceback
        import html
        error_msg = traceback.format_exc()
        await msg.edit_text(f"ðŸš¨ Lá»—i há»‡ thá»‘ng:\n<pre>{html.escape(error_msg)}</pre>", parse_mode="HTML")


@router.message(Command("lichhoc"))
async def command_lichhoc_handler(message: Message) -> None:
    """Xem toÃ n bá»™ lá»‹ch há»c trong tuáº§n"""
    import os
    import json
    
    if not os.path.exists("data/last_schedule.json"):
        await message.answer("ChÆ°a cÃ³ dá»¯ liá»‡u lá»‹ch há»c. HÃ£y cháº¡y lá»‡nh /update_scores Ä‘á»ƒ láº¥y dá»¯ liá»‡u nhÃ©!")
        return
        
    with open("data/last_schedule.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)
        
    if not schedule:
        await message.answer("Tuáº§n nÃ y cáº­u khÃ´ng cÃ³ lá»‹ch há»c trÃªn trÆ°á»ng.")
        return
        
    msg_text = "ðŸ“… <b>Lá»ŠCH Há»ŒC TUáº¦N NÃ€Y Cá»¦A Cáº¬U:</b>\n\n"
    
    # Gom nhÃ³m theo thá»©
    from collections import defaultdict
    days = defaultdict(list)
    for item in schedule:
        wd = item.get("weekday")
        if not wd and "(" in item.get("raw_info", ""):
            wd = item.get("raw_info").split("(")[0].strip()
        elif not wd:
            wd = "KhÃ´ng rÃµ"
        raw_info = item.get("raw_info", "")
        parts = [p.strip() for p in raw_info.split('|')]
        if len(parts) >= 4:
            time_str = parts[-1]
            subj_str = parts[-2]
            room_str = parts[-3] if len(parts) >= 5 else ""
            days[wd].append(f"â° {time_str} - {subj_str} ({room_str})")
        else:
            days[wd].append(f"ðŸ“Œ {raw_info}")
            
    # Thá»© tá»± in
    order = ["Thá»© Hai", "Thá»© Ba", "Thá»© TÆ°", "Thá»© NÄƒm", "Thá»© SÃ¡u", "Thá»© Báº£y", "Chá»§ Nháº­t"]
    for d in order:
        if d in days:
            msg_text += f"<b>{d}:</b>\n"
            for t in days[d]:
                msg_text += f"{t}\n"
            msg_text += "\n"
            
    await message.answer(msg_text, parse_mode="HTML")

@router.message(F.text)
async def text_handler(message: Message) -> None:
    """Xá»­ lÃ½ tin nháº¯n text thÃ´ng thÆ°á»ng (tÃ³m táº¯t sÃ¡ch, tÃ¢m sá»±)"""
    text = message.text.lower()
    
    if text.startswith("/"):
        return # Bá» qua cÃ¡c lá»‡nh
        
    msg = await message.answer("Äang phÃ¢n tÃ­ch bÃ¡o cÃ¡o cá»§a cáº­u...")
    
    # Cháº¥m Ä‘iá»ƒm báº±ng AI
    import asyncio
    status, feedback = await asyncio.to_thread(evaluate_text_report, "TÃ³m táº¯t sÃ¡ch / BÃ¡o cÃ¡o chung", message.text)
    
    await msg.edit_text(f"Káº¿t quáº£: [{status.upper()}]\n\nNháº­n xÃ©t:\n{feedback}")



