from apscheduler.schedulers.asyncio import AsyncIOScheduler

def test_func(a, b):
    pass

scheduler = AsyncIOScheduler()
try:
    scheduler.add_job(test_func, 'cron', hour=5, args=['test'])
    print("Success")
except Exception as e:
    print("Error:", e)