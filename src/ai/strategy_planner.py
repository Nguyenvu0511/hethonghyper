import logging
from src.ai.client import ai_client

logger = logging.getLogger(__name__)

def generate_aa_strategy(syllabus_text):
    """
    Phân tích đề cương môn học (Syllabus) để sinh ra lộ trình lấy điểm A/A+.
    """
    prompt = f"""
    Bạn là một Chiến Lược Gia Học Tập cực kỳ xuất sắc.
    Sinh viên vừa cung cấp cho bạn một đề cương môn học (Syllabus). Mục tiêu của sinh viên là lấy điểm A hoặc A+ (trên 8.5 hoặc 9.0) cho môn này.
    
    Đề cương môn học:
    "{syllabus_text}"
    
    Nhiệm vụ của bạn:
    1. Trích xuất các trọng số điểm (nếu có): Chuyên cần, Bài tập, Giữa kỳ, Cuối kỳ.
    2. Dựa vào trọng số đó, đưa ra chiến lược tối ưu:
       - Phần nào cần tập trung học hàng ngày?
       - Mẹo lấy điểm tối đa ở phần Tiểu luận/Thuyết trình (nếu có)?
       - Chiến thuật ôn thi cuối kỳ (Cần bắt đầu ôn trước bao nhiêu tuần).
    3. Trả về kết quả dưới dạng Markdown chuyên nghiệp, rõ ràng, mang tính động viên và kỷ luật thép.
    """
    
    try:
        return ai_client.generate_text(prompt)
    except Exception as e:
        logger.error(f"Lỗi khi sinh chiến lược A/A+: {e}")
        return f"Lỗi xử lý đề cương: {e}"

def generate_daily_quiz(subject_name):
    """
    Sinh bài tập nhỏ (Quiz) hằng ngày để 'Xóa mù chữ' cho các môn yếu.
    """
    prompt = f"""
    Bạn là một Gia Sư khắt khe nhưng cực kỳ tâm huyết.
    Học sinh của bạn đang bị hổng kiến thức môn "{subject_name}" ở bậc Đại học.
    Mục tiêu: Xóa mù chữ và phục hồi nền tảng căn bản (Toán cao cấp, Vật lý, Kỹ thuật điện...).
    
    Hãy sinh ra 1 BÀI TẬP DUY NHẤT (trắc nghiệm hoặc tự luận ngắn) tập trung vào một khái niệm lõi của môn "{subject_name}".
    Bài tập này không được quá khó, nhưng phải đánh trúng bản chất.
    Trả về định dạng Markdown, có đánh dấu phần [CÂU HỎI]. KHÔNG BAO GỒM LỜI GIẢI (vì học sinh phải tự giải ra giấy và nộp lại).
    """
    
    try:
        return ai_client.generate_text(prompt)
    except Exception as e:
        logger.error(f"Lỗi khi sinh Quiz môn {subject_name}: {e}")
        return f"Lỗi ra đề: {e}"

def generate_academic_advice(records_text, target="Bằng Đỏ"):
    """
    Phân tích bảng điểm và đưa ra lời khuyên "Báo cáo Sát thủ" dựa trên mục tiêu Bằng Đỏ.
    """
    prompt = f"""
    Bạn là Cố Vấn Học Tập tàn nhẫn nhưng chân thành. 
    Học sinh của bạn có mục tiêu đạt được "{target}" (GPA >= 3.2 hoặc 3.6).
    
    Dưới đây là lịch sử điểm số của học sinh (đã thu thập được):
    {records_text}
    
    Yêu cầu:
    1. Chỉ ra những môn điểm F bắt buộc phải đăng ký học lại ngay. Nhận xét thật gắt gao.
    2. Chỉ ra các môn có điểm D hoặc C- đang kéo lùi GPA. Tính toán xem có NÊN học cải thiện môn đó không và phân tích kỹ TỪNG MÔN MỘT (tại sao phải học lại, ích lợi là gì).
    3. Đưa ra 1 chiến lược tổng thể dài hạn để cứu vớt tình hình, thái độ học tập, và dặn dò cực kỳ nghiêm khắc.
    4. Giọng điệu: Khinh bỉ sự lười biếng, tàn nhẫn, lạnh lùng, nhưng phân tích cực kỳ logic và thuyết phục. Viết cực kỳ DÀI và CHI TIẾT.
    5. Trích xuất danh sách các môn học cụ thể cần đưa vào LỘ TRÌNH học lại/cải thiện.
    6. Đề xuất các NHIỆM VỤ HÀNG NGÀY (daily tasks) cụ thể.
    
    BẮT BUỘC TRẢ VỀ CHÍNH XÁC ĐỊNH DẠNG JSON, KHÔNG CÓ COMMENTS (//), VÀ PHẢI ESCAPE DẤU NGOẶC KÉP (\") BÊN TRONG CHUỖI, VỚI CẤU TRÚC SAU:
    {{
      "advice": "Văn bản nhận xét cực kỳ dài và chi tiết. Viết giống hệt một bài báo cáo phân tích sâu sắc, chia làm 3 phần rõ rệt: [CẢNH BÁO ĐỎ], [CHIẾN LƯỢC CẢI THIỆN] (phân tích từng môn), [LỜI KHUYÊN TỔNG THỂ]. Dùng \\n\\n để tạo các đoạn văn cách nhau dễ nhìn. Tuyệt đối không dùng dấu ngoặc kép chưa escape bên trong đoạn văn này.",
      "roadmap": [
         {{"subject_name": "Tên môn học", "target_level": "Mục tiêu (ví dụ: B+ hoặc A)", "end_date": "YYYY-MM-DD"}}
      ],
      "daily_tasks": [
         {{"category": "Học thuật", "title": "Tên nhiệm vụ ngắn gọn", "description": "Mô tả chi tiết nhiệm vụ", "target_time": "Thời gian dự kiến (ví dụ 20:00)"}}
      ]
    }}
    """
    import time
    import json
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response_text = ai_client.generate_text(prompt, is_json=True)
            
            # Cắt lấy đúng phần JSON (từ dấu { đầu tiên đến dấu } cuối cùng)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                response_text = response_text[start_idx:end_idx+1]
            else:
                raise json.JSONDecodeError("Không tìm thấy JSON", response_text, 0)
            
            result = json.loads(response_text, strict=False)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON từ AI: {e}. Raw text: {response_text}")
            if attempt == max_retries - 1:
                return {"advice": f"Lỗi định dạng phản hồi từ AI: {e}\n\nRaw text:\n{response_text[:1500]}", "roadmap": [], "daily_tasks": []}
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Lỗi API (lần {attempt+1}): {e}. Thử lại sau 5s...")
                time.sleep(5)
                continue
            logger.error(f"Lỗi khi sinh Academic Advice: {e}")
            return {"advice": f"Lỗi phân tích: {e}", "roadmap": [], "daily_tasks": []}

def summarize_announcement(html_content):
    """
    Tóm tắt nội dung thông báo từ MyDTU.
    """
    prompt = f"""
    Dưới đây là mã HTML/text của một thông báo từ trường đại học:
    "{html_content}"
    
    Hãy đọc và TÓM TẮT THẬT NGẮN GỌN (bullet points) thông báo trên. 
    Lọc bỏ các thủ tục rườm rà. Chỉ lấy: 
    - Sự kiện gì?
    - Dành cho ai? 
    - Có deadline/thời hạn hành động không?
    
    Sử dụng giọng điệu nhắc nhở dứt khoát của một Bot AI Kỷ Luật.
    """
    
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return ai_client.generate_text(prompt)
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Lỗi API (lần {attempt+1}): {e}. Thử lại sau 5s...")
                time.sleep(5)
                continue
            logger.error(f"Lỗi khi tóm tắt thông báo: {e}")
            return f"Lỗi phân tích nội dung: {e}"


def generate_daily_plan(records_text, timetable_today, date_str):
    """
    Sinh danh sách nhiệm vụ HÔM NAY dựa trên lịch học thực tế của hôm nay và điểm số.
    """
    prompt = f"""
    Bạn là Bot Kỷ Luật. Nhiệm vụ của bạn là vạch ra lịch trình (daily tasks) cho học sinh trong HÔM NAY ({date_str}).
    
    1. Dưới đây là các môn học yếu kém cần cày cuốc (F, D, C-):
    {records_text}
    
    2. Dưới đây là lịch học TRÊN TRƯỜNG của học sinh trong HÔM NAY:
    {timetable_today if timetable_today else 'Hôm nay học sinh được nghỉ học trên trường, toàn thời gian rảnh rỗi.'}
    
    Yêu cầu:
    Tạo ra 3-5 nhiệm vụ trong ngày HÔM NAY.
    TUYỆT ĐỐI KHÔNG xếp nhiệm vụ trùng với khung giờ học trên trường.
    Hãy chèn xen kẽ: 1 nhiệm vụ thể dục/chạy bộ, 1-2 nhiệm vụ tự học sâu (Deep Work) cho các môn yếu kém.
    
    BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON, KHÔNG CÓ COMMENTS:
    {{
      "daily_tasks": [
         {{"category": "Học thuật / Thể chất", "title": "Tên nhiệm vụ ngắn gọn", "description": "Mô tả chi tiết", "target_time": "Giờ dự kiến (VD: 20:00)"}}
      ]
    }}
    """
    import time
    import json
    for attempt in range(3):
        try:
            response_text = ai_client.generate_text(prompt, is_json=True)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                response_text = response_text[start_idx:end_idx+1]
            return json.loads(response_text, strict=False)
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
                continue
            logger.error(f"Lỗi khi sinh Daily Plan: {e}")
            return {"error": str(e), "raw_text": response_text if 'response_text' in locals() else ""}
