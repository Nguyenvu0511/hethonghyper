import os
import requests
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load config
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../..", "API_KEYS.txt"))
PIHOLE_URL = os.getenv("PIHOLE_URL")
PIHOLE_AUTH_TOKEN = os.getenv("PIHOLE_AUTH_TOKEN")

def enable_blocklist():
    """Bật lại blocklist (Thiết quân luật/Giới nghiêm)"""
    if not PIHOLE_AUTH_TOKEN or PIHOLE_AUTH_TOKEN == "YOUR_PIHOLE_AUTH_TOKEN_HERE":
        logger.info("[MOCK PI-HOLE] Đã BẬT blocklist (Internet đã bị chặn).")
        return True
        
    try:
        url = f"{PIHOLE_URL}?enable=1&auth={PIHOLE_AUTH_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Pi-hole: Đã bật blocklist thành công.")
            return True
        else:
            logger.error(f"Pi-hole lỗi: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Lỗi gọi API Pi-hole: {e}")
        return False

def disable_blocklist(seconds=7200):
    """Tạm thời tắt blocklist (Mở Internet) trong `seconds` giây"""
    if not PIHOLE_AUTH_TOKEN or PIHOLE_AUTH_TOKEN == "YOUR_PIHOLE_AUTH_TOKEN_HERE":
        logger.info(f"[MOCK PI-HOLE] Đã TẮT blocklist trong {seconds} giây (Được phép vào mạng).")
        return True
        
    try:
        url = f"{PIHOLE_URL}?disable={seconds}&auth={PIHOLE_AUTH_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Pi-hole: Đã tắt blocklist tạm thời ({seconds} giây).")
            return True
        else:
            logger.error(f"Pi-hole lỗi: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Lỗi gọi API Pi-hole: {e}")
        return False
