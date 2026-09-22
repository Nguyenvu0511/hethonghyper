import asyncio
import logging
import os
import sys

# Khắc phục lỗi Unicode trên Windows (cp1252)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from src.bot.handlers import router
from src.scheduler.daily_cron import setup_scheduler

# Load biến môi trường từ file .env
load_dotenv()
load_dotenv("API_KEYS.txt")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main() -> None:
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Lỗi: Không tìm thấy TELEGRAM_BOT_TOKEN hợp lệ trong file .env")
        sys.exit(1)
        
    # Khởi tạo Bot và Dispatcher
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Đăng ký các router (handlers)
    dp.include_router(router)

    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Khởi động bot"),
        BotCommand(command="tasks", description="Xem nhiệm vụ hôm nay"),
        BotCommand(command="status", description="Xem thống kê Level & EXP"),
        BotCommand(command="plan_today", description="Lập kế hoạch linh động cho hôm nay"),
        BotCommand(command="update_scores", description="Cập nhật bảng điểm & Lộ trình"),
        BotCommand(command="check_news", description="Quét thông báo MyDTU"),
        BotCommand(command="scores", description="Xem bảng điểm MyDTU"),
        BotCommand(command="quiz", description="Làm bài tập xóa mù chữ"),
        BotCommand(command="lichhoc", description="Xem thời khóa biểu tuần này"),
        BotCommand(command="done", description="Đánh dấu xong nhiệm vụ (nhập ID)")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        print(f"Không thể set commands (có thể do rate limit): {e}")

    
    # Khởi chạy Scheduler (Giả định user đầu tiên là Admin để nhận thông báo)
    # Trong thực tế nên query Database lấy user_id
    setup_scheduler(bot) # Cần update chỗ này nếu muốn push chính xác
    
    # Xóa webhook cũ (nếu có) và bắt đầu polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot đang chạy... (Nhấn Ctrl+C để dừng)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
