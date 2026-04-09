# Ứng Dụng Mô Phỏng Thuật Toán Đồ Thị (KMA GraphViz - Graph Algorithms Simulator)

![Python](https://img.shields.io/badge/Python-3.x-3776AB.svg?style=flat-square&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-E38B29.svg?style=flat-square)
![Algorithms](https://img.shields.io/badge/Algorithms-4_Supported-8E44AD.svg?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-27AE60.svg?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-2C3E50.svg?style=flat-square)

Đây là một ứng dụng giao diện đồ họa (GUI) chuyên nghiệp được phát triển bằng Python (Tkinter) nhằm mục đích giáo dục và trực quan hóa dữ liệu. Ứng dụng cho phép người dùng tự do vẽ các đồ thị, nhập trọng số và quan sát mô phỏng chạy từng bước của 4 bài toán đồ thị kinh điển.

## 🌟 Các tính năng nổi bật

* **4 Thuật toán cốt lõi:**
  1. **Welsh-Powell:** Tô màu đồ thị (Graph Coloring) với số màu tối thiểu.
  2. **Dijkstra:** Tìm đường đi ngắn nhất (Shortest Path). Hỗ trợ cả đồ thị vô hướng và đồ thị có hướng.
  3. **Kruskal:** Tìm Cây khung nhỏ nhất (MST) dựa trên việc duyệt cạnh.
  4. **Prim:** Tìm Cây khung nhỏ nhất (MST) dựa trên sự lan tỏa từ đỉnh bắt đầu.

* **🔥 Điểm nhấn công nghệ (Interactive Simulation):**
  * **Nhãn nổi thông minh (Floating Labels):** Hiển thị trực tiếp thông số `(khoảng cách, đỉnh trước)` lên từng đỉnh trên đồ thị theo thời gian thực (như một bảng tính động). Có thể Bật/Tắt để tránh rối mắt.
  * **Tương tác hai chiều (Time-travel):** Click vào một bước bất kỳ trên bảng lịch sử để "tua" lại đồ thị, xem chính xác trạng thái nhãn và đường đi tại thời điểm đó.
  * **Lưu vết thông minh:** Tùy chọn giữ lại giá trị lịch sử của các đỉnh đã chốt (hiển thị nền xám) để dễ dàng theo dõi toàn cảnh thuật toán.

* **Giao diện & Trải nghiệm (UI/UX):** * Không gian làm việc vô hạn: Kéo thả đỉnh, phóng to/thu nhỏ (Zoom), dịch chuyển vùng nhìn (Pan).
  * Tự động đánh nhãn (A, B, C...) hoặc (1, 2, 3...) và cho phép đổi tên đỉnh tự do. Không cho phép đặt tên trùng lặp.
  * Bẫy lỗi chặt chẽ: Chặn trọng số âm cho Dijkstra, chặn nối cạnh trùng lặp, bắt lỗi chọn thiếu đỉnh...

* **Quản lý File & An toàn dữ liệu:** * Hỗ trợ bộ phím tắt chuẩn: `Ctrl+N` (Mới), `Ctrl+O` (Mở), `Ctrl+S` (Lưu nhanh đè file cũ) và `Ctrl+Shift+S` (Lưu bản sao). 
  * Lưu trữ cấu trúc đồ thị dưới định dạng `.svg` (có nhúng JSON).
  * Tự động cảnh báo lưu file khi thoát ứng dụng hoặc tạo bản vẽ mới.

## 📂 Cấu trúc dự án

Dự án được thiết kế theo mô hình phân tách logic rõ ràng (MVC pattern):

```text
welch-powell/
├── algorithms/                
│   ├── dijkstra.py             # Thuật toán tìm đường đi ngắn nhất
│   ├── kruskal.py              # Thuật toán tìm cây khung nhỏ nhất 
│   ├── prim.py                 # Thuật toán tìm cây khung nhỏ nhất 
│   └── welsh_powell.py         # Thuật toán tô màu đồ thị
├── core/                       
│   ├── app_methods.py          # Quản lý state, đối tượng đồ thị và hệ thống vẽ Canvas
│   ├── events.py               # Bắt sự kiện click, kéo thả chuột, con lăn zoom
│   └── graph_actions.py        # Các thao tác CRUD (Thêm/Sửa/Xóa) đỉnh và cạnh
├── gui/                        
│   ├── dijkstra_ui.py          # Giao diện và bảng điều khiển cho Dijkstra
│   ├── kruskal_ui.py           # Giao diện và bảng điều khiển cho Kruskal
│   ├── prim_ui.py              # Giao diện và bảng điều khiển cho Prim
│   ├── ui.py                   # Bộ khung giao diện chung 
│   └── welsh_powell_ui.py      # Giao diện và bảng điều khiển cho Welsh-Powell
├── utils/                      
│   └── file_manager.py         # Xử lý đọc/ghi file định dạng SVG + JSON nhúng
└── main.py                     # Điểm khởi chạy ứng dụng (Entry point / Launcher)
```
## Donwload and Install: [.exe](https://www.mediafire.com/file/a42fqpew0tvve98/setupKMAGraphViz.exe/file)