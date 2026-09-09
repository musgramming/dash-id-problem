import sys
import os


def _resolve_page_name() -> str:
    """Hàm phụ trợ lấy tên trang tối ưu bằng sys._getframe."""
    frame = sys._getframe(2)
    filename = frame.f_code.co_filename
    
    # Lấy tên file thuần túy không bao gồm đường dẫn và phần mở rộng .py
    basename = os.path.basename(filename)
    return basename.replace(".py", "")