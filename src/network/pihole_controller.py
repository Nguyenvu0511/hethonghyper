import os
import requests
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load config
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../..", "API_KEYS.txt"))
PIHOLE_URL = os.getenv("PIHOLE_URL") # Dành cho v6, đây thường là http://127.0.0.1
PIHOLE_AUTH_TOKEN = os.getenv("PIHOLE_AUTH_TOKEN")

def get_session():
    """Lấy Session ID và CSRF token từ API v6"""
    try:
        # Nếu url có chứa admin/api.php, gọt bỏ đi
        base_url = PIHOLE_URL.replace("/admin/api.php", "")
        auth_url = f"{base_url}/api/auth"
        payload = {"password": PIHOLE_AUTH_TOKEN}
        response = requests.post(auth_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # session object chứa sid và csrf
            session = data.get("session", {})
            if session:
                return session.get("sid"), session.get("csrf"), base_url
        logger.error(f"Lỗi xác thực Pi-hole v6: {response.text}")
        return None, None, None
    except Exception as e:
        logger.error(f"Lỗi khi gọi API Auth Pi-hole: {e}")
        return None, None, None

def enable_blocklist():
    """Bật lại blocklist (Thiết quân luật/Giới nghiêm)"""
    if not PIHOLE_AUTH_TOKEN or PIHOLE_AUTH_TOKEN == "YOUR_PIHOLE_AUTH_TOKEN_HERE":
        logger.info("[MOCK PI-HOLE] Đã BẬT blocklist (Internet đã bị chặn).")
        return True
        
    sid, csrf, base_url = get_session()
    if not sid:
        return False
        
    try:
        headers = {
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf,
            "Content-Type": "application/json"
        }
        url = f"{base_url}/api/dns/blocking"
        payload = {"blocking": True}
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info("Pi-hole: Đã bật blocklist thành công.")
            return True
        else:
            logger.error(f"Pi-hole lỗi: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Lỗi gọi API Pi-hole: {e}")
        return False

def disable_blocklist(seconds=3600):
    """Tạm thời tắt blocklist (Mở Internet) trong `seconds` giây"""
    if not PIHOLE_AUTH_TOKEN or PIHOLE_AUTH_TOKEN == "YOUR_PIHOLE_AUTH_TOKEN_HERE":
        logger.info(f"[MOCK PI-HOLE] Đã TẮT blocklist trong {seconds} giây (Được phép vào mạng).")
        return True
        
    sid, csrf, base_url = get_session()
    if not sid:
        return False
        
    try:
        headers = {
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf,
            "Content-Type": "application/json"
        }
        url = f"{base_url}/api/dns/blocking"
        payload = {"blocking": False, "timer": seconds}
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"Pi-hole: Đã tắt blocklist tạm thời ({seconds} giây).")
            return True
        else:
            logger.error(f"Pi-hole lỗi: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Lỗi gọi API Pi-hole: {e}")
        return False

