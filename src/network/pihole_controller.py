import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def enable_blocklist():
    """Bật lại blocklist (Thiết quân luật/Giới nghiêm)"""
    try:
        # Nếu Bot chạy cùng server với Pi-hole, gọi lệnh trực tiếp
        result = subprocess.run(["pihole", "enable"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Pi-hole: Đã bật blocklist thành công (CLI).")
            return True
        else:
            logger.error(f"Pi-hole lỗi (CLI): {result.stderr}")
            return False
    except FileNotFoundError:
        logger.info("[MOCK PI-HOLE] Lệnh pihole không tồn tại. Đã BẬT blocklist ảo.")
        return True
    except Exception as e:
        logger.error(f"Lỗi gọi CLI Pi-hole: {e}")
        return False

def disable_blocklist(seconds=7200):
    """Tạm thời tắt blocklist (Mở Internet) trong `seconds` giây"""
    minutes = seconds // 60
    try:
        result = subprocess.run(["pihole", "disable", f"{minutes}m"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Pi-hole: Đã tắt blocklist tạm thời ({minutes} phút).")
            return True
        else:
            logger.error(f"Pi-hole lỗi (CLI): {result.stderr}")
            return False
    except FileNotFoundError:
        logger.info(f"[MOCK PI-HOLE] Lệnh pihole không tồn tại. Đã TẮT blocklist trong {minutes} phút.")
        return True
    except Exception as e:
        logger.error(f"Lỗi gọi CLI Pi-hole: {e}")
        return False
