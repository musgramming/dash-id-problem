from dash import MATCH, ALL, ALLSMALLER
import inspect
import os
import hmac
import hashlib
import random
import platform
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Union



# --- Khởi tạo hệ thống bảo mật mật mã (Cryptographic Initialization) ---

os.makedirs("utils/direction", exist_ok=True)
dotenv_path = "utils/direction/.env"

if not os.path.exists(dotenv_path):
    with open(dotenv_path, "w") as f:
        salt = random.getrandbits(1024).to_bytes(128, 'big').hex()
        f.write(f"RANDOM_SALT={salt}")



def protect_env_file(filepath):
    """
    Thiết lập quyền truy cập file ở mức hệ điều hành (OS-level permissions).
    Chỉ cho phép người dùng hiện tại đọc/ghi file Salt.
    """
    try:
        if platform.system() == "Windows":
            user = os.getlogin()
            os.system(f'icacls "{filepath}" /inheritance:r >nul 2>&1')
            os.system(f'icacls "{filepath}" /grant:r {user}:(R,W) >nul 2>&1')
        else:
            os.chmod(filepath, 0o600)

    except Exception:
        pass

protect_env_file(dotenv_path)

load_dotenv(dotenv_path)
__RANDOM_SALT_HEX = os.getenv("RANDOM_SALT")
__RANDOM_SALT = bytes.fromhex(__RANDOM_SALT_HEX) if __RANDOM_SALT_HEX else b'default_salt_if_failed'



def _hashing(string: str) -> str:
    """
    Thực hiện băm mật mã HMAC-SHA512.
    Biến dữ liệu thô (tên ID) thành chuỗi Hex an toàn không thể đảo ngược.
    """
    hash_object = hmac.new(
        key=__RANDOM_SALT, 
        msg=string.encode(), 
        digestmod=hashlib.sha512
    )
    return hash_object.hexdigest()

class PageDirection:
    """
    Manager trung tâm điều phối Namespace dựa trên mã băm cho Multi-page App.
    Đảm bảo tính cô lập giữa các trang bằng cách băm tên module thực thi.
    """
    def __init__(self) -> None:
        self.__pages: Dict[str, '_SingleDirection'] = {}

    def __get_page_hash(self, page_name: Optional[str] = None) -> str:
        """[Private] Tự động trích xuất và băm tên trang từ Call Stack."""
        if page_name is None:
            stack = inspect.stack()
            frame_info = stack[2]
            filename = frame_info.filename
            page_name = os.path.basename(filename).replace(".py", "")
        return _hashing(page_name)

    def assign_page(self, page: Optional[str] = None) -> '_SingleDirection':
        """Khởi tạo hoặc đăng ký một trang mới vào hệ thống quản lý băm."""
        page_hash = self.__get_page_hash(page)
        if page_hash not in self.__pages:
            self.__pages[page_hash] = _SingleDirection(page_hash)
        return self.__pages[page_hash]

    def use_page(self, page: Optional[str] = None) -> '_SingleDirection':
        """Truy xuất Instance quản lý của trang hiện tại."""
        return self.assign_page(page)

class _SingleDirection:
    """
    Hệ thống tạo ID bảo mật (Secured ID Generator).
    Mã hóa toàn bộ ID Dictionary trước khi gửi xuống Client-side.
    """
    def __init__(self, page_hash: str) -> None:
        self.__page: str = page_hash
        # Lưu trữ chỉ số index hiện tại (None nếu là static)
        self.__table_of_id: Dict[str, Optional[int]] = {}  
        # Ánh xạ hai chiều giữa ID thô và mã băm
        self.__hash_to_id: Dict[str, str] = {} 
        self.__id_to_hash: Dict[str, str] = {} 

    def __build_dict(self, id_hash: str, index: Any = None) -> Dict[str, Any]:
        """[Private] Đóng gói Dictionary theo cấu trúc Pattern-matching của Dash."""
        render_index = index if index is not None else "static"
        return {
            "type": self.__page,
            "id_name": id_hash,
            "index": render_index
        }

    def assign_id(self, id_name: str, is_dynamic: bool = False) -> Dict[str, Any]:
        """
        Đăng ký và băm một ID mới. Chặn trùng lặp ngay từ bước khai báo.
        
        Args:
            id_name: Tên ID dễ đọc (ví dụ: 'input-data').
            is_dynamic: Nếu True, khởi tạo index bắt đầu từ 1.
            
        Raises:
            Exception: Nếu ID trống hoặc đã tồn tại trong Registry của trang.
        """
        if not id_name: 
            raise Exception("Không được để ID trống")
        if id_name in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' đã tồn tại")
        
        id_hash = _hashing(id_name)
        self.__id_to_hash[id_name] = id_hash
        self.__hash_to_id[id_hash] = id_name
        self.__table_of_id[id_hash] = 1 if is_dynamic else None

        return self.__build_dict(id_hash, self.__table_of_id[id_hash])

    def next_index(self, id_name: str) -> Dict[str, Any]:
        """
        Tăng chỉ số index cho ID động. Thường dùng trong các hàm 'Add Row'.
        
        Raises:
            Exception: Nếu ID không tồn tại hoặc là ID tĩnh.
        """
        if not id_name: raise Exception("Không được để ID trống")
        if id_name not in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại để sinh thêm index")

        id_hash = self.__id_to_hash[id_name]
        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID {id_name} là id tĩnh. Không thể dùng next_index()")
        
        self.__table_of_id[id_hash] += 1 # type: ignore
        return self.__build_dict(id_hash, self.__table_of_id[id_hash])

    def use_id(self, id_name: str, index: Union[int, Any, None] = None) -> Dict[str, Any]:
        """
        Sử dụng lại ID đã đăng ký. Kiểm tra tính hợp lệ của index truyền vào.
        
        Args:
            id_name: Tên ID gốc.
            index: Chỉ số cụ thể (int) hoặc các hằng số MATCH/ALL.
            
        Raises:
            Exception: Nếu truyền index vào ID tĩnh hoặc không truyền vào ID động.
        """
        if not id_name: raise Exception("Không được để ID trống")
        if id_name not in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại")
        
        id_hash = self.__id_to_hash[id_name]
        val_in_table = self.__table_of_id[id_hash]

        if val_in_table is None:
            if index is not None:
                raise Exception(f"ID {id_name} là dạng static. Không được truyền index")
            return self.__build_dict(id_hash, index=None)
        
        if index is None:
            raise Exception(f"ID {id_name} là dạng dynamic. Phải truyền index")
        
        # Kiểm tra xem index yêu cầu có vượt quá giới hạn hiện tại không (tránh phỏng đoán ID)
        if isinstance(index, int) and val_in_table < index:
            raise Exception(f"Index {index} chưa được khởi tạo cho ID {id_name}")
        
        return self.__build_dict(id_hash, index)


    def reduce_index(self, id_name : str) -> Dict[str, Any]:
        """
        Giảm chỉ số index của một ID động và trả về cấu trúc đã băm.

        Args:
            id_name (str): Tên định danh gốc của component.

        Returns:
            Dict[str, Any]: Dictionary ID chứa mã băm của trang, mã băm của ID và index mới.

        Raises:
            Exception: Nếu id_name không tồn tại trong Registry.
            Exception: Nếu ID là dạng tĩnh (không có index để giảm).
            Exception: Nếu index đang ở mức tối thiểu (<= 1), không thể giảm thêm để tránh lỗi logic.
        """
        id_hash = self.__id_to_hash.get(id_name)
        if not id_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại")
        
        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID {id_name} là id tĩnh.")
        
        if self.__table_of_id[id_hash] <= 1:
            raise Exception(f"ID {id_name} không thể giảm thêm index.")

        self.__table_of_id[id_hash] -= 1
        return self.__build_dict(id_hash, self.__table_of_id[id_hash])


    def match(self, id_name : str) -> Dict[str, Any]:
        """
        Tạo khuôn mẫu khớp (Pattern-matching) dùng cho dash.MATCH.
        Sử dụng trong Callback để nhắm đến các component có cùng ID băm và cùng index.

        Args:
            id_name (str): Tên định danh gốc cần tạo khuôn mẫu.

        Returns:
            Dict[str, Any]: Dictionary ID với index là hằng số MATCH.

        Raises:
            Exception: Nếu ID chưa được khai báo hoặc là ID tĩnh (MATCH yêu cầu ID động).
        """
        id_hash = self.__id_to_hash.get(id_name)
        if not id_hash or self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' không hợp lệ cho MATCH")
        
        return self.__build_dict(id_hash, index=MATCH)


    def all(self, id_name : str) -> Dict[str, Any]:
        """
        Tạo khuôn mẫu khớp dùng cho dash.ALL.
        Dùng trong Callback để lấy dữ liệu từ tất cả các index của cùng một ID băm.

        Args:
            id_name (str): Tên định danh gốc.

        Returns:
            Dict[str, Any]: Dictionary ID với index là hằng số ALL.

        Raises:
            Exception: Nếu ID chưa khai báo hoặc không phải dạng động.
        """
        id_hash = self.__id_to_hash.get(id_name)
        if not id_hash or self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' không hợp lệ cho ALL")
        
        return self.__build_dict(id_hash, index=ALL)


    def allsmaller(self, id_name):
        """
        Tạo khuôn mẫu khớp dùng cho dash.ALLSMALLER.
        Thường dùng cho các logic lũy kế hoặc so sánh các component phía trước trong danh sách động.

        Args:
            id_name (str): Tên định danh gốc.

        Returns:
            Dict[str, Any]: Dictionary ID với index là hằng số ALLSMALLER.

        Raises:
            Exception: Nếu ID không hợp lệ cho cơ chế Pattern-matching.
        """
        id_hash = self.__id_to_hash.get(id_name)
        if not id_hash or self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' không hợp lệ cho ALLSMALLER")
        
        return self.__build_dict(id_hash, index=ALLSMALLER)