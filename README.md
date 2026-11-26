<div align="center">

# ⚡ SOLVER PRO V8

**Công cụ đối chiếu & giải bài tập luyện tập trên Windows tích hợp Google Gemini API**

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Gemini API](https://img.shields.io/badge/Google-Gemini%20API-8E75B2?style=for-the-badge&logo=google&logoColor=white)](#)
[![Author](https://img.shields.io/badge/Developed%20by-ThanhDevHub-2ea44f?style=for-the-badge)](#)

*Nhẹ • Chạy độc lập không cần cài đặt • Hỗ trợ DPI Scaling • Dán ảnh trực tiếp từ Clipboard*

</div>

---

## 📁 Cấu trúc thư mục dự án

```text
📦 SolverProV8/
 ┣ 📂 dist/
 ┃ ┗ 🚀 SolverProV8.exe      # File chạy chính thức (độc lập, chỉ cần file này để dùng)
 ┣ 📂 build/                 # Thư mục tạm sinh ra khi đóng gói PyInstaller (có thể xóa)
 ┣ 📜 solver_pro_v8.py       # Mã nguồn Python gốc của ứng dụng
 ┣ 📜 SolverProV8.spec       # File cấu hình đóng gói PyInstaller
 ┗ 📖 README.md              # Tài liệu hướng dẫn sử dụng
```

> **Mẹo chia sẻ:** Khi gửi ứng dụng cho máy khác dùng, bạn **chỉ cần gửi duy nhất file `dist\SolverProV8.exe`**. Thư mục `build/` và file `.spec` không cần thiết khi chạy.

---

## ✨ Tính năng nổi bật

* **🖥️ Chụp vùng màn hình trực tiếp:** Kéo chuột khoanh vùng bất kỳ trên màn hình để gửi bài tập ngay lập tức (tự động khử lệch tọa độ khi bật Windows Scaling `125%–150%`).
* **📋 Dán thông minh (`Ctrl + V`):** Tự động nhận diện ảnh chụp màn hình từ Clipboard (`Win + Shift + S`) hoặc văn bản để xử lý ngay trong 1 thao tác.
* **✂️ Cắt vùng & Tải file ảnh:** Hỗ trợ mở file `PNG`, `JPG`, `JPEG`, `WEBP` (tối đa `10 MB`) để khoanh vùng từng câu hỏi hoặc giải toàn bộ ảnh.
* **🤖 Tự động dò tìm & xếp hạng Model:** Tự động quét danh sách model `gemini-*` khả dụng, ưu tiên bản `Flash` / `Lite` ổn định mới nhất và tự chuyển sang model dự phòng nếu gặp lỗi.
* **🔑 Lưu cấu hình tự động:** Ghi nhớ Gemini API Key cục bộ sau lần kết nối đầu tiên, kèm thanh trượt chỉnh độ mờ cửa sổ (`75%–100%`) để đè lên tài liệu học tập.

---

## 🚀 Hướng dẫn sử dụng

### Cách 1: Chạy trực tiếp bằng file `.EXE` (Khuyên dùng)

Phù hợp cho mọi máy tính Windows, **không cần cài Python**:

1. Mở thư mục **`dist`** và nhấp đúp vào **`SolverProV8.exe`**.
2. Chờ màn hình khởi động chạy hoàn tất **`100%`**, nhấn **`BẮT ĐẦU →`**.
3. Nhấn **`Dán API Key`** (hoặc nhập thủ công) → nhấn **`Kiểm tra & Kết nối`**.

---

### Cách 2: Chạy trực tiếp từ mã nguồn Python (Không cần file `.EXE`)

Phù hợp khi bạn muốn chỉnh sửa giao diện, tùy biến prompt hoặc tự đóng gói lại:

**Bước 1:** Cài đặt thư viện xử lý ảnh `Pillow` (yêu cầu Python 3.10+):
```bash
pip install pillow
```

**Bước 2:** Chạy trực tiếp ứng dụng:
```bash
python solver_pro_v8.py
```

*(Tùy chọn)* Đóng gói lại thành file `.exe` mới sau khi sửa code:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name SolverProV8 solver_pro_v8.py
```

---

## 🎮 Bảng phím tắt & Thao tác nhanh

| Thao tác / Nút bấm | Chức năng |
| :--- | :--- |
| **`Chụp vùng màn hình`** | Làm mờ toàn màn hình, giữ chuột trái kéo chọn đề bài và thả chuột để giải (`Esc` để hủy). |
| **`Dán (Text / Ảnh)`** hoặc `Ctrl + V` | Tự động gửi ảnh trong Clipboard (sau khi chụp bằng `Win + Shift + S`) hoặc dán chữ vào ô nhập. |
| **`Giải văn bản`** | Gửi nội dung bài tập đã nhập/dán trong khung văn bản để đối chiếu đáp án. |
| **`Cắt từ file ảnh`** | Mở ảnh từ máy tính, kéo chọn vùng câu hỏi cần giải và nhấn **`Giải vùng đã chọn`**. |
| **`Chọn file ảnh giải ngay`** | Chọn file ảnh có sẵn trên máy và gửi toàn bộ ảnh cho AI xử lý. |
| **Thanh trượt độ mờ (`75%–100%`)** | Điều chỉnh độ trong suốt của cửa sổ ứng dụng khi đặt chồng lên file PDF/Word. |
| **`Sao chép` / `Đổi API`** | Copy nhanh kết quả ra Clipboard hoặc thay đổi Gemini API Key bất kỳ lúc nào. |

---

## 🔑 Lấy & Quản lý Gemini API Key

1. Truy cập **[Google AI Studio](https://aistudio.google.com/)** và đăng nhập tài khoản Google.
2. Chọn **Get API key** → **Create API key** → sao chép chuỗi khóa.
3. Dán vào màn hình kết nối của **Solver Pro V8**.

* **Vị trí lưu cấu hình:** `%APPDATA%\SolverProV8\config.json` (tự động nạp ở các lần mở sau).
* **Xóa dữ liệu cá nhân:** Bấm **`Đổi API`** trong app để ghi đè key mới, hoặc xóa thư mục `%APPDATA%\SolverProV8`.

---

## 🛠️ Khắc phục sự cố

<details>
<summary><b>1. Windows SmartScreen hiện cảnh báo khi mở <code>SolverProV8.exe</code></b></summary>
<br>
Nhấn <b>More info</b> → chọn <b>Run anyway</b>. Cảnh báo này xuất hiện do file <code>.exe</code> tự đóng gói cá nhân chưa đăng ký chữ ký số thương mại.
</details>

<details>
<summary><b>2. Lỗi kết nối API (<code>HTTP 400</code>, <code>403</code>, <code>429</code>)</b></summary>
<br>
<ul>
  <li>Kiểm tra lại kết nối Internet.</li>
  <li>Đảm bảo API Key không dính khoảng trắng thừa và chưa hết hạn mức miễn phí (Quota) trên Google AI Studio.</li>
</ul>
</details>

<details>
<summary><b>3. Không chụp được vùng màn hình hoặc ảnh bị đen</b></summary>
<br>
Nếu cửa sổ chứa đề bài đang chạy bằng quyền Quản trị viên (Administrator), hãy chuột phải vào <code>SolverProV8.exe</code> và chọn <b>Run as administrator</b>.
</details>

---

<div align="center">

**© 2026 ThanhDevHub • All Rights Reserved**

</div>
