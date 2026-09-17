import os
import sys
import logging
import asyncio
import base64
import hashlib
import json
import random
import re
import httpx
from datetime import datetime, timezone, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class MaintenanceError(Exception):
    """Ngoại lệ xảy ra khi hệ thống MyDTU đang bảo trì hoặc sao lưu dữ liệu."""
    pass


# Đảm bảo mã hóa UTF-8 khi chạy trên terminal Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Tải cấu hình từ file .env nếu chạy cục bộ (Local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("TimetableBot")

# Lấy các biến cấu hình
MYDTU_USER = os.getenv("MYDTU_USER")
MYDTU_PASS = os.getenv("MYDTU_PASS")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

_ocr_instance = None

def get_ocr_instance():
    """Khởi tạo và giữ một phiên bản ddddocr duy nhất trong bộ nhớ (singleton)."""
    global _ocr_instance
    if _ocr_instance is None:
        try:
            import ddddocr
            _ocr_instance = ddddocr.DdddOcr(show_ad=False)
            logger.info("Đã khởi tạo thư viện ddddocr nhận diện Captcha thành công.")
        except Exception as e:
            logger.warning(f"Không thể khởi tạo thư viện ddddocr cục bộ: {e}")
    return _ocr_instance

def solve_captcha_via_ddddocr(image_bytes: bytes) -> str:
    """
    Giải mã Captcha MyDTU siêu tốc bằng thư viện ddddocr (offline, chính xác, không phụ thuộc API).
    """
    ocr = get_ocr_instance()
    if ocr is None:
        raise RuntimeError("ddddocr chưa được cài đặt hoặc khởi tạo không thành công.")
    res = ocr.classification(image_bytes)
    return res.strip().replace(" ", "").upper()

def get_random_salutation() -> str:
    """
    Sinh câu chào ngẫu nhiên thân mật (Chào Vũ, Chào Zũ, Hí lu, Hi lo, Hí lo...).
    """
    salutations = [
        "👋 Chào Vũ",
        "👋 Chào Zũ",
        "✨ Hí lu Vũ",
        "✨ Hí lu Zũ",
        "💫 Hi lo Vũ",
        "💫 Hi lo Zũ",
        "🌟 Hí lo Vũ",
        "🌟 Hí lo Zũ",
        "👋 Hé lo Vũ",
        "✨ Hé lo Zũ",
        "👋 Chào Zũ nè",
        "🌸 Hí lu Zũ"
    ]
    return random.choice(salutations)

async def generate_dynamic_greeting_via_gemini(api_key: str, user_name: str = "Vũ", day_status: str = "") -> str:
    """
    Sử dụng Google Gemini API để tự động sinh lời chúc độc đáo, ngắn gọn và đầy động lực mỗi ngày cho Vũ.
    """
    if not api_key:
        return ""

    MODEL_NAME = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"

    prompt = (
        f"Bạn là 'Trợ lý chu đáo', một người bạn đồng hành tích cực, thân thiện và đầy năng lượng của bạn {user_name}.\n"
        f"Hãy viết 1 lời chúc hoặc câu nhắn gửi ngắn gọn (1 đến 2 câu), mới mẻ hoàn toàn, không trùng lặp và đầy động lực cho {user_name}.\n"
        f"Bối cảnh hôm nay: {day_status}.\n"
        f"Yêu cầu:\n"
        f"- Dưới 30 từ, tự nhiên, xưng 'tớ' và gọi '{user_name}' hoặc 'cậu' (Tuyệt đối KHÔNG gọi là 'Hoàng Vũ').\n"
        f"- Tuyệt đối không dùng các câu sáo rỗng, truyền cảm hứng tích cực cho ngày mới.\n"
        f"- Chỉ trả về duy nhất nội dung lời chúc, không có dấu ngoặc kép hay tiêu đề."
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("candidates") and data["candidates"][0].get("content"):
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text.startswith('"') and text.endswith('"'):
                        text = text[1:-1].strip()
                    return text
    except Exception as e:
        logger.warning(f"Không thể sinh lời chúc động từ Gemini API ({e}), sẽ dùng lời chúc mặc định.")

    return ""

def clean_and_parse_schedule_text(raw_info: str) -> list[str]:
    """
    Làm sạch chuỗi thời khóa biểu cào từ MyDTU:
    - Loại bỏ các mốc giờ rác time grid (7sa, 8sa, 9sa...)
    - Tách các môn học bị dính chùm thành từng dòng riêng
    """
    if not raw_info:
        return []

    # 1. Chuẩn hóa khoảng trắng và dấu gạch đứng
    cleaned = re.sub(r'[\r\n]+', ' | ', raw_info)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'(\s*\|\s*)+', ' | ', cleaned).strip(' |')

    # 2. Tìm tất cả các môn học có cấu trúc chuẩn: Mã_Môn | Tên_Môn | Phòng | Giờ
    # Ví dụ: EE 301 I | Kỹ Thuật Điện Nâng Cao | P. Online 19, Online | 07:00-09:00
    subject_pattern = r'([A-Z]{2,4}\s*\d{3}\s*[A-Z0-9]*\s*\|\s*[^\|]+\|\s*(?:P\.|Phòng|Sân)[^\|]+\|\s*\d{2}:\d{2}-\d{2}:\d{2})'
    matches = re.findall(subject_pattern, cleaned, re.IGNORECASE)
    
    if matches:
        results = []
        for m in matches:
            m_clean = re.sub(r'(\s*\|\s*)+', ' | ', m).strip(' |')
            if is_valid_schedule_item(m_clean):
                results.append(m_clean)
        if results:
            return results

    # 3. Phương thức dự phòng: Lọc bỏ các từ rác mốc giờ "7sa", "8sa", "9sa"...
    cleaned = re.sub(r'\b(?:\d{1,2}(?:sa|ch))\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'(\s*\|\s*)+', ' | ', cleaned).strip(' |')

    if is_valid_schedule_item(cleaned) and len(cleaned) > 8:
        return [cleaned]

    return []

def is_valid_schedule_item(raw_info: str) -> bool:
    """
    Lọc bỏ các tiêu đề menu, tên tab, rác time-grid và các ngày tháng đơn thuần không chứa môn học.
    """
    text_lower = raw_info.lower().strip()
    
    # Bỏ qua các chuỗi trùng khớp với tiêu đề menu/tab
    ignored_keywords = [
        "lịch học | lịch cá nhân",
        "lịch cá nhân",
        "lịch học",
        "lịch thi",
        "xem lịch học",
        "trang chủ",
        "thông báo",
        "đăng xuất"
    ]
    if text_lower in ignored_keywords:
        return False
        
    # Bỏ qua các dòng chỉ chứa ngày tháng mà không có môn học/tiết/phòng (Ví dụ: "Thứ bảy, ngày 1 tháng 8 năm 2026")
    if text_lower.startswith("thứ") and "ngày" in text_lower and "năm" in text_lower:
        if not any(k in text_lower for k in ["tiết", "phòng", "môn", "lớp", "mã", "học phần", "tín chỉ"]):
            return False

    # Bỏ qua các dòng dump time-grid (7sa, 8sa, 9sa...)
    time_slots = ["7sa", "8sa", "9sa", "10sa", "11sa", "12ch", "1ch", "2ch", "3ch", "4ch", "5ch", "6ch", "7ch", "8ch", "9ch", "10ch"]
    found_slots = sum(1 for slot in time_slots if slot in text_lower)
    if found_slots >= 3 and not any(k in text_lower for k in ["môn", "p.", "phòng", "online", "tòa nhà", "nguyễn văn linh", "hòa khánh"]):
        return False

    return True

def get_class_type_tag(raw_info: str) -> str:
    """
    Phân loại hình thức học:
    - 💻🏠 [ONLINE TẠI NHÀ (GV ở trường)]: Lớp học tập trung & trực tuyến
    - 💻 [ONLINE TẠI NHÀ]: Học online hoàn toàn
    - 🏫 [HỌC TẠI TRƯỜNG]: Học trực tiếp trên lớp
    """
    text_lower = raw_info.lower()
    
    # 1. Hình thức Lớp Học Tập Trung & Trực Tuyến
    if any(k in text_lower for k in ["tập trung & trực tuyến", "tập trung và trực tuyến", "tập trung & online", "tập trung và online"]):
        return "💻🏠 [ONLINE TẠI NHÀ (GV ở trường)]"
        
    # 2. Hình thức Trực tuyến / Online hoàn toàn
    online_keywords = ["trực tuyến", "online", "zoom", "teams", "lms", "e-learning", "google meet"]
    if any(k in text_lower for k in online_keywords):
        return "💻 [ONLINE TẠI NHÀ]"
        
    # 3. Hình thức Học trực tiếp tại trường
    return "🏫 [HỌC TẠI TRƯỜNG]"

def extract_radscheduler_appointments(page_content: str) -> list[dict]:
    """
    Trích xuất lịch học trực tiếp từ RadScheduler JSON trong mã nguồn HTML MyDTU.
    Bao gồm chính xác Thứ, Ngày (dd/mm), Mã môn, Tên môn, Phòng học và Giờ.
    """
    weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    items = []
    
    app_matches = re.findall(r'\"appointments\"\s*:\s*\"(\[.*?\])\"', page_content)
    for match_str in app_matches:
        try:
            cleaned_json = match_str.replace(r'\"', '"').replace(r'\\', '\\')
            app_list = json.loads(cleaned_json)
            for app in app_list:
                subj = app.get("subject", "").strip()
                start_str = app.get("start", "").strip()  # "2026/08/10 09:15"
                if subj and start_str:
                    try:
                        dt = datetime.strptime(start_str, "%Y/%m/%d %H:%M")
                        wd_name = weekday_names[dt.weekday()]
                        date_str = dt.strftime("%d/%m")
                        raw_info = f"{wd_name} ({date_str}) | {subj}"
                        items.append({
                            "raw_info": raw_info,
                            "weekday": wd_name,
                            "date": date_str,
                            "start_dt": dt.isoformat()
                        })
                    except Exception as de:
                        logger.warning(f"Lỗi parse ngày start {start_str}: {de}")
                        items.append({"raw_info": subj})
        except Exception as e:
            logger.warning(f"Lỗi parse JSON appointments từ RadScheduler: {e}")

    items.sort(key=lambda x: x.get("start_dt", ""))
    return items

def format_class_item_display(idx: int, raw_info: str, tag_prefix: str = "📌", icon_class: str = "") -> str:
    """
    Định dạng hiển thị môn học ngắn gọn, rõ ràng, dễ đọc trên Discord.
    """
    type_tag = get_class_type_tag(raw_info)
    prefix_str = f"{tag_prefix} **{idx}.**" if not icon_class else f"{icon_class} **{idx}.**"
    
    parts = [p.strip() for p in raw_info.split("|") if p.strip()]
    
    # Bỏ phần Thứ/Ngày ở đầu nếu có (vì đã in ở tiêu đề Thứ)
    if parts and any(w in parts[0].lower() for w in ["thứ", "chủ nhật"]):
        parts = parts[1:]

    if len(parts) >= 4:
        code = parts[0]
        name = parts[1]
        room = parts[2]
        time_str = parts[3]
        return f"{prefix_str} {type_tag} **{code}** - *{name}*\n   📍 *{room}* | ⏰ *{time_str}*"
    elif len(parts) == 3:
        return f"{prefix_str} {type_tag} **{parts[0]}** - *{parts[1]}*\n   📍 *{parts[2]}*"
    else:
        info_clean = " | ".join(parts)
        return f"{prefix_str} {type_tag} {info_clean}"

class DTUScraper:
    """
    Lớp cào dữ liệu từ MyDTU, tự động đăng nhập và vượt Captcha bằng ddddocr.
    """
    def __init__(self, username=MYDTU_USER, password=MYDTU_PASS):
        self.username = username
        self.password = password
        self.login_url = "https://mydtu.duytan.edu.vn/Signin.aspx"
        self.timetable_url = "https://mydtu.duytan.edu.vn/sites/index.aspx?p=home_timetable&functionid=13"

    async def login(self, page) -> bool:
        """
        Đăng nhập vào cổng MyDTU (Hỗ trợ thử lại nếu máy chủ ngắt kết nối tạm thời).
        """
        for nav_attempt in range(1, 4):
            try:
                logger.info(f"Đang điều hướng tới trang đăng nhập (Lần {nav_attempt}/3): {self.login_url}")
                await page.goto(self.login_url, wait_until="load", timeout=40000)
                break
            except Exception as ne:
                err_txt = str(ne).lower()
                if any(k in err_txt for k in ["err_connection_refused", "err_name_not_resolved", "err_connection_timed_out", "timeout"]):
                    logger.warning(f"⚠️ [Lần thử {nav_attempt}/3] MyDTU tạm thời ngắt kết nối/bảo trì: {ne}")
                    if nav_attempt < 3:
                        await asyncio.sleep(8)
                        continue
                    else:
                        raise MaintenanceError("Cổng thông tin MyDTU hiện đang từ chối kết nối hoặc máy chủ đang khởi động lại.")
                raise ne

        # Kiểm tra trạng thái bảo trì hoặc sao lưu dữ liệu của MyDTU
        body_element = await page.query_selector("body")
        if body_element:
            body_text = await body_element.inner_text()
            if any(k in body_text.lower() for k in ["sao lưu dữ liệu", "under construction", "bảo trì"]):
                logger.warning("⚠️ Cổng thông tin MyDTU hiện đang bảo trì hoặc sao lưu dữ liệu.")
                raise MaintenanceError("MyDTU đang bảo trì hoặc sao lưu dữ liệu.")

        # Ẩn các quảng cáo và popup phiền phức
        await page.add_style_tag(content=".darkness, #popout, #adbox { display: none !important; }")

        login_success = False
        for attempt in range(1, 11):
            logger.info(f"--- Đăng nhập MyDTU - Lần thử {attempt}/10 ---")
            
            await page.fill("input#txtUser", self.username)
            await page.fill("input#txtPass", self.password)

            captcha_element = await page.query_selector('#UpdatePanel1 img, img[src*="CaptchaImage.axd"]')
            if not captcha_element:
                logger.error("Không tìm thấy ảnh Captcha trên trang đăng nhập.")
                return False

            # Lấy ảnh Captcha chuẩn từ canvas (giữ nguyên độ phân giải pixel gốc như Extension)
            try:
                b64_data = await page.evaluate('''() => {
                    const img = document.querySelector('#UpdatePanel1 img') || document.querySelector('img[src*="CaptchaImage.axd"]');
                    if (!img || !img.complete || img.naturalWidth === 0) return null;
                    const canvas = document.createElement("canvas");
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0);
                    return canvas.toDataURL("image/png").replace(/^data:image\\/(png|jpg|jpeg);base64,/, "");
                }''')
                if b64_data:
                    captcha_bytes = base64.b64decode(b64_data)
                else:
                    captcha_bytes = await captcha_element.screenshot()
            except Exception:
                captcha_bytes = await captcha_element.screenshot()

            # Giải Captcha siêu tốc bằng ddddocr
            try:
                captcha_code = solve_captcha_via_ddddocr(captcha_bytes)
                logger.info(f"⚡ [Lần {attempt}/10] ddddocr giải mã Captcha: {captcha_code}")
            except Exception as de:
                logger.warning(f"Lỗi khi giải captcha bằng ddddocr: {de}. Đang thử lại...")
                await page.reload(wait_until="load")
                await page.add_style_tag(content=".darkness, #popout, #adbox { display: none !important; }")
                continue

            await page.fill("input#txtCaptcha", captcha_code)
            await page.click("input#btnLogin1")

            # Chờ chuyển hướng sang index.aspx hoặc có thông báo lỗi trả về nhanh
            try:
                await page.wait_for_function('''() => {
                    const msg = document.getElementById("lbMessage");
                    const isError = msg && msg.innerText.trim().length > 0;
                    const isNavigated = window.location.href.includes("index.aspx");
                    return isError || isNavigated;
                }''', timeout=10000)
            except PlaywrightTimeoutError:
                pass

            if "index.aspx" in page.url:
                login_success = True
                break

            # Kiểm tra xem có phải trang web chuyển sang trang bảo trì/sao lưu hay không
            body_element = await page.query_selector("body")
            if body_element:
                body_text = await body_element.inner_text()
                if any(k in body_text.lower() for k in ["sao lưu dữ liệu", "under construction", "bảo trì"]):
                    logger.warning("⚠️ Phát hiện MyDTU đã chuyển sang trang bảo trì hoặc sao lưu dữ liệu.")
                    raise MaintenanceError("MyDTU đang bảo trì hoặc sao lưu dữ liệu.")

            error_element = await page.query_selector("span#lbMessage")
            if error_element:
                error_text = (await error_element.inner_text()).strip()
                if error_text:
                    logger.warning(f"Đăng nhập không thành công (Lần {attempt}/10): {error_text}")
                    if "mật khẩu" in error_text.lower() or "tên đăng nhập" in error_text.lower():
                        logger.error("Sai tài khoản hoặc mật khẩu MyDTU.")
                        return False
            else:
                logger.warning(f"Đăng nhập không thành công (Lần {attempt}/10 - Hết thời gian chờ hoặc Captcha sai).")
            
            if attempt < 10:
                logger.info("Đang tải lại trang đăng nhập để lấy Captcha mới...")
                await page.goto(self.login_url, wait_until="load", timeout=25000)
                await page.add_style_tag(content=".darkness, #popout, #adbox { display: none !important; }")
                continue

        if not login_success:
            logger.error("Không thể đăng nhập sau 10 lần thử giải Captcha.")
            return False

        logger.info("Đăng nhập thành công và đã truy cập hệ thống.")
        return True

    async def fetch_timetable(self) -> dict:
        """
        Đăng nhập MyDTU và cào lịch học hiện tại.
        """
        result = {
            "success": False,
            "timetable": [],
            "hash": "",
            "message": ""
        }

        async with async_playwright() as p:
            logger.info("Đang khởi động trình duyệt ẩn (Headless Chromium)...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ignore_https_errors=True
            )
            page = await context.new_page()

            try:
                if not await self.login(page):
                    result["message"] = "Đăng nhập vào hệ thống MyDTU thất bại."
                    return result

                logger.info(f"Đang mở trang thời khóa biểu: {self.timetable_url}")
                await page.goto(self.timetable_url, wait_until="domcontentloaded", timeout=40000)

                # Chờ RadScheduler và các phần tử lịch học AJAX xuất hiện
                try:
                    await page.wait_for_selector(".rsApt, [id*='RadScheduler'], table", timeout=20000)
                    await asyncio.sleep(4)
                except Exception as we:
                    logger.warning(f"Chờ RadScheduler load timeout: {we}")

                items = []

                async def extract_current_view():
                    view_items = []
                    # Cách 1: Gọi JavaScript RadScheduler Client API trực tiếp từ trình duyệt
                    try:
                        js_appts = await page.evaluate('''() => {
                            try {
                                const el = document.querySelector("[id*='RadScheduler']");
                                if (!el) return null;
                                const scheduler = $find(el.id);
                                if (!scheduler) return null;
                                const appts = scheduler.get_appointments();
                                return appts.map(a => {
                                    const st = a.get_start();
                                    return {
                                        subject: a.get_subject(),
                                        year: st.getFullYear(),
                                        month: st.getMonth() + 1,
                                        day: st.getDate(),
                                        hours: st.getHours(),
                                        minutes: st.getMinutes()
                                    };
                                });
                            } catch(e) {
                                return null;
                            }
                        }''')
                        
                        if js_appts:
                            weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
                            for a in js_appts:
                                subj = a.get("subject", "").strip()
                                if subj:
                                    try:
                                        dt = datetime(a["year"], a["month"], a["day"], a["hours"], a["minutes"])
                                        wd_name = weekday_names[dt.weekday()]
                                        date_str = dt.strftime("%d/%m")
                                        raw_info = f"{wd_name} ({date_str}) | {subj}"
                                        view_items.append({
                                            "raw_info": raw_info,
                                            "weekday": wd_name,
                                            "date": date_str,
                                            "start_dt": dt.isoformat()
                                        })
                                    except Exception as de:
                                        view_items.append({"raw_info": subj})
                    except Exception as jse:
                        pass

                    # Cách 2: Trích xuất trực tiếp từ RadScheduler JSON trong mã nguồn HTML trang
                    if not view_items:
                        page_content = await page.content()
                        view_items = extract_radscheduler_appointments(page_content)

                    # Cách 3 (Dự phòng): Quét theo các bảng thời khóa biểu
                    if not view_items:
                        tables = await page.query_selector_all("table")
                        for table in tables:
                            rows = await table.query_selector_all("tr")
                            for row in rows:
                                cols = await row.query_selector_all("td, th")
                                if len(cols) >= 3:
                                    col_texts = [(await c.inner_text()).strip() for c in cols]
                                    text_combined = " ".join(col_texts).lower()
                                    if any(k in text_combined for k in ["thứ", "tiết", "phòng", "môn", "lớp", "học"]):
                                        if any(char.isdigit() for char in text_combined):
                                            view_items.append({
                                                "raw_info": " | ".join([t for t in col_texts if t])
                                            })
                    
                    # Cách 4 (Dự phòng): Quét div dạng card/item
                    if not view_items:
                        card_elements = await page.query_selector_all("div.card, div.item, div[class*='timetable'], div[class*='lichhoc']")
                        for card in card_elements:
                            txt = (await card.inner_text()).strip()
                            if txt and len(txt) > 10:
                                view_items.append({"raw_info": " ".join(txt.split())})
                    
                    return view_items

                items = await extract_current_view()
                if items:
                    logger.info(f"Đã trích xuất thành công {len(items)} buổi học của tuần hiện tại.")

                # Tự động lấy thêm lịch tuần tới nếu hôm nay là cuối tuần (Thứ Bảy hoặc Chủ Nhật)
                vn_tz = timezone(timedelta(hours=7))
                now_vn = datetime.now(vn_tz)
                if now_vn.weekday() >= 5:
                    try:
                        next_btn = await page.query_selector(".rsNext, .rsArrowNext, a[title='Next'], a[title='Next Week'], a:has-text('Next')")
                        if next_btn:
                            logger.info("Hôm nay là cuối tuần. Đang bấm nút Next để tải thêm lịch học tuần tới...")
                            await next_btn.click()
                            await asyncio.sleep(5)  # Chờ AJAX load
                            
                            next_week_items = await extract_current_view()
                            if next_week_items:
                                items.extend(next_week_items)
                                logger.info(f"Đã lấy thêm {len(next_week_items)} buổi học của tuần tới.")
                    except Exception as e:
                        logger.warning(f"Không thể lấy lịch học tuần tới: {e}")

                # Lọc bỏ các mục rác time-grid, tách các môn bị dính chùm và xóa trùng lặp
                cleaned_items = []
                seen_raw = set()
                for item in items:
                    raw_str = item.get("raw_info", "")
                    
                    if "start_dt" in item:
                        # Dữ liệu từ RadScheduler đã chuẩn, chỉ cần dọn dẹp nhẹ
                        prefix = ""
                        subject_part = raw_str
                        if " | " in raw_str:
                            parts = raw_str.split(" | ", 1)
                            prefix = parts[0] + " | "
                            subject_part = parts[1]
                        
                        subj_clean = re.sub(r'[\r\n]+', ' | ', subject_part)
                        subj_clean = re.sub(r'\s+', ' ', subj_clean)
                        subj_clean = re.sub(r'(\s*\|\s*)+', ' | ', subj_clean).strip(' |')
                        
                        # Swap vị trí Giờ và Phòng nếu MyDTU RadScheduler trả Giờ trước Phòng
                        s_parts = [p.strip() for p in subj_clean.split("|") if p.strip()]
                        if len(s_parts) >= 4:
                            if re.search(r'\d{2}:\d{2}', s_parts[2]) and not re.search(r'\d{2}:\d{2}', s_parts[3]):
                                s_parts[2], s_parts[3] = s_parts[3], s_parts[2]
                                subj_clean = " | ".join(s_parts)
                        
                        # Bỏ dấu ngoặc (07:00-09:00) -> 07:00-09:00
                        subj_clean = subj_clean.replace("(", "").replace(")", "")
                        
                        final_raw = prefix + subj_clean
                        if final_raw not in seen_raw and is_valid_schedule_item(final_raw):
                            seen_raw.add(final_raw)
                            new_item = item.copy()
                            new_item["raw_info"] = final_raw
                            cleaned_items.append(new_item)
                    else:
                        parsed_entries = clean_and_parse_schedule_text(raw_str)
                        for entry in parsed_entries:
                            if entry and entry not in seen_raw and is_valid_schedule_item(entry):
                                seen_raw.add(entry)
                                cleaned_items.append({"raw_info": entry})

                items = cleaned_items if cleaned_items else items

                # Tính mã băm SHA256 để kiểm tra thay đổi
                schedule_json_str = json.dumps(items, ensure_ascii=False, sort_keys=True)
                schedule_hash = hashlib.sha256(schedule_json_str.encode("utf-8")).hexdigest()

                result["success"] = True
                result["timetable"] = items
                result["hash"] = schedule_hash
                result["message"] = f"Tải lịch học thành công ({len(items)} dòng)."
                logger.info(f"Cào dữ liệu hoàn tất. Tổng số mục: {len(items)}. Hash: {schedule_hash}")

            except MaintenanceError as me:
                logger.warning(f"Cổng MyDTU đang bảo trì hoặc sao lưu dữ liệu: {me}")
                result["maintenance"] = True
                result["message"] = str(me)
            except PlaywrightTimeoutError as te:
                logger.warning(f"Hết thời gian kết nối tới MyDTU: {te}")
                result["maintenance"] = True
                result["message"] = "Hết thời gian kết nối tới cổng thông tin MyDTU."
            except Exception as e:
                err_lower = str(e).lower()
                if any(k in err_lower for k in ["err_connection_refused", "err_name_not_resolved", "err_connection_timed_out"]):
                    logger.warning(f"⚠️ Cổng MyDTU tạm thời từ chối kết nối/máy chủ sập: {e}")
                    result["maintenance"] = True
                    result["message"] = f"MyDTU ngắt kết nối tạm thời: {e}"
                else:
                    logger.exception("Sự cố xảy ra khi cào thời khóa biểu:")
                    result["message"] = f"Lỗi hệ thống cào dữ liệu: {e}"
            finally:
                await context.close()
                await browser.close()

        return result

async def send_discord_dm_alert(token: str, user_id: str, title: str, description: str, color: int = 0x3498db) -> bool:
    """
    Gửi tin nhắn trực tiếp (Direct Message - DM) qua Discord Bot REST API.
    """
    headers = {
        "Authorization": f"Bot {token.strip()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # Bước 1: Khởi tạo kênh DM cá nhân với người dùng
        dm_url = "https://discord.com/api/v10/users/@me/channels"
        try:
            resp_dm = await client.post(dm_url, json={"recipient_id": user_id.strip()}, headers=headers, timeout=10.0)
            if resp_dm.status_code not in (200, 201):
                logger.error(f"Lỗi khởi tạo kênh DM Discord ({resp_dm.status_code}): {resp_dm.text}")
                return False
            
            dm_data = resp_dm.json()
            channel_id = dm_data.get("id")
            if not channel_id:
                logger.error("Không nhận được ID kênh DM từ Discord API.")
                return False

            # Bước 2: Tách description thành các phần nhỏ (tối đa 4000 ký tự) để không vượt giới hạn Discord
            chunks = []
            if len(description) <= 4000:
                chunks.append(description)
            else:
                lines = description.split('\n')
                current_chunk = ""
                for line in lines:
                    if len(current_chunk) + len(line) + 1 > 4000:
                        chunks.append(current_chunk.strip())
                        current_chunk = line + "\n"
                    else:
                        current_chunk += line + "\n"
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

            msg_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            success_all = True
            
            for i, chunk in enumerate(chunks):
                embed_title = title if i == 0 else f"{title} (Tiếp theo)"
                payload = {
                    "embeds": [
                        {
                            "title": embed_title,
                            "description": chunk,
                            "color": color,
                            "footer": {
                                "text": "ᝰ.ᐟ Tiểu Thanh Thanh ᝰ.ᐟ"
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    ]
                }

                resp_msg = await client.post(msg_url, json=payload, headers=headers, timeout=10.0)
                if resp_msg.status_code in (200, 201):
                    logger.info(f"Đã gửi tin nhắn DM Discord (Phần {i+1}/{len(chunks)}) thành công tới User ID: {user_id}")
                else:
                    logger.error(f"Gửi tin nhắn DM Discord thất bại (Phần {i+1}/{len(chunks)}) ({resp_msg.status_code}): {resp_msg.text}")
                    success_all = False

            return success_all
        except Exception as e:
            logger.error(f"Ngoại lệ xảy ra khi gửi tin nhắn Discord DM: {e}")
            return False

async def send_telegram_alert(token: str, chat_ids: str, message: str):
    """
    Gửi tin nhắn thông báo qua Telegram API (Phương thức dự phòng).
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    list_chat_ids = [cid.strip() for cid in chat_ids.split(",") if cid.strip()]
    
    async with httpx.AsyncClient() as client:
        for chat_id in list_chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    logger.info(f"Đã gửi tin nhắn Telegram thành công tới Chat ID: {chat_id}")
                else:
                    logger.error(f"Gửi tin nhắn Telegram thất bại: {response.text}")
            except Exception as e:
                logger.error(f"Lỗi kết nối Telegram API: {e}")

async def main():
    logger.info("=== Bắt đầu quy trình kiểm tra lịch học ===")
    
    # Kiểm tra khung giờ bảo trì định kỳ của MyDTU (23h00 - 00h00 giờ Việt Nam)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    h_vn = now_vn.hour
    if h_vn == 23:
        logger.info("⏰ [Bảo trì định kỳ] Hiện đang trong khung giờ sao lưu dữ liệu hàng ngày của MyDTU (23:00 - 00:00).")
        logger.info("Bỏ qua lượt quét lịch học này để tiết kiệm tài nguyên và tránh lỗi kết nối.")
        sys.exit(0)
    
    # Kiểm tra cấu hình bắt buộc
    if not all([MYDTU_USER, MYDTU_PASS]):
        logger.error("LỖI CẤU HÌNH: Vui lòng cấu hình đầy đủ MYDTU_USER, MYDTU_PASS trong file .env hoặc GitHub Secrets.")
        sys.exit(1)

    if not GEMINI_API_KEY:
        logger.info("ℹ️ Không tìm thấy GEMINI_API_KEY. Bot sẽ sử dụng ddddocr giải Captcha cục bộ và dùng câu chào mặc định.")

    has_discord = bool(DISCORD_BOT_TOKEN and DISCORD_USER_ID)
    has_telegram = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)

    if not (has_discord or has_telegram):
        logger.error("LỖI CẤU HÌNH: Cần cấu hình (DISCORD_BOT_TOKEN + DISCORD_USER_ID) hoặc (TELEGRAM_TOKEN + TELEGRAM_CHAT_ID).")
        sys.exit(1)

    scraper = DTUScraper()
    res = await scraper.fetch_timetable()

    if res.get("maintenance"):
        logger.info(f"Quy trình quét tạm dừng: {res.get('message')}")
        sys.exit(0)

    if not res.get("success"):
        logger.error(f"Quét lịch học thất bại: {res.get('message')}")
        sys.exit(1)

    new_hash = res.get("hash")
    timetable = res.get("timetable", [])

    # Tên các file lưu trạng thái
    hash_file = "last_hash.txt"
    schedule_file = "last_schedule.json"
    sent_date_file = "last_sent_date.txt"

    # Đọc mã băm cũ
    old_hash = ""
    if os.path.exists(hash_file):
        try:
            with open(hash_file, "r", encoding="utf-8") as f:
                old_hash = f.read().strip()
        except Exception as e:
            logger.warning(f"Không thể đọc file {hash_file}: {e}")

    # Đọc ngày gửi báo cáo gần nhất
    last_sent_date = ""
    if os.path.exists(sent_date_file):
        try:
            with open(sent_date_file, "r", encoding="utf-8") as f:
                last_sent_date = f.read().strip()
        except Exception as e:
            logger.warning(f"Không thể đọc file {sent_date_file}: {e}")

    today_date_key = now_vn.strftime("%Y-%m-%d")

    # Kiểm tra xem có phải lượt chạy thủ công (workflow_dispatch), báo cáo buổi sáng (5h-9h), hoặc FORCE_NOTIFY
    is_manual_trigger = (os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch")
    is_morning_window = (5 <= h_vn <= 9)
    is_morning_report = (is_morning_window and last_sent_date != today_date_key) or (os.getenv("FORCE_NOTIFY", "").lower() == "true") or is_manual_trigger

    # So sánh xem lịch học có thay đổi không (Nếu đã gửi báo cáo ngày hôm nay thì chỉ gửi khi lịch học có thay đổi hoặc kích hoạt thủ công)
    if new_hash == old_hash and not is_morning_report:
        logger.info(f"Lịch học không thay đổi và hôm nay ({today_date_key}) đã gửi báo cáo rồi. Kết thúc quy trình.")
        return

    if is_manual_trigger:
        logger.info("🚀 Kích hoạt gửi báo cáo trực tiếp từ chạy thủ công GitHub Actions!")
    elif is_morning_report:
        logger.info(f"🌅 Kích hoạt gửi báo cáo thời khóa biểu buổi sáng cho Vũ (Ngày {today_date_key})!")
    else:
        logger.info("🚨 PHÁT HIỆN THỜI KHÓA BIỂU MYDTU ĐÃ CÓ THAY ĐỔI!")

    # Lưu lại lịch học mới và ngày gửi báo cáo vào file
    try:
        with open(hash_file, "w", encoding="utf-8") as f:
            f.write(new_hash)
        with open(schedule_file, "w", encoding="utf-8") as f:
            json.dump(timetable, f, ensure_ascii=False, indent=2)
        with open(sent_date_file, "w", encoding="utf-8") as f:
            f.write(today_date_key)
        logger.info("Đã cập nhật mã băm mới, file thời khóa biểu và ngày gửi thông báo.")
    except Exception as e:
        logger.error(f"Lỗi khi lưu dữ liệu lịch học mới vào file: {e}")

    # --- XỬ LÝ VÀ DỰNG TIN NHẮN PHONG CÁCH "TRỢ LÝ CHU ĐÁO" ---
    weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    today_name = weekday_names[now_vn.weekday()]
    today_date_str = now_vn.strftime("%d/%m")
    
    tomorrow_vn = now_vn + timedelta(days=1)
    tomorrow_name = weekday_names[tomorrow_vn.weekday()]
    tomorrow_date_str = tomorrow_vn.strftime("%d/%m")

    is_weekend = now_vn.weekday() >= 5
    default_greeting = "cuối tuần thảnh thơi nhé!" if is_weekend else "chúc cậu một ngày mới vui vẻ và đầy năng lượng nhé!"

    # Lọc danh sách buổi học hôm nay và ngày mai
    today_items = []
    tomorrow_items = []

    for item in timetable:
        raw_txt = item.get("raw_info", "")
        raw_lower = raw_txt.lower()
        if today_name.lower() in raw_lower or now_vn.strftime("%d/%m") in raw_txt or now_vn.strftime("%d-%m") in raw_txt:
            today_items.append(item)
        if tomorrow_name.lower() in raw_lower or tomorrow_vn.strftime("%d/%m") in raw_txt or tomorrow_vn.strftime("%d-%m") in raw_txt:
            tomorrow_items.append(item)

    # 📋 Tổng hợp lịch học cả tuần theo từng Thứ (Sắp xếp theo trình tự thời gian tăng dần từ sáng đến chiều)
    if timetable:
        # Sắp xếp danh sách môn học theo mốc thời gian start_dt
        timetable_sorted = sorted(timetable, key=lambda x: x.get("start_dt", x.get("raw_info", "")))

        grouped_by_day = {}
        for item in timetable_sorted:
            raw_txt = item.get("raw_info", "")
            day_key = "Lịch học khác"
            for wd in ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]:
                if wd.lower() in raw_txt.lower():
                    m_date = re.search(rf'{wd}\s*\(\d{{2}}/\d{{2}}\)', raw_txt, re.IGNORECASE)
                    if m_date:
                        day_key = m_date.group(0)
                    else:
                        day_key = wd
                    break
            
            if day_key not in grouped_by_day:
                grouped_by_day[day_key] = []
            grouped_by_day[day_key].append(item)

        week_blocks = []
        for day_name_key, day_classes in grouped_by_day.items():
            is_today = today_name.lower() in day_name_key.lower() or today_date_str in day_name_key
            header_prefix = "👉 [HÔM NAY] " if is_today else "📌 "
            
            class_lines = []
            # Reset đếm số thứ tự (1, 2, 3...) cho từng Thứ/ngày riêng biệt
            for idx, c_item in enumerate(day_classes, 1):
                c_info = c_item.get("raw_info", "")
                class_lines.append(format_class_item_display(idx, c_info, tag_prefix="  🔹"))
            
            day_block = f"{header_prefix}**{day_name_key}:**\n" + "\n".join(class_lines)
            week_blocks.append(day_block)

        week_summary = "\n\n".join(week_blocks)
    else:
        week_summary = "ℹ️ *Tuần này hiện chưa ghi nhận lịch học nào trên hệ thống.*"

    # --- DỰNG NỘI DUNG THEO 3 TRƯỜNG HỢP ---
    embed_title = "🌸 Thời khoá biểu MyDTU"
    embed_color = 0x3498db  # Mặc định xanh dương
    salutation = get_random_salutation()

    if today_items:
        # TRƯỜNG HỢP 1: Có lịch học hôm nay
        n_items = len(today_items)
        icon_class = "📚" if n_items > 1 else "📌"
        embed_title = f"🌸 Thời khoá biểu MyDTU - Hôm nay có học ({today_date_str})"
        embed_color = 0x3498db  # Xanh dương

        day_status = f"Hôm nay ({today_name}) Vũ có {n_items} môn học trên trường"
        dynamic_greeting = await generate_dynamic_greeting_via_gemini(GEMINI_API_KEY, "Vũ", day_status)
        greeting_text = dynamic_greeting if dynamic_greeting else default_greeting

        today_lines = []
        for idx, it in enumerate(today_items, 1):
            raw_info = it.get('raw_info', '')
            today_lines.append(format_class_item_display(idx, raw_info, icon_class=icon_class))
        today_summary_str = "\n".join(today_lines)

        description = (
            f"{salutation}, {greeting_text}\n\n"
            f"🗓️ **Tớ vừa xem lịch học trên MyDTU mới nhất.** Hôm nay ({today_name}, {today_date_str}) cậu có lịch học trên trường:\n\n"
            f"{today_summary_str}\n\n"
            f"🗓️ **TỔNG HỢP LỊCH HỌC CẢ TUẦN:**\n"
            f"{week_summary}\n\n"
            "⏰ **Vũ nhớ đặt báo thức và check kỹ phòng học để không đi muộn nha!**"
        )

    elif tomorrow_items:
        # TRƯỜNG HỢP 2: Hôm nay nghỉ, mai có học
        embed_title = f"🌸 Thời khoá biểu MyDTU - Hôm nay nghỉ, mai có học ({tomorrow_date_str})"
        embed_color = 0xe67e22  # Cam

        day_status = f"Hôm nay ({today_name}) Vũ được nghỉ học xả hơi, nhưng mai ({tomorrow_name}) có môn học"
        dynamic_greeting = await generate_dynamic_greeting_via_gemini(GEMINI_API_KEY, "Vũ", day_status)
        greeting_text = dynamic_greeting if dynamic_greeting else default_greeting

        tomorrow_lines = []
        tomorrow_subjects = []
        for idx, it in enumerate(tomorrow_items, 1):
            raw_info = it.get('raw_info', '')
            tomorrow_lines.append(format_class_item_display(idx, raw_info, tag_prefix="📌"))
            parts = [p.strip() for p in raw_info.split("|") if p.strip()]
            if len(parts) >= 2:
                tomorrow_subjects.append(parts[1])
            else:
                tomorrow_subjects.append(raw_info)

        tomorrow_summary_str = "\n".join(tomorrow_lines)
        subject_name_str = ", ".join(tomorrow_subjects) if tomorrow_subjects else "học"

        description = (
            f"{salutation}, {greeting_text}\n\n"
            f"🗓️ **Tớ vừa xem lịch học trên MyDTU mới nhất.** Hôm nay ({today_date_str}) cậu KHÔNG CÓ LỊCH HỌC trên trường.\n\n"
            f"🛌 **Hôm nay xả hơi, nhưng mai ({tomorrow_name}, {tomorrow_date_str}) là có môn {subject_name_str} rồi đấy nhé!**\n\n"
            f"📌 **Chi tiết lịch học ngày mai:**\n"
            f"{tomorrow_summary_str}\n\n"
            f"🗓️ **TỔNG HỢP LỊCH HỌC CẢ TUẦN:**\n"
            f"{week_summary}\n\n"
            "🔔 **Có thay đổi gì về lịch tớ sẽ hú cậu ngay!**"
        )

    else:
        # TRƯỜNG HỢP 3: Hôm nay nghỉ & mai không có học / Nghỉ cả tuần
        embed_title = f"🌸 Thời khoá biểu MyDTU - Nghỉ học ({today_date_str})"
        embed_color = 0x2ecc71  # Xanh lá

        day_status = f"Hôm nay ({today_name}) và cả tuần này Vũ được nghỉ học trên trường, rảnh rỗi nghỉ ngơi"
        dynamic_greeting = await generate_dynamic_greeting_via_gemini(GEMINI_API_KEY, "Vũ", day_status)
        greeting_text = dynamic_greeting if dynamic_greeting else default_greeting

        if not timetable:
            description = (
                f"{salutation}, {greeting_text}\n\n"
                f"🗓️ **Tớ vừa xem lịch học trên MyDTU mới nhất.** Hôm nay ({today_date_str}) và cả tuần này cậu không có lịch học trên trường.\n\n"
                f"🛌 **Tranh thủ thời gian này để nghỉ ngơi, nạp lại năng lượng hoặc chạy deadline bài tập cá nhân nha. Có thay đổi gì về lịch tớ sẽ hú cậu ngay!**"
            )
        else:
            description = (
                f"{salutation}, {greeting_text}\n\n"
                f"🗓️ **Tớ vừa xem lịch học trên MyDTU mới nhất.** Hôm nay ({today_date_str}) và ngày mai cậu không có lịch học trên trường.\n\n"
                f"🛌 **Tranh thủ thời gian này để nghỉ ngơi, nạp lại năng lượng hoặc chạy deadline bài tập cá nhân nha.**\n\n"
                f"🗓️ **TỔNG HỢP LỊCH HỌC CÁC NGÀY TIẾP THEO:**\n"
                f"{week_summary}\n\n"
                f"🔔 **Có thay đổi gì về lịch tớ sẽ hú cậu ngay!**"
            )

    # --- GỬI THÔNG BÁO ---
    if has_discord:
        await send_discord_dm_alert(
            token=DISCORD_BOT_TOKEN,
            user_id=DISCORD_USER_ID,
            title=embed_title,
            description=description,
            color=embed_color
        )

    if has_telegram:
        # Telegram gửi định dạng Markdown plain text
        tele_text = f"*{embed_title}*\n\n{description}"
        await send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, tele_text)

    logger.info("=== Hoàn tất quy trình phát hiện thay đổi và gửi cảnh báo ===")

if __name__ == "__main__":
    asyncio.run(main())

