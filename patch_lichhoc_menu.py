# -*- coding: utf-8 -*-
with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_menu = '''        BotCommand(command="quiz", description="Làm bài tập xóa mù chữ")
    ]'''
new_menu = '''        BotCommand(command="quiz", description="Làm bài tập xóa mù chữ"),
        BotCommand(command="lichhoc", description="Xem thời khóa biểu tuần này")
    ]'''

content = content.replace(old_menu, new_menu)

with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)