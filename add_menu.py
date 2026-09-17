# -*- coding: utf-8 -*-
with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

menu_code = '''
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Khởi động bot"),
        BotCommand(command="tasks", description="Xem nhiệm vụ hôm nay"),
        BotCommand(command="status", description="Xem thống kê Level & EXP"),
        BotCommand(command="plan_today", description="Lập kế hoạch linh động cho hôm nay"),
        BotCommand(command="update_scores", description="Cập nhật bảng điểm & Lộ trình"),
        BotCommand(command="check_news", description="Quét thông báo MyDTU"),
        BotCommand(command="scores", description="Xem bảng điểm MyDTU"),
        BotCommand(command="quiz", description="Làm bài tập xóa mù chữ")
    ]
    await bot.set_my_commands(commands)
'''

# insert after dp.include_router(router)
content = content.replace("dp.include_router(router)", "dp.include_router(router)\n" + menu_code)

with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)