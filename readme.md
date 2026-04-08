# Ứng Dụng Mô Phỏng Thuật Toán Đồ Thị (Graph Algorithms Simulator)

![Python](https://img.shields.io/badge/Python-3.x-3776AB.svg?style=flat-square&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-E38B29.svg?style=flat-square)
![Algorithms](https://img.shields.io/badge/Algorithms-4_Supported-8E44AD.svg?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-27AE60.svg?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-2C3E50.svg?style=flat-square)

Đây là một ứng dụng giao diện đồ họa (GUI) được phát triển bằng Python (Tkinter) nhằm mục đích giáo dục và trực quan hóa dữ liệu. Ứng dụng cho phép người dùng tự do vẽ các đồ thị, nhập trọng số và quan sát mô phỏng chạy từng bước của 4 bài toán đồ thị kinh điển.

## 🌟 Các tính năng nổi bật

* **4 Thuật toán cốt lõi:**
  1. **Welsh-Powell:** Tô màu đồ thị (Graph Coloring) với số màu tối thiểu.
  2. **Dijkstra:** Tìm đường đi ngắn nhất (Shortest Path) từ một đỉnh đến đỉnh đích. Hỗ trợ cả **đồ thị vô hướng** và **đồ thị có hướng**.
  3. **Kruskal:** Tìm Cây khung nhỏ nhất (Minimum Spanning Tree) dựa trên việc duyệt cạnh.
  4. **Prim:** Tìm Cây khung nhỏ nhất (Minimum Spanning Tree) dựa trên sự lan tỏa từ đỉnh.
* **Giao diện tương tác trực quan:** Kéo thả đỉnh, phóng to/thu nhỏ (Zoom), dịch chuyển vùng nhìn (Pan) đồ thị dễ dàng.
* **Tự động cấp phát nhãn:** Tự động đánh số (1, 2, 3...) hoặc chữ cái (A, B, C...) tùy theo thuật toán. Hỗ trợ công cụ đổi tên đỉnh tự do.
* **Mô phỏng thuật toán từng bước (Animation):** Hiển thị rõ ràng quá trình duyệt đồ thị, đổi màu đỉnh/cạnh với các mức tốc độ khác nhau. Tích hợp bảng (Treeview) hiển thị trạng thái tính toán động.
* **Quản lý File Chuyên Nghiệp:** * Hỗ trợ tạo mới (New), mở (Open), lưu nhanh (Save) và lưu thành bản sao (Save As). 
  * Lưu trữ đồ thị dưới định dạng `.svg` (có nhúng JSON để phục hồi trạng thái).
  * Tích hợp cảnh báo an toàn khi thoát ứng dụng hoặc tạo bản vẽ mới mà chưa lưu.
* **Bẫy lỗi thông minh:** Chặn nhập trọng số âm cho Dijkstra, cảnh báo khi nối trùng cạnh, cảnh báo khi đặt tên đỉnh trùng lặp.

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