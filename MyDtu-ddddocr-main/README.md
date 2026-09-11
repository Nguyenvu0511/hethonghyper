# MyDTU Auto-Login with Local AI (ddddocr) 🚀

Dự án này là một tiện ích mở rộng (Chrome/Edge Extension) giúp tự động vượt qua mã Captcha và tự động đăng nhập vào cổng thông tin MyDTU của Đại học Duy Tân. Nó sử dụng một Server cục bộ chạy trí tuệ nhân tạo (AI) `ddddocr` để giải mã Captcha với độ chính xác cao.

## 🌟 Tính năng nổi bật
- **Vượt Captcha chuẩn xác:** Tích hợp mô hình CNN của `ddddocr` - giải mã cực kỳ chính xác các loại Captcha nhiễu, gạch chéo.
- **Tự động 100%:** Chỉ cần lưu tài khoản/mật khẩu, Extension sẽ tự động điền thông tin, tự động gửi Captcha cho AI giải và tự động bấm Đăng nhập.
- **Xử lý Vòng lặp:** Nếu Captcha quá mờ khiến AI đọc sai, web tự tải lại, Extension sẽ tiếp tục tự động vòng lặp cho đến khi vào được web (thường là thành công ở lần 1 hoặc 2).
- **Tránh dính Mixed Content:** Extension được thiết kế chuẩn MV3, sử dụng `background.js` (Service Worker) để làm cầu nối gửi ảnh đến Server HTTP ở Localhost một cách an toàn mà không bị trình duyệt chặn.
- **Bảo mật tuyệt đối:** Tài khoản và mật khẩu chỉ được lưu trên chính trình duyệt của bạn thông qua `chrome.storage.sync`. AI giải mã cũng chạy ngay trên máy tính của bạn, không lo lộ dữ liệu ra bên ngoài.

---

## 🏗️ Kiến trúc Hệ thống

Dự án này được chia làm 2 thành phần hoạt động song song (Client - Server):

### 1. Client (Chrome Extension)
Là phần giao diện và logic chạy trên trình duyệt.
- **`content.js`:** Được tiêm (inject) vào trang web MyDTU. Nhiệm vụ của nó là ẩn giao diện thừa, bắt hình ảnh Captcha `<canvas>`, chuyển nó thành định dạng Base64 (PNG không nén) và bắn tin nhắn cho `background.js`. Nó cũng chịu trách nhiệm điền tài khoản và click nút Đăng nhập.
- **`background.js`:** Là cầu nối (Service Worker). Nhận Base64 từ `content.js` và gửi một HTTP POST request đến Server cục bộ (127.0.0.1:8080).
- **`options.html` / `options.js`:** Giao diện cho phép người dùng nhập tài khoản, mật khẩu và bật/tắt tính năng Auto-Login.

### 2. Server AI Cục Bộ (Python)
Là một HTTP Server siêu nhẹ chạy bằng Python.
- **`server.py`:** Mở cổng `8080` trên `127.0.0.1`. Nó nhận ảnh Base64 từ Extension, giải mã ngược lại thành byte ảnh, đưa vào thư viện `ddddocr` để quét ra 4 ký tự, và trả kết quả chữ về cho Extension.
- **`start_server.bat`:** File thực thi nhanh trên Windows. Tự động kiểm tra cài đặt thư viện `ddddocr` qua `pip` và khởi chạy `server.py`.

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng

### Phần 1: Khởi động Server AI
1. Máy tính của bạn cần cài đặt **Python 64-bit** (khuyên dùng Python 3.12 trở lên) và **nhớ tích vào "Add python.exe to PATH"** khi cài đặt.
2. Mở thư mục dự án, nhấp đúp vào file **`start_server.bat`**.
3. Lần chạy đầu tiên, hệ thống sẽ tự động tải thư viện `ddddocr` (khoảng 70MB). 
4. Hãy để bảng đen (Terminal) chạy ngầm trong suốt quá trình sử dụng. Khi có dòng chữ `🚀 ddddocr Server đang chạy tại http://127.0.0.1:8080`, nghĩa là Server đã sẵn sàng.

### Phần 2: Cài đặt Extension lên trình duyệt
1. Mở Chrome hoặc Edge, truy cập vào trang quản lý: `chrome://extensions/`
2. Bật công tắc **Developer mode** (Chế độ dành cho nhà phát triển) ở góc trên bên phải.
3. Bấm vào nút **Load unpacked** (Tải tiện ích đã giải nén).
4. Chọn thư mục chứa dự án này.

### Phần 3: Trải nghiệm
1. Bấm vào biểu tượng Extension MyDTU trên thanh công cụ của Chrome.
2. Nhập Mã sinh viên và Mật khẩu MyDTU của bạn, bật công tắc **Auto-login** và bấm Lưu.
3. Truy cập vào trang `https://mydtu.duytan.edu.vn/Signin.aspx`.
4. Bỏ tay ra khỏi chuột và xem AI biểu diễn!

---

## ☁️ Hướng dẫn nâng cấp đưa lên VPS (Dành cho Pro)

Nếu bạn không muốn lúc nào cũng phải bật cái bảng đen trên máy tính của mình, bạn có thể đưa phần Server lên một con VPS (Ubuntu/Linux) chạy 24/7.

1. Bê file `server.py` lên con VPS.
2. Trên VPS chạy lệnh: `pip install ddddocr`
3. Sửa lại dòng code trong `server.py` từ `("127.0.0.1", PORT)` thành `("0.0.0.0", PORT)` để VPS cho phép nhận kết nối từ bên ngoài.
4. Mở Port 8080 trên Firewall của VPS. Chạy lệnh: `python3 server.py`
5. Về lại máy tính của bạn, mở file `background.js` ra, đổi cái link `http://127.0.0.1:8080/` thành `http://<IP_CỦA_VPS>:8080/`.
6. Mở file `manifest.json`, sửa lại quyền truy cập `http://127.0.0.1/*` thành `http://<IP_CỦA_VPS>/*`.
7. Refresh lại Extension và tận hưởng hệ thống Client-Server hoàn chỉnh!

---

*📝 Note: Dự án này là mã nguồn mở. Việc sử dụng công cụ tự động đăng nhập cần tuân thủ các quy định bảo mật của nhà trường.*
