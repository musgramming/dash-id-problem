import sympy as sp



def __jsonify_triangle_result(is_exist : bool, data : dict = {}, error : str = None):
    """
    Mã hóa kết quả trả về của tam giác

    Parameters:
        is_exist: Tính tồn tại của tam giác
        data: Kết quả trả về từ tam giác
        error: Ngoại lệ từ tam giác đó nếu có
    """
    return {
        "Tồn tại" : is_exist,
        "Kết quả" : data,
        "Lỗi" : error
    }


def __check_equal(a, b, epsilon = 1e-7):
    return abs(a - b) <= epsilon




def solve_triangle(x1, y1, x2, y2, x3, y3):
    """
    Trả về thông tin tam giác, bao gồm trạng thái tồn tại, loại tam giác (theo cạnh và theo góc), chu vi và diện tích
    
    Parameters:
        x1: Hoành độ điểm A
        y1: Tung độ điểm A
        x2: Hoành độ điểm B
        y2: Tung độ điểm B
        x3: Hoành độ điểm C
        y3: Tung độ điểm C
    """
    # Kiểm tra đã nhập chưa
    if any(val is None for val in [x1, x2, x3, y1, y2, y3]):
        return __jsonify_triangle_result(is_exist=False, error="Có giá trị chưa nhập")

    A = sp.Point(x1, y1)
    B = sp.Point(x2, y2)
    C = sp.Point(x3, y3)

    # Kiểm tra 3 điểm trùng nhau
    if (A == B) or (A == C) or (B == C):
        return __jsonify_triangle_result(is_exist=False, error="3 điểm trùng nhau")

    a = B.distance(C)
    b = A.distance(C)
    c = A.distance(B)


    # Kiểm tra 3 điểm thẳng hàng
    if (a + b == c) or (b + c == a) or (b == a + c):
        return __jsonify_triangle_result(is_exist=False, error="3 điểm thẳng hàng")

    # Tính toán thông số của tam giác
    triangle = sp.Triangle(A, B, C)
    angles = triangle.angles

    # Phân loại tam giác
    # Theo góc
    type_by_angles = None
    pi_2 = float((sp.pi / 2).evalf())
    if any(float(val) > pi_2 + 1e-7 for val in angles.values()):
        type_by_angles = "Tam giác tù"
    elif any(abs(float(val) - pi_2) <= 1e-7 for val in angles.values()):
        type_by_angles = "Tam giác vuông"
    else:
        type_by_angles = "Tam giác nhọn"


    # Theo cạnh
    type_by_edges = None 
    if __check_equal(a, b) and __check_equal(b, c):
        type_by_edges = "Tam giác đều"
    elif __check_equal(a, b) or __check_equal(a, c) or __check_equal(b, c):
        type_by_edges = "Tam giác cân"
    else: 
        type_by_edges = "Tam giác thường"
    
    return __jsonify_triangle_result(
        is_exist=True, 
        data = {
            "Chu vi" : float(triangle.perimeter.evalf()),
            "Diện tích" : abs(float(triangle.area.evalf())),
            "Phân loại (theo cạnh)": type_by_edges,
            "Phân loại (theo góc)": type_by_angles
        }
    )