import os
import sys
import json
import base64
import asyncio
import logging
import httpx
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Đảm bảo hiển thị Tiếng Việt trên Windows Terminal
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Tải cấu hình từ file .env hoặc API_KEYS.txt
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(__file__), "../..", "API_KEYS.txt"))
except ImportError:
    pass

# Cấu hình Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("MyDTUScoreCrawler")

# Lấy biến môi trường tài khoản
MYDTU_USER = os.getenv("MYDTU_USER", "")
MYDTU_PASS = os.getenv("MYDTU_PASS", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_CAPTCHA_API_KEY = os.getenv("GEMINI_CAPTCHA_API_KEY", GEMINI_API_KEY)

LOGIN_URL = "https://mydtu.duytan.edu.vn/Signin.aspx"
TRANSCRIPT_URL = "https://mydtu.duytan.edu.vn/sites/index.aspx?p=home_bangdiem&functionid=14"


async def solve_captcha_gemini(base64_image: str, api_key: str) -> str:
    """
    Gửi ảnh Captcha dạng Base64 lên Google Gemini API để giải mã tự động.
    """
    model_name = "gemini-3.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [
                {"text": "Read the text in this CAPTCHA image. Return ONLY the uppercase letters and numbers. No spaces or extra text."},
                {"inline_data": {"mime_type": "image/png", "data": base64_image}}
            ]
        }]
    }

    async with httpx.AsyncClient() as client:
        import asyncio
        max_retries = 4
        for attempt in range(max_retries):
            res = await client.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20.0)
            if res.status_code == 429 and attempt < max_retries - 1:
                logger.warning(f"Bị giới hạn API giải Captcha (429). Đợi 30s... (Lần {attempt+1}/{max_retries})")
                await asyncio.sleep(30)
                continue
            
            data = res.json()
            if "candidates" in data and data["candidates"]:
                code = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return code.replace(" ", "").replace("\n", "").upper()
            else:
                raise Exception(f"Gemini API Error: {data.get('error', 'Unknown error')}")


async def crawl_student_scores(username: str = MYDTU_USER, password: str = MYDTU_PASS, gemini_key: str = GEMINI_CAPTCHA_API_KEY):
    """
    MÃ NGUỒN TỰ ĐỘNG ĐĂNG NHẬP TRƯỜNG DUY TÂN (MYDTU) & QUÉT BẢNG ĐIỂM SỐ CỤ THỂ.
    """
    if not username or not password or not gemini_key:
        logger.error("Vui lòng cấu hình MYDTU_USER, MYDTU_PASS và GEMINI_API_KEY trong tệp .env!")
        return None

    logger.info("=== BẮT ĐẦU QUY TRÌNH ĐĂNG NHẬP MYDTU VÀ QUÉT ĐIỂM SỐ ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Điều hướng tới trang đăng nhập
            logger.info(f"1. Đang mở trang đăng nhập MyDTU: {LOGIN_URL}")
            await page.goto(LOGIN_URL, wait_until="load", timeout=40000)

            # Ẩn quảng cáo
            await page.add_style_tag(content=".darkness, #popout, #adbox { display: none !important; }")

            # 2. Thực hiện đăng nhập (thử 3 lần nếu sai Captcha)
            logged_in = False
            for attempt in range(1, 4):
                logger.info(f"-> Thử đăng nhập lần {attempt}/3...")

                await page.fill("input#txtUser", username)
                await page.fill("input#txtPass", password)

                captcha_el = await page.query_selector('#UpdatePanel1 img, img[src*="CaptchaImage.axd"]')
                if not captcha_el:
                    logger.error("Không thấy thẻ Captcha!")
                    break

                captcha_bytes = await captcha_el.screenshot()
                base64_img = base64.b64encode(captcha_bytes).decode('utf-8')

                try:
                    captcha_code = await solve_captcha_gemini(base64_img, gemini_key)
                    logger.info(f"   AI giải Captcha thành công: {captcha_code}")
                except Exception as ge:
                    logger.warning(f"   AI giải Captcha thất bại: {ge}")
                    await page.reload(wait_until="load")
                    continue

                await page.fill("input#txtCaptcha", captcha_code)
                await page.click("input#btnLogin1")

                try:
                    await page.wait_for_url("**/index.aspx*", timeout=15000)
                    logged_in = True
                    logger.info("2. ĐĂNG NHẬP MYDTU THÀNH CÔNG!")
                    break
                except PlaywrightTimeoutError:
                    logger.warning("   Đăng nhập chưa thành công (Sai captcha/mật khẩu). Đang thử lại...")
                    await page.goto(LOGIN_URL, wait_until="load", timeout=20000)

            if not logged_in:
                logger.error("Không thể đăng nhập vào cổng MyDTU trường bạn.")
                return None

            # 3. Chuyển hướng tới trang Bảng điểm / Điểm số cụ thể
            logger.info(f"3. Đang chuyển hướng sang trang Điểm Số Cụ Thể: {TRANSCRIPT_URL}")
            await page.goto(TRANSCRIPT_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # 4. Trích xuất bảng điểm từ HTML của trường
            logger.info("4. Đang phân tích dữ liệu bảng điểm...")
            await page.screenshot(path="debug_transcript.png", full_page=True)
            html = await page.content()
            with open("debug_transcript.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            extracted_scores = []
            
            # Quét tất cả các hàng trong bảng điểm
            rows = await page.query_selector_all("table tr")
            for row in rows:
                row_text = await row.inner_text()
                if not row_text:
                    continue
                
                # Tách text theo dòng hoặc tab
                cells = [c.strip() for c in row_text.replace('\t', '\n').split('\n') if c.strip()]
                if not cells:
                    continue
                    
                mamon = cells[0]
                if len(mamon) >= 3 and any(char.isdigit() for char in mamon) and "Tổng số" not in mamon:
                    # Tìm index của từ khóa 'Tín Chỉ' hoặc 'Tín chỉ'
                    tc_idx = -1
                    for i, c in enumerate(cells):
                        if "Tín Chỉ" in c or "Tín chỉ" in c:
                            tc_idx = i
                            break
                    
                    if tc_idx != -1 and tc_idx >= 2:
                        tenmon = cells[tc_idx - 2]
                        tinchi = cells[tc_idx - 1]
                        
                        diem_tongket = "Chưa có"
                        diem_chu = "Chưa có"
                        
                        if len(cells) > tc_idx + 1:
                            diem_tongket = cells[tc_idx + 1]
                        if len(cells) > tc_idx + 2:
                            diem_chu = cells[tc_idx + 2]

                        extracted_scores.append({
                            "ma_mon": mamon,
                            "ten_mon": tenmon,
                            "so_tin_chi": tinchi,
                            "diem_tong_ket": diem_tongket,
                            "diem_chu": diem_chu
                        })

            # 5. Lưu kết quả ra file JSON
            output_file = "scores_output.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(extracted_scores, f, ensure_ascii=False, indent=2)

            logger.info(f"=== HOÀN THÀNH: Đã quét {len(extracted_scores)} môn học và lưu vào {output_file} ===")
            return extracted_scores

        except Exception as e:
            logger.exception(f"Lỗi xảy ra trong quá trình cào điểm: {e}")
            return None
        finally:
            await context.close()
            await browser.close()

async def crawl_new_announcements(username: str = MYDTU_USER, password: str = MYDTU_PASS, gemini_key: str = GEMINI_CAPTCHA_API_KEY):
    """
    Quét thông báo mới (có icon Mới) từ MyDTU.
    Trả về list dictionary: [{'id': '573', 'title': '...', 'content': '...', 'url': '...'}]
    """
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse, parse_qs
    
    if not username or not password or not gemini_key:
        logger.error("Vui lòng cấu hình MYDTU_USER, MYDTU_PASS và GEMINI_API_KEY trong tệp .env!")
        return None

    logger.info("=== BẮT ĐẦU QUY TRÌNH ĐĂNG NHẬP MYDTU & QUÉT THÔNG BÁO ===")
    
    ANNOUNCEMENT_URL = "https://mydtu.duytan.edu.vn/sites/index.aspx?p=home_announcements&functionid=11"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Đăng nhập
            logger.info(f"1. Đang mở trang đăng nhập MyDTU: {LOGIN_URL}")
            await page.goto(LOGIN_URL, wait_until="load", timeout=40000)
            await page.add_style_tag(content=".darkness, #popout, #adbox { display: none !important; }")

            logged_in = False
            for attempt in range(1, 4):
                await page.fill("input#txtUser", username)
                await page.fill("input#txtPass", password)

                captcha_el = await page.query_selector('#UpdatePanel1 img, img[src*="CaptchaImage.axd"]')
                if not captcha_el:
                    break

                captcha_bytes = await captcha_el.screenshot()
                base64_img = base64.b64encode(captcha_bytes).decode('utf-8')

                try:
                    captcha_code = await solve_captcha_gemini(base64_img, gemini_key)
                except Exception:
                    await page.reload(wait_until="load")
                    continue

                await page.fill("input#txtCaptcha", captcha_code)
                await page.click("input#btnLogin1")

                try:
                    await page.wait_for_url("**/index.aspx*", timeout=15000)
                    logged_in = True
                    break
                except PlaywrightTimeoutError:
                    await page.goto(LOGIN_URL, wait_until="load", timeout=20000)

            if not logged_in:
                logger.error("Không thể đăng nhập vào cổng MyDTU.")
                return None

            # Quét thông báo
            logger.info(f"3. Đang chuyển hướng sang trang Thông báo: {ANNOUNCEMENT_URL}")
            await page.goto(ANNOUNCEMENT_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            h3_tags = soup.find_all('h3')
            
            new_items = []
            from src.database.db_manager import db
            
            for h3 in h3_tags:
                if h3.find('img', src="../../../images/icon-new.gif"):
                    a_tag = h3.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        # Extract idann from URL
                        parsed_url = urlparse(href)
                        query_params = parse_qs(parsed_url.query)
                        if 'idann' in query_params:
                            idann = query_params['idann'][0]
                            title = a_tag.text.strip()
                            
                            # Check database
                            if not db.is_announcement_seen(idann):
                                # Limit to max 5 new announcements per crawl to avoid spamming/taking too long
                                if len(new_items) >= 5:
                                    break
                                    
                                logger.info(f"Phát hiện thông báo mới: {title} (ID: {idann})")
                                
                                # Lấy nội dung chi tiết
                                detail_url = "https://mydtu.duytan.edu.vn/sites/" + href
                                new_page = await context.new_page()
                                await new_page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                                detail_html = await new_page.content()
                                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                                
                                content_div = detail_soup.find('div', class_='content-thongbao')
                                full_text = content_div.text.strip() if content_div else "Không thể tải nội dung chi tiết."
                                
                                new_items.append({
                                    'id': idann,
                                    'title': title,
                                    'content': full_text,
                                    'url': detail_url
                                })
                                await new_page.close()
                                await asyncio.sleep(1)

            logger.info(f"=== Đã quét xong. Có {len(new_items)} thông báo mới cần gửi ===")
            return new_items

        except Exception as e:
            logger.exception(f"Lỗi xảy ra trong quá trình quét thông báo: {e}")
            return None
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    scores = asyncio.run(crawl_student_scores())
    if scores:
        print("\n📊 --- KẾT QUẢ ĐIỂM SỐ CỦA BẠN TRÊN MYDTU ---")
        for idx, item in enumerate(scores, 1):
            print(f"{idx}. [{item['ma_mon']}] {item['ten_mon']} - Số TC: {item['so_tin_chi']} | Điểm TK: {item['diem_tong_ket']} | Điểm chữ: {item['diem_chu']}")
