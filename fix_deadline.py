with open('src/scheduler/daily_cron.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = '''async def check_upcoming_deadlines(bot: Bot):
    """Kiểm tra và nhắc nhở các task sắp tới deadline (15 phút)"""
    users = db.get_all_users()'''

new_str = '''async def check_upcoming_deadlines(bot: Bot):
    """Kiểm tra và nhắc nhở các task sắp tới deadline (15 phút)"""
    from src.database.db_manager import db
    users = db.get_all_users()'''

content = content.replace(old_str, new_str)

with open('src/scheduler/daily_cron.py', 'w', encoding='utf-8') as f:
    f.write(content)