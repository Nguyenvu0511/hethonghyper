import os
import logging
from src.ai.client import ai_client

logger = logging.getLogger(__name__)

def evaluate_text_report(task_category, text_content):
    """
    Sử dụng AI để chấm điểm một bài báo cáo dạng text (ví dụ: tóm tắt sách).
    Trả về (status, feedback_message)
    status: 'completed' hoặc 'failed'
    """
    prompt = f"""
    Bạn là một Người Thầy Ảo khắt khe, đang giám sát quá trình tự rèn luyện của một sinh viên (Thân - Tâm - Trí).
    Sinh viên vừa nộp báo cáo cho nhiệm vụ thuộc danh mục: '{task_category}'.
    
    Nội dung báo cáo:
    "{text_content}"
    
    Nhiệm vụ của bạn:
    1. Đánh giá xem báo cáo này có hời hợt, chống đối hay không.
    2. Nếu sinh viên có vẻ đang than vãn mệt mỏi, hãy nhắc nhở triết lý: "Thành công = Ý chí", và khuyên nghỉ ngơi 15 phút rồi làm tiếp.
    3. Cuối cùng, quyết định xem nhiệm vụ này là PASS (Đạt) hay FAIL (Làm lại).
    
    Định dạng phản hồi BẮT BUỘC bắt đầu bằng chữ [PASS] hoặc [FAIL], sau đó là nhận xét của bạn.
    """
    
    try:
        reply = ai_client.generate_text(prompt).strip()
        
        status = 'completed' if reply.startswith('[PASS]') else 'failed'
        # Xóa tiền tố [PASS]/[FAIL] để lấy nhận xét
        feedback = reply.replace('[PASS]', '').replace('[FAIL]', '').strip()
        
        return status, feedback
    except Exception as e:
        logger.error(f"Lỗi khi gọi AI API: {e}")
        return 'failed', f"Đã có lỗi xảy ra khi chấm bài: {e}"

def evaluate_image_report(task_category, image_path):
    """
    Sử dụng Vision AI để đánh giá ảnh nộp (bài tập Toán, ảnh tập thể dục, điểm danh sáng).
    """
    prompt = f"""
    Bạn là một Người Thầy Ảo khắt khe.
    Sinh viên vừa nộp một BỨC ẢNH để chứng minh đã hoàn thành nhiệm vụ thuộc danh mục: '{task_category}'.
    
    Hãy quan sát bức ảnh và xác minh:
    1. Ảnh này có thực sự khớp với yêu cầu của '{task_category}' không? (Ví dụ: Nếu là tập luyện thì phải có cảnh tập hoặc đổ mồ hôi. Nếu là Toán Cao Cấp thì phải là giấy nháp có công thức toán).
    2. Trả về [PASS] nếu ảnh hợp lệ và chứng minh được nỗ lực, hoặc [FAIL] nếu ảnh sai, không liên quan, hoặc lấy từ mạng.
    
    Định dạng phản hồi BẮT BUỘC bắt đầu bằng chữ [PASS] hoặc [FAIL], sau đó là lời nhận xét nghiêm khắc.
    """
    
    try:
        reply = ai_client.generate_vision(prompt, image_path).strip()
        
        status = 'completed' if reply.startswith('[PASS]') else 'failed'
        feedback = reply.replace('[PASS]', '').replace('[FAIL]', '').strip()
        
        return status, feedback
    except Exception as e:
        logger.error(f"Lỗi xử lý ảnh với AI: {e}")
        return 'failed', f"Lỗi đọc ảnh: {e}"

