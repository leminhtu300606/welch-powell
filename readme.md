# Ứng Dụng Mô Phỏng Thuật Toán Đồ Thị (Graph Algorithms Simulator)

Đây là một ứng dụng giao diện đồ họa (GUI) được viết bằng Python (Tkinter) nhằm mục đích giáo dục và học tập. Ứng dụng cho phép người dùng tự do vẽ các đồ thị và quan sát mô phỏng chạy từng bước của 2 bài toán kinh điển: **Tô màu đồ thị (Welsh-Powell)** và **Tìm đường đi ngắn nhất (Dijkstra)**.

## 🌟 Các tính năng nổi bật

* **Giao diện tương tác trực quan:** Kéo thả, phóng to/thu nhỏ (Zoom), dịch chuyển vùng nhìn (Pan) đồ thị dễ dàng.
* **Tự động cấp phát nhãn:** Tự động đánh số (1, 2, 3...) cho chế độ Welsh-Powell và chữ cái (A, B, C...) cho chế độ Dijkstra. Hỗ trợ chỉnh sửa tên đỉnh tự do.
* **Mô phỏng thuật toán từng bước (Animation):** Hiển thị rõ ràng quá trình duyệt đồ thị, đổi màu đỉnh/cạnh với 3 mức tốc độ (Chậm, Vừa, Nhanh).
* **Bảng chạy Dijkstra chuẩn giáo trình:** * Cột tự động sắp xếp theo thứ tự lan tỏa của thuật toán.
  * Hiển thị dấu `-` cho đỉnh đã chốt, và dấu `*` cho đỉnh đang xét.
  * Hỗ trợ tìm và hiển thị **Đa đường đi (Multiple shortest paths)**.
* **Lưu & Tải đồ thị (I/O):** Hỗ trợ lưu trữ đồ thị đang vẽ (bao gồm cả trọng số và cấu trúc) dưới dạng file `.svg` để mở lại vào lần sau.

## 📂 Cấu trúc dự án

Dự án được thiết kế theo mô hình phân tách logic rõ ràng (MVC pattern):

```text
welch-powell/
├── main.py                     # File khởi chạy ứng dụng (Entry point)
├── file_manager.py             # Xử lý lưu/tải đồ thị dưới định dạng SVG
├── algorithms/                 # Chứa "Bộ não" thuần toán học
│   ├── dijkstra.py             # Logic thuật toán Dijkstra
│   └── welsh_powell.py         # Logic thuật toán Welsh-Powell
├── core/                       # Xử lý tương tác cốt lõi
│   ├── app_methods.py          # Quản lý state, đối tượng đồ thị và vẽ Canvas
│   ├── events.py               # Bắt sự kiện click, kéo thả, con lăn chuột
│   └── graph_actions.py        # Các thao tác CRUD (Thêm/Sửa/Xóa) nút và cạnh
└── gui/                        # Quản lý giao diện người dùng
    ├── ui.py                   # Bộ khung giao diện chung (Thanh công cụ, Canvas)
    ├── dijkstra_ui.py          # Khung tính năng và bảng kết quả cho Dijkstra
    └── welsh_powell_ui.py      # Khung tính năng và danh sách cho Welsh-Powell