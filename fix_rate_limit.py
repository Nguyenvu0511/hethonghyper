with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()
old_cmd = 'await bot.set_my_commands(commands)'
new_cmd = '''try:
        await bot.set_my_commands(commands)
    except Exception as e:
        print(f"Không thể set commands (có thể do rate limit): {e}")'''
content = content.replace(old_cmd, new_cmd)
with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)