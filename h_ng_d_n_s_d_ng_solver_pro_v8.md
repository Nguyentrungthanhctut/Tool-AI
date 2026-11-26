# Solver Pro V8 — Hướng dẫn cài đặt & sử dụng

**Solver Pro V8** là công cụ hỗ trợ đối chiếu bài tập luyện tập trên máy tính Windows, tích hợp Google Gemini API với các thao tác chụp vùng màn hình, dán ảnh nhanh từ Clipboard, cắt vùng từ file ảnh và giải trực tiếp văn bản.

*Developed by **ThanhDevHub***

---

## 1. Cấu trúc thư mục dự án

```text
├── dist/
│   └── SolverProV8.exe      # File thực thi chính (chạy độc lập, không cần cài Python)
├── build/                   # Thư mục file tạm sinh ra trong quá trình đóng gói PyInstaller
├── solver_pro_v8.py         # Mã nguồn gốc Python của ứng dụng
├── SolverProV8.spec         # File cấu hình đóng gói của PyInstaller
└── README.md                # Tài liệu hướng dẫn sử dụng
```

> **Lưu ý khi chia sẻ hoặc dọn dẹp:**
> * Nếu gửi ứng dụng cho người khác dùng ngay, bạn chỉ cần gửi duy nhất file `dist\SolverProV8.exe`.
> * Thư mục `build\` và file `SolverProV8.spec` chỉ phục vụ cho việc đóng gói lại mã nguồn, không cần thiết khi chạy `SolverProV8.exe` (có thể xóa nếu muốn dọn nhẹ thư mục).

---

## 2. Yêu cầu hệ thống

* **Hệ điều hành:** Windows 10 hoặc Windows 11 (64-bit).
* **Kết nối:** Có Internet ổn định.
* **Tài khoản:** Có **Gemini API Key** hợp lệ (lấy miễn phí tại Google AI Studio).

---

## 3. Cách 1: Chạy trực tiếp bằng file `.exe` (Khuyên dùng)

Phù hợp cho người dùng thông thường hoặc máy không cài đặt môi trường Python.

1. Mở thư mục `dist`.
2. Nhấp đúp vào file `SolverProV8.exe`.
3. Chờ màn hình khởi động chạy hoàn tất `100%`, sau đó nhấn nút **BẮT ĐẦU →**.
4. Nhấn **Dán API Key** (hoặc nhập trực tiếp vào ô) → nhấn **Kiểm tra & Kết nối**.

---

## 4. Cách 2: Chạy trực tiếp từ mã nguồn Python (Không cần file `.exe`)

Phù hợp khi bạn muốn chỉnh sửa code, tùy biến giao diện hoặc tự đóng gói lại.

### Bước 1: Cài đặt Python & thư viện phụ thuộc

Đảm bảo máy đã cài **Python 3.10 trở lên** (tích chọn *Add Python to PATH* khi cài). Mở **Command Prompt (CMD)** hoặc **PowerShell** và cài thư viện xử lý ảnh Pillow:

```bash
pip install pillow
```

### Bước 2: Khởi chạy ứng dụng

Mở Terminal tại thư mục chứa `solver_pro_v8.py` và chạy:

```bash
python solver_pro_v8.py
```

### Bước 3: Đóng gói lại thành file `.exe` (Nếu có chỉnh sửa code)

Nếu bạn sửa file `solver_pro_v8.py` và muốn cập nhật lại file trong thư mục `dist\`, chạy lệnh:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name SolverProV8 solver_pro_v8.py
```

File `SolverProV8.exe` mới sẽ tự động ghi đè vào thư mục `dist\`.

---

## 5. Hướng dẫn lấy & quản lý Gemini API Key

1. Truy cập **Google AI Studio** và đăng nhập bằng tài khoản Google.
2. Chọn **Get API key** → **Create API key**.
3. Sao chép chuỗi khóa và nhấn **Dán API Key** trong ứng dụng.

* **Tự động lưu Key:** Sau lần kết nối thành công đầu tiên, ứng dụng tự động lưu API Key tại `%APPDATA%\SolverProV8\config.json` để bạn không phải nhập lại ở những lần mở sau.
* **Đổi hoặc xóa Key:** Nhấn nút **Đổi API** ở góc dưới bên phải màn hình chính để nhập key mới, hoặc xóa thư mục `%APPDATA%\SolverProV8` để xóa dữ liệu cấu hình.
* **Bảo mật:** Không chia sẻ công khai API Key hoặc đăng key lên mạng xã hội, kho mã nguồn công khai.

---

## 6. Các tính năng chính trên giao diện

| Chức năng | Cách thao tác |
| :--- | :--- |
| **Chụp vùng màn hình** | Nhấn **Chụp vùng màn hình** → giữ chuột trái kéo chọn khu vực đề bài → thả chuột để giải ngay (nhấn `Esc` để hủy). |
| **Dán (Text / Ảnh)** | Chụp màn hình bằng `Win + Shift + S` hoặc copy ảnh/văn bản → nhấn **Dán (Text / Ảnh)** hoặc bấm phím tắt `Ctrl + V`. |
| **Giải văn bản** | Nhập hoặc dán đề bài vào ô trống phía trên → nhấn **Giải văn bản**. |
| **Cắt từ file ảnh** | Nhấn **Cắt từ file ảnh** → chọn file (`PNG`, `JPG`, `JPEG`, `WEBP`) → kéo khoanh vùng câu hỏi → nhấn **Giải vùng đã chọn**. |
| **Chọn file ảnh giải ngay** | Nhấn **Chọn file ảnh giải ngay** để gửi toàn bộ ảnh bài tập (dung lượng tối đa `10 MB`). |
| **Độ mờ cửa sổ & Sao chép** | Kéo thanh trượt ở thanh công cụ dưới cùng để làm mờ cửa sổ khi cần đè lên tài liệu; nhấn **Sao chép** để copy đáp án. |

---

## 7. Khắc phục sự cố thường gặp

* **Windows SmartScreen cảnh báo khi mở `SolverProV8.exe`:**
  * Nhấn **More info** → **Run anyway**. Cảnh báo này xuất hiện do file `.exe` tự đóng gói chưa đăng ký chữ ký số thương mại.
* **Lỗi kết nối API (`HTTP 400`, `403`, `429`):**
  * Kiểm tra lại kết nối Internet.
  * Đảm bảo API Key không dính khoảng trắng thừa, còn hiệu lực hoặc chưa vượt quá giới hạn lượt gọi miễn phí (Quota) của Google AI Studio.
* **Không chụp được vùng màn hình hoặc ảnh bị đen:**
  * Nếu cửa sổ chứa đề bài đang chạy dưới quyền Administrator, hãy chạy `SolverProV8.exe` bằng quyền **Run as administrator**.
  * Kiểm tra xem có phần mềm bảo mật chống chụp màn hình nào đang bật hay không.

---

**© 2026 ThanhDevHub • All Rights Reserved**