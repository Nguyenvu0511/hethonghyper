# 🤖 Bot Quét Lịch Học MyDTU - Thông Báo Discord DM & Trợ Lý AI Chu Đáo

Hệ thống quét thời khóa biểu MyDTU tự động hoạt động trên đám mây bằng **GitHub Actions** (miễn phí 100%, không cần cắm máy). 

Bot tự động đăng nhập MyDTU, tự giải Captcha bằng **Google Gemini AI**, phân tích lịch học và gửi tin nhắn **trực tiếp (Direct Message - DM)** tới tài khoản Discord cá nhân của bạn với giao diện **Discord Rich Embed** đẹp mắt, đi kèm **lời chúc động lực độc đáo thay đổi mỗi ngày** do AI sáng tạo riêng cho bạn (**Vũ**).

---

## 🌟 Tính Năng Nổi Bật

- 📩 **Thông báo riêng tư qua Discord DM**: Gửi tin nhắn riêng (Direct Message) trực tiếp vào tài khoản Discord của Vũ, không cần đăng bài công khai trên kênh máy chủ.
- 🎨 **Giao diện Discord Rich Embed siêu đẹp**: Tự động đổi màu khung Embed theo từng trường hợp (Xanh dương - Có học hôm nay / Cam - Mai có học / Xanh lá - Được nghỉ).
- 🧠 **Google Gemini AI linh hoạt**:
  - Tự động vượt Captcha hình ảnh đăng nhập MyDTU chính xác (`gemini-flash-latest`).
  - Sáng tạo **lời chúc ngắn gọn, mới mẻ và truyền cảm hứng** mỗi ngày cho **Vũ** (xưng *"tớ"*, gọi *"Vũ"* hoặc *"cậu"*), tuyệt đối không trùng lặp hay sáo rỗng.
- 🏫 **Tự động phân loại 3 hình thức học MyDTU**:
  - 🏫 **`[HỌC TẠI TRƯỜNG]`**: Học trực tiếp tại phòng học trên cơ sở trường.
  - 💻🏠 **`[ONLINE TẠI NHÀ (GV ở trường)]`**: Lớp học Tập Trung & Trực Tuyến (Giảng viên dạy ở phòng tại trường, Sinh viên học Online ở nhà).
  - 💻 **`[ONLINE TẠI NHÀ]`**: Học trực tuyến/online hoàn toàn (Zoom, MS Teams, LMS).
- 🔄 **Chạy hoàn toàn tự động trên GitHub Actions**:
  - Báo cáo định kỳ lúc **5h00 sáng hàng ngày** (giờ Việt Nam).
  - Quét ngầm **5 tiếng/lần** để phát hiện thay đổi lịch tức thì từ nhà trường.
  - Tự động ngắt trong khung giờ bảo trì của MyDTU (23h00 - 00h00).

---

## ⚙️ HƯỚNG DẪN CẤU HÌNH CHI TIẾT TỪ A ĐẾN Z

Nếu sau này bạn cần cài đặt lại từ đầu, hãy làm lần lượt theo 6 bước cặn kẽ dưới đây:

### 📌 Bước 1: Tạo Discord Bot & Lấy Token
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications).
2. Bấm nút **Tạo ứng dụng mới** (*New Application*) ➔ Nhập tên (ví dụ: `Trợ Lý MyDTU`) ➔ Bấm **Tạo** (*Create*).
3. Ở menu cột bên trái, chọn mục **Bot** (biểu tượng đầu robot 🤖):
   - Bấm **Đặt lại Token** (*Reset Token*) ➔ Chọn **Có, làm đi!** (*Yes, do it!*).
   - Bấm **Sao chép** (*Copy*) để lấy mã `DISCORD_BOT_TOKEN` *(Lưu lại mã này)*.
4. **Mời Bot vào máy chủ** *(Bắt buộc để Discord cấp quyền cho Bot nhắn DM riêng cho bạn)*:
   - Ở menu bên trái, chọn **OAuth2** ➔ chọn **Trình tạo URL** (*URL Generator*).
   - Ở mục **Phạm vi** (*Scopes*): Tích chọn ô `bot`.
   - Ở bảng **Quyền hạn của Bot** (*Bot Permissions*): Tích chọn ô `Send Messages` (Gửi tin nhắn).
   - Cuộn xuống dưới cùng, bấm nút **Sao chép** (*Copy*) đường link URL.
   - Dán link đó vào trình duyệt ➔ Chọn máy chủ Discord của bạn ➔ Bấm **Phê duyệt** (*Authorize*) để mời bot vào.

---

### 📌 Bước 2: Lấy Discord User ID Cá Nhân
1. Mở ứng dụng Discord trên máy tính hoặc điện thoại.
2. Vào **Cài đặt người dùng (⚙️ Bánh răng)** ➔ Chọn mục **Nâng cao** (*Advanced*) ➔ Bật công tắc **Chế độ nhà phát triển** (*Developer Mode*).
3. Nhấn chuột phải vào **Tên / Avatar cá nhân** của bạn (ở góc dưới bên trái màn hình) ➔ Chọn **Sao chép ID người dùng** (*Copy User ID*).
4. Lưu lại chuỗi số này làm `DISCORD_USER_ID` (ví dụ: `897419519943905281`).

---

### 📌 Bước 3: Lấy Google Gemini API Key
1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Đăng nhập bằng tài khoản Google ➔ Bấm **Create API Key**.
3. Sao chép chuỗi API Key vừa tạo làm `GEMINI_API_KEY`.

---

### 📌 Bước 4: Đẩy Mã Nguồn Lên GitHub Repository
Mở Terminal / Command Prompt tại thư mục dự án này và chạy các lệnh:

```bash
# Khởi tạo git (nếu chưa có)
git init
git branch -M main

# Trỏ tới Repository của bạn trên GitHub
git remote add origin https://github.com/Nguyenvu0511/bot-lich-discord.git

# Hoặc nếu đã có remote cũ, cập nhật URL mới:
# git remote set-url origin https://github.com/Nguyenvu0511/bot-lich-discord.git

# Đẩy code lên GitHub
git add .
git commit -m "Cập nhật Bot Lịch Học Discord DM + Gemini AI Greetings"
git push -u origin main
```

---

### 📌 Bước 5: Cấu Hình Secrets Trên GitHub Repository
1. Truy cập vào Repository của bạn: `https://github.com/Nguyenvu0511/bot-lich-discord`.
2. Vào **Settings** ➔ Chọn **Secrets and variables** (ở cột bên trái) ➔ Chọn **Actions**.
3. Bấm nút **New repository secret** và lần lượt thêm **5 bí mật** sau:

| Tên Secret | Giá trị (Value) | Mô tả |
| :--- | :--- | :--- |
| `MYDTU_USER` | *(Tên đăng nhập MyDTU)* | Mã sinh viên / Mã đăng nhập MyDTU |
| `MYDTU_PASS` | *(Mật khẩu MyDTU)* | Mật khẩu tài khoản MyDTU |
| `GEMINI_API_KEY` | *(API Key ở Bước 3)* | Key của Google Gemini AI |
| `DISCORD_BOT_TOKEN` | *(Bot Token ở Bước 1)* | Token của Discord Bot |
| `DISCORD_USER_ID` | *(User ID ở Bước 2)* | ID tài khoản Discord nhận tin nhắn DM |

---

### 📌 Bước 6: Cấp Quyền & Kích Hoạt Chạy Tự Động
1. Trong tab **Settings** của Repo trên GitHub ➔ Chọn **Actions** ➔ **General**.
2. Cuộn xuống mục **Workflow permissions** ➔ Chọn ô **Read and write permissions**.
3. Bấm **Save**.

**🧪 Kiểm thử chạy thử ngay:**
- Chuyển sang tab **Actions** trên GitHub ➔ Click chọn workflow **Quét Lịch Học MyDTU Định Kỳ**.
- Bấm nút **Run workflow** ➔ Chọn nhánh `main` ➔ Bấm **Run workflow** màu xanh để kích hoạt chạy ngay lập tức.
- Bot sẽ gửi tin nhắn DM thử nghiệm trực tiếp vào Discord của bạn!

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
├── .github/workflows/
│   └── quet_lich_hoc.yml    # Định nghĩa lịch chạy ngầm GitHub Actions (5h00 sáng & 5 tiếng/lần)
├── check_schedule.py        # Core Python script (Playwright cào dữ liệu, Gemini AI, Discord DM REST API)
├── last_hash.txt            # Lưu mã băm SHA256 để so sánh sự thay đổi thời khóa biểu
├── last_schedule.json       # Lưu chi tiết lịch học gần nhất
├── requirements.txt         # Thư viện Python (httpx, playwright, python-dotenv)
├── .env                     # File cấu hình biến môi trường khi chạy cục bộ
├── .gitignore               # Loại bỏ file tạm và .env khỏi Git
└── README.md                # Tài liệu hướng dẫn chi tiết từ A đến Z
```

---

## 💻 Chạy Cục Bộ (Local Testing)

Nếu muốn chạy thử nghiệm trực tiếp trên máy tính cá nhân:

1. Tạo file `.env` tại thư mục gốc với nội dung:
```env
MYDTU_USER=taikhoan_mydtu
MYDTU_PASS=matkhau_mydtu
GEMINI_API_KEY=AIzaSy...
DISCORD_BOT_TOKEN=MTUz...
DISCORD_USER_ID=897419519943905281
```

2. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

3. Thực thi script:
```bash
python check_schedule.py
```

---

## 📄 Giấy Phép
Dự án mã nguồn mở phục vụ mục đích cá nhân và hỗ trợ học tập cho sinh viên Đại học Duy Tân (DTU).
