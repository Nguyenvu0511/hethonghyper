# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime

with open('src/scraper/mydtu_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

func = '''
def extract_radscheduler_appointments(page_content: str):
    import re, json
    from datetime import datetime
    weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    items = []
    app_matches = re.findall(r'\\"appointments\\"\\s*:\\s*\\"(\\[.*?\\])\\"', page_content)
    for match_str in app_matches:
        try:
            cleaned_json = match_str.replace(r'\\"', '"').replace(r'\\\\', '\\\\')
            app_list = json.loads(cleaned_json)
            for app in app_list:
                subj = app.get("subject", "").strip()
                start_str = app.get("start", "").strip()
                if subj and start_str:
                    try:
                        dt = datetime.strptime(start_str, "%Y/%m/%d %H:%M")
                        wd_name = weekday_names[dt.weekday()]
                        date_str = dt.strftime("%d/%m")
                        parts = [p.strip() for p in subj.split('|') if p.strip()]
                        if len(parts) >= 4:
                            if re.search(r'\\d{2}:\\d{2}', parts[2]) and not re.search(r'\\d{2}:\\d{2}', parts[3]):
                                parts[2], parts[3] = parts[3], parts[2]
                        subj_clean = " | ".join(parts).replace("(", "").replace(")", "")
                        raw_info = f"{wd_name} ({date_str}) | {subj_clean}"
                        items.append({"raw_info": raw_info, "start_dt": dt.isoformat()})
                    except Exception:
                        pass
        except Exception:
            pass
    items.sort(key=lambda x: x.get("start_dt", ""))
    return items

async def crawl_timetable(username: str = MYDTU_USER, password: str = MYDTU_PASS, gemini_key: str = GEMINI_CAPTCHA_API_KEY):
    if not username or not password: return []
    logger.info("=== QUÉT LỊCH HỌC MYDTU ===")
    TIMETABLE_URL = "https://mydtu.duytan.edu.vn/sites/index.aspx?p=home_timetable&functionid=13"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        try:
            await page.goto(LOGIN_URL, wait_until="load", timeout=40000)
            logged_in = False
            for attempt in range(1, 10):
                await page.fill("input#txtUser", username)
                await page.fill("input#txtPass", password)
                base64_str = await get_captcha_base64_from_canvas(page)
                if not base64_str: break
                captcha_bytes = base64.b64decode(base64_str)
                try:
                    captcha_code = await solve_captcha(image_bytes=captcha_bytes, api_key=gemini_key)
                    if len(captcha_code) != 4:
                        await page.reload(wait_until="load")
                        continue
                except:
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
            
            if not logged_in: return []
            
            await page.goto(TIMETABLE_URL, wait_until="domcontentloaded", timeout=40000)
            try:
                await page.wait_for_selector(".rsApt, [id*='RadScheduler']", timeout=20000)
                await asyncio.sleep(3)
            except: pass
            
            page_content = await page.content()
            items = extract_radscheduler_appointments(page_content)
            
            if items:
                import os
                if not os.path.exists("data"):
                    os.makedirs("data")
                with open("data/last_schedule.json", "w", encoding="utf-8") as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
            
            return items
        except Exception as e:
            logger.exception(f"Lỗi quét lịch học: {e}")
            return []
        finally:
            await context.close()
            await browser.close()
'''
if 'async def crawl_timetable' not in content:
    content += '\n' + func

with open('src/scraper/mydtu_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)