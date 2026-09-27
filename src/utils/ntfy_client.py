import aiohttp
import logging

logger = logging.getLogger(__name__)

NTFY_TOPIC = "atsuki_study_bot_secret_xyz" # Change this if needed
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

async def send_ntfy_alert(message: str, title: str = "Báo động từ Bot", priority: str = "high", tags: str = "warning,loudspeaker"):
    """
    Gửi thông báo ntfy
    priority: min, low, default, high, max
    """
    headers = {
        "Title": title.encode('utf-8'),
        "Priority": priority,
        "Tags": tags
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(NTFY_URL, data=message.encode('utf-8'), headers=headers) as resp:
                if resp.status == 200:
                    logger.info(f"Đã gửi cảnh báo ntfy thành công: {title}")
                else:
                    logger.warning(f"Gửi ntfy thất bại, status: {resp.status}")
    except Exception as e:
        logger.error(f"Lỗi khi gửi ntfy: {e}")
