# Hướng Dẫn Triển Khai (Deploy) Bot Lên VPS Ubuntu 24.04 Từ A-Z

Tớ đã đẩy toàn bộ mã nguồn của chúng ta lên GitHub của cậu thành công tại: `https://github.com/Nguyenvu0511/hethonghyper.git`. (Đã giấu đi các file chứa API Key để bảo mật).

Dưới đây là hướng dẫn **Cầm tay chỉ việc** để cậu tự mình dựng cơ đồ trên VPS. Hãy copy từng dòng lệnh và dán vào cửa sổ SSH của VPS nhé!

---

## Bước 1: Kết nối và Cập nhật VPS
Mở Terminal (Mac/Linux) hoặc Command Prompt/PowerShell (Windows) và gõ:
```bash
ssh root@<địa-chỉ-IP-VPS-của-cậu>
```
Sau khi đăng nhập thành công, hãy cập nhật toàn bộ hệ điều hành:
```bash
sudo apt update && sudo apt upgrade -y
```

## Bước 2: Tải Mã nguồn từ GitHub về VPS
Cài đặt Git, Python và tải mã nguồn về:
```bash
sudo apt install git python3 python3-pip python3-venv -y
git clone https://github.com/Nguyenvu0511/hethonghyper.git
cd hethonghyper
```

## Bước 3: Phục hồi "Linh hồn" cho Bot (Tệp .env)
Do lý do bảo mật, file `.env` (chứa API Key) và `API_KEYS.txt` không được đẩy lên GitHub. Cậu phải tạo lại nó trên VPS:
```bash
nano .env
```
Sau đó copy nội dung y hệt file `.env` ở máy tính hiện tại của cậu dán vào cửa sổ này (Chứa `TELEGRAM_BOT_TOKEN`, `MYDTU_USER`, `MYDTU_PASS`, `GEMINI_CAPTCHA_API_KEY`).
Ấn `Ctrl + O` -> `Enter` để lưu. Ấn `Ctrl + X` để thoát nano.

(Nếu hệ thống của cậu dùng thêm `API_KEYS.txt`, hãy tạo nó tương tự bằng lệnh `nano API_KEYS.txt`).

## Bước 4: Cài đặt Môi trường & Thư viện
Tạo môi trường ảo Python và cài đặt các thư viện cần thiết:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Cài đặt Trình duyệt ảo cho Điệp viên Playwright:
```bash
playwright install-deps
playwright install chromium
```

## Bước 5: Tạo Dịch vụ Chạy Ngầm Bất Tử (Systemd)
Cậu không thể gõ `python main_bot.py` rồi tắt máy được. Chúng ta phải cài nó thành dịch vụ hệ thống.
Tạo file cấu hình:
```bash
sudo nano /etc/systemd/system/mydtu_bot.service
```
Dán y nguyên đoạn này vào (Chú ý: Đường dẫn `/root/hethonghyper` nếu cậu cài ở thư mục root):
```ini
[Unit]
Description=MyDTU Kỷ Luật Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/hethonghyper
Environment="PATH=/root/hethonghyper/venv/bin"
Environment="PYTHONPATH=/root/hethonghyper"
ExecStart=/root/hethonghyper/venv/bin/python -m src.bot.main_bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Lưu (`Ctrl + O` -> `Enter`) và thoát (`Ctrl + X`).

## Bước 6: Kích hoạt & Khởi động Bot
```bash
sudo systemctl daemon-reload
sudo systemctl enable mydtu_bot
sudo systemctl start mydtu_bot
```

> [!TIP] 
> **Cách kiểm tra Bot có đang chạy tốt không:**
> Gõ lệnh sau để xem log trực tiếp của Bot:
> ```bash
> sudo journalctl -u mydtu_bot -f
> ```
> (Bấm `Ctrl + C` để thoát màn hình xem log).

## Hướng dẫn Vận hành sau này
Nếu sau này cậu nhờ tớ code thêm tính năng mới (Ví dụ: Chặn TikTok bằng Pi-hole) ở máy tính cá nhân. Cậu chỉ cần cập nhật VPS bằng 2 lệnh cực dễ:
1. Đăng nhập VPS, vào thư mục: `cd hethonghyper`
2. Kéo code mới và khởi động lại Bot: 
```bash
git pull origin main
sudo systemctl restart mydtu_bot
```

XONG! Vậy là cậu đã chính thức sở hữu một con Bot chạy ngầm vĩnh viễn trên Đám mây. Bắt tay vào làm theo các bước này đi, vướng ở đâu thì copy màn hình lỗi ném vào đây cho tớ xử lý!
