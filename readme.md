# Ứng Dụng Mô Phỏng Thuật Toán Đồ Thị (Graph Algorithms Simulator)

Đây là một ứng dụng giao diện đồ họa (GUI) được phát triển bằng Python (Tkinter) nhằm mục đích giáo dục và trực quan hóa dữ liệu. Ứng dụng cho phép người dùng tự do vẽ các đồ thị, nhập trọng số và quan sát mô phỏng chạy từng bước của 4 bài toán đồ thị kinh điển.

## 🌟 Các tính năng nổi bật

* **4 Thuật toán cốt lõi:**
  1. **Welsh-Powell:** Tô màu đồ thị (Graph Coloring) với số màu tối thiểu.
  2. **Dijkstra:** Tìm đường đi ngắn nhất (Shortest Path) từ một đỉnh đến đỉnh đích.
  3. **Kruskal:** Tìm Cây khung nhỏ nhất (Minimum Spanning Tree) dựa trên việc duyệt cạnh.
  4. **Prim:** Tìm Cây khung nhỏ nhất (Minimum Spanning Tree) dựa trên sự lan tỏa từ đỉnh.
* **Giao diện tương tác trực quan:** Kéo thả đỉnh, phóng to/thu nhỏ (Zoom), dịch chuyển vùng nhìn (Pan) đồ thị dễ dàng.
* **Tự động cấp phát nhãn:** Tự động đánh số (1, 2, 3...) hoặc chữ cái (A, B, C...) tùy theo thuật toán. Hỗ trợ công cụ đổi tên đỉnh tự do.
* **Mô phỏng thuật toán từng bước (Animation):** Hiển thị rõ ràng quá trình duyệt đồ thị, đổi màu đỉnh/cạnh với 3 mức tốc độ (Chậm, Vừa, Nhanh).
* **Bảng theo dõi thuật toán:** Tích hợp bảng (Treeview) hiển thị trạng thái tính toán động, cập nhật lịch sử duyệt y hệt cách làm bài tập trên giấy.
* **Lưu & Tải đồ thị (I/O):** Hỗ trợ lưu trữ đồ thị đang vẽ (bao gồm cả tọa độ, nhãn, cấu trúc và trọng số) dưới dạng file `.svg` để tiếp tục làm việc vào lần sau.

## 📂 Cấu trúc dự án

Dự án được thiết kế theo mô hình phân tách logic rõ ràng (MVC pattern):

```text
welch-powell/
├── algorithms/                 # "Bộ não" toán học (Không chứa code giao diện)
│   ├── dijkstra.py             # Thuật toán tìm đường đi ngắn nhất
│   ├── kruskal.py              # Thuật toán tìm cây khung nhỏ nhất (duyệt cạnh)
│   ├── prim.py                 # Thuật toán tìm cây khung nhỏ nhất (duyệt đỉnh)
│   └── welsh_powell.py         # Thuật toán tô màu đồ thị
├── core/                       # Xử lý tương tác cốt lõi
│   ├── app_methods.py          # Quản lý state, đối tượng đồ thị và hệ thống vẽ Canvas
│   ├── events.py               # Bắt sự kiện click, kéo thả chuột, con lăn zoom
│   └── graph_actions.py        # Các thao tác CRUD (Thêm/Sửa/Xóa) đỉnh và cạnh
├── gui/                        # Quản lý giao diện người dùng
│   ├── dijkstra_ui.py          # Giao diện và bảng điều khiển cho Dijkstra
│   ├── kruskal_ui.py           # Giao diện và bảng điều khiển cho Kruskal
│   ├── prim_ui.py              # Giao diện và bảng điều khiển cho Prim
│   ├── ui.py                   # Bộ khung giao diện chung (Cửa sổ chính, Toolbar, Canvas)
│   └── welsh_powell_ui.py      # Giao diện và bảng điều khiển cho Welsh-Powell
├── utils/                      # Các công cụ tiện ích hỗ trợ
│   └── file_manager.py         # Xử lý đọc/ghi file định dạng SVG + JSON nhúng
└── main.py                     # Điểm khởi chạy ứng dụng (Entry point / Launcher)