import asyncio, base64, httpx
from playwright.async_api import async_playwright
async def solve_captcha_gemini(base64_image: str, api_key: str) -> str:
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}'
    payload = {'contents': [{'parts': [{'text': 'Read the text in this CAPTCHA image. Return ONLY the uppercase letters and numbers. No spaces or extra text.'}, {'inline_data': {'mime_type': 'image/png', 'data': base64_image}}]}]}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=20.0)
        return res.json()['candidates'][0]['content']['parts'][0]['text'].strip().replace(' ', '').replace('\n', '').upper()
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        await page.goto('https://mydtu.duytan.edu.vn/Signin.aspx', wait_until='load')
        await page.fill('input#txtUser', 'nguyenhoangvu24')
        await page.fill('input#txtPass', 'Trong08051985@')
        captcha_el = await page.query_selector('#UpdatePanel1 img, img[src*=\"CaptchaImage.axd\"]')
        captcha_bytes = await captcha_el.screenshot()
        base64_img = base64.b64encode(captcha_bytes).decode('utf-8')
        captcha_code = await solve_captcha_gemini(base64_img, 'AQ.Ab8RN6KE5Z7wSHNNFp-GBMuG2nAHrJxaeika2_2B7wUjkVxb9Q')
        await page.fill('input#txtCaptcha', captcha_code)
        await page.click('input#btnLogin1')
        await page.wait_for_url('**/index.aspx*', timeout=15000)
        await page.goto('https://mydtu.duytan.edu.vn/Modules/portal/ajax/TopMenuList.aspx', wait_until='domcontentloaded')
        html = await page.content()
        with open('menu_dump.html', 'w', encoding='utf-8') as f:
            f.write(html)
        await browser.close()
asyncio.run(main())
