# ID Problem in Dash

Dự án này giới thiệu một kiến trúc quản lý định danh (ID Management) tiên tiến, nhằm giải quyết triệt để những hạn chế cố hữu của Plotly Dash trong các ứng dụng quy mô lớn.

# 🔴 Vấn đề (The Problem)

Trong Dash tiêu chuẩn, việc quản lý ID thường đối mặt với:

- ID Collisions: Dễ trùng lặp ID khi ứng dụng có nhiều trang (Multi-page).

- Security Leak: ID lộ diện dưới dạng PlainText ở Client-side, giúp hacker dễ dàng đoán biết cấu trúc logic.

- Maintenance Hell: Việc gõ tay chuỗi ID dẫn đến sai sót (Typo) mà không có cảnh báo sớm.

- Dynamic Complexity: Quản lý MATCH, ALL bằng Dictionary thủ công cực kỳ rườm rà.

# 🟢 Giải pháp của tôi (The Direction Solution)

Bộ công cụ PageDirection (nằm trong utils/direction) giải quyết các vấn đề trên bằng tư duy bảo mật của Rust và sức mạnh của Mật mã học:

1. Cryptographic Namespacing: Tự động băm ID bằng HMAC-SHA512. ID trên trình duyệt bây giờ là các chuỗi Hex không thể giải mã.

2. Zero-Configuration: Tự động nhận diện trang thông qua Call Stack, không cần khai báo Namespace thủ công.

3. Fail-Fast System: Ném Exception ngay khi có sai sót nhỏ nhất về logic ID trước khi App kịp Render.

4. Encapsulated Pattern-Matching: Đơn giản hóa Dash Pattern-matching thành các hàm match(), all() minh bạch.

# Hướng dẫn coding

1. Ở đầu từng trang:

```py
from utils.direction import pdp     # Nếu muốn dễ đọc
from utils.direction import pds     # Nếu muốn an toàn

page = pdp.assign_page() # Hoặc pds.assign_page()
```

2. Ở các layout, ví dụ:

```py
from dash import html, callback
import dash_bootstrap_components as dbc


...
# Ví dụ sử dụng id 'input-1'
dbc.Input(id=page.assign_id("input-1"))
...
```

3. Ở các callback

```py
@callback(
    Output(page.use_id("result-display"), "children"),
    Input(page.use_id("input-1"), "value")
)
# Hàm của bạn
```



