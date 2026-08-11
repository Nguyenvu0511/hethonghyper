import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='learning_system.db'):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        """Khởi tạo cơ sở dữ liệu từ file schema.sql nếu chưa có"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_script = f.read()
                cursor.executescript(schema_script)
                conn.commit()
                logger.info("Database initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing database: {e}")

    def add_user(self, telegram_id, username):
        """Thêm người dùng mới"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username)
                VALUES (?, ?)
            ''', (telegram_id, username))
            conn.commit()

    def get_user_id(self, telegram_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def add_task(self, user_id, category, title, description, frequency, target_time):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (user_id, category, title, description, frequency, target_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, category, title, description, frequency, target_time))
            conn.commit()
            return cursor.lastrowid

    def get_daily_tasks(self, user_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tạm thời query đơn giản
            cursor.execute('''
                SELECT task_id, category, title, description, target_time 
                FROM tasks 
                WHERE user_id = ? AND frequency = 'daily'
            ''', (user_id,))
            return cursor.fetchall()

    def get_completed_tasks_today(self, user_id):
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT task_id FROM daily_progress 
                WHERE user_id = ? AND date = ? AND status = 'completed'
            ''', (user_id, today))
            return [row[0] for row in cursor.fetchall()]

            
    def log_daily_progress(self, user_id, task_id, status, proof_type=None, proof_content=None, ai_evaluation=None):
        today = datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_progress (user_id, date, task_id, status, proof_type, proof_content, ai_evaluation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, today, task_id, status, proof_type, proof_content, ai_evaluation))
            conn.commit()
            return cursor.lastrowid
            
    def clear_old_academic_tasks(self, user_id):
        """Xóa các nhiệm vụ học thuật cũ và lộ trình cũ trước khi tạo mới"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE user_id = ? AND category = 'Học thuật'", (user_id,))
            cursor.execute("DELETE FROM subjects_tracker WHERE user_id = ?", (user_id,))
            conn.commit()

    def insert_roadmap(self, user_id, subject_name, target_level, end_date):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO subjects_tracker (user_id, subject_name, current_level, target_level, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, subject_name, 'Cần cải thiện', target_level, today, end_date))
            conn.commit()
            
    def get_all_users(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, telegram_id, username FROM users')
            return cursor.fetchall()
            
    def get_task_by_id(self, task_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
            return cursor.fetchone()

    def is_announcement_seen(self, announcement_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT announcement_id FROM seen_announcements WHERE announcement_id = ?', (announcement_id,))
            return cursor.fetchone() is not None

    def mark_announcement_seen(self, announcement_id, title):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO seen_announcements (announcement_id, title)
                VALUES (?, ?)
            ''', (announcement_id, title))
            conn.commit()

# Khởi tạo singleton
db = DatabaseManager(db_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'learning_system.db'))
