-- Users Table (Mặc dù là cá nhân nhưng vẫn nên có)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    telegram_id TEXT UNIQUE NOT NULL,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks Table (Nhiệm vụ học tập và sinh hoạt)
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- Ví dụ: 'Toán', 'Tiếng Anh', 'Tập luyện', 'Skincare', 'Đọc sách'
    title TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL, -- 'daily', 'weekly', 'once'
    target_time TIME, -- Giờ cần hoàn thành (ví dụ: '22:30')
    status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Daily Progress Table (Ghi nhận điểm danh mỗi ngày)
CREATE TABLE IF NOT EXISTS daily_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    task_id INTEGER NOT NULL,
    status TEXT NOT NULL, -- 'completed', 'failed', 'missed'
    proof_type TEXT, -- 'text', 'image', 'none'
    proof_content TEXT, -- Nội dung tóm tắt hoặc đường dẫn ảnh
    ai_evaluation TEXT, -- Đánh giá của AI về bài nộp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(task_id) REFERENCES tasks(task_id)
);

-- Subjects Tracker (Lộ trình "Xóa mù")
CREATE TABLE IF NOT EXISTS subjects_tracker (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_name TEXT NOT NULL, -- 'Toán Cao Cấp', 'Mạch Điện Tử'
    current_level TEXT, -- 'Mất gốc', 'Kém'
    target_level TEXT, -- 'Bằng Đỏ', 'Qua môn'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL, -- Thường là 90 ngày
    progress_percentage INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Milestones (Tiền đề Tình cảm/Sự nghiệp)
CREATE TABLE IF NOT EXISTS milestones (
    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- 'Tài chính', 'Học thuật'
    name TEXT NOT NULL, -- 'Đạt GPA 3.2', 'Có thu nhập từ chuyên ngành'
    achieved BOOLEAN DEFAULT FALSE,
    achieved_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Course Weaknesses (Theo dõi điểm yếu từng môn để ra bài tập A/A+)
CREATE TABLE IF NOT EXISTS course_weaknesses (
    weakness_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_name TEXT NOT NULL, -- 'Toán A1', 'Vật Lý 1'
    weak_topic TEXT NOT NULL, -- 'Tích phân', 'Cơ học'
    ai_score FLOAT DEFAULT 0.0, -- Điểm AI chấm trung bình các bài tập
    last_practiced DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Academic Records (Lịch sử điểm số cào từ MyDTU)
CREATE TABLE IF NOT EXISTS academic_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    credits INTEGER,
    score FLOAT,
    grade_letter TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_code),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Seen Announcements (Ghi nhớ các thông báo MyDTU đã gửi để tránh spam)
CREATE TABLE IF NOT EXISTS seen_announcements (
    announcement_id TEXT PRIMARY KEY,
    title TEXT,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
