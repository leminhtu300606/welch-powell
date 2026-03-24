# 🎨 Ứng dụng Tô Màu Đồ Thị - Welch-Powell

## Giới thiệu
Đây là ứng dụng giúp bạn vẽ và tô màu đồ thị bằng **thuật toán Welch-Powell** - một thuật toán tham lam để tô màu đồ thị với số lượng màu tối thiểu.

## Cài đặt

### Yêu cầu
- Python 3.x
- tkinter (thường được cài mặc định với Python)

### Chạy ứng dụng
```bash
# Chạy trình khởi chạy chính
python main.py

# Hoặc chạy ứng dụng Welch-Powell trực tiếp
python drag_drop.py
```

## Hướng Dẫn Sử Dụng

### 1️⃣ Tạo Nút (Đỉnh của đồ thị)
- **Click vào vùng trống** trên canvas
- Một nút hình tròn **màu trắng** sẽ xuất hiện
- Nút được tự động đặt tên: **A, B, C, D, E, ...**
- Mặc định, chữ trên nút là **màu đen**

### 2️⃣ Kéo Di Chuyển Nút
- **Click và kéo nút** để di chuyển vị trí
- Tất cả các cạnh nối sẽ tự động cập nhật vị trí

### 3️⃣ Vẽ Cạnh (Liên Kết giữa các Nút)
- **Giữ Ctrl + Click** vào nút thứ nhất
- **Giữ Ctrl + Click** vào nút thứ hai
- Một đường nối giữa 2 nút sẽ được tạo
- Bậc (số cạnh) của mỗi nút sẽ được cập nhật tự động

### 4️⃣ Xóa Cạnh
- **Right-click (Click chuột phải)** vào đường nối
- Chọn **"Có"** để xác nhận xóa
- Bậc của các nút sẽ được cập nhật

### 5️⃣ Xóa Nút
- **Double-click (Click kép)** vào nút
- Nút sẽ bị xóa cùng tất cả các cạnh liên quan

### 6️⃣ Áp Dụng Thuật Toán Welch-Powell ⭐
- **Nhấn SPACE** (phím cách) trên bàn phím
- Ứng dụng sẽ:
  1. **Sắp xếp** các nút theo bậc (**giảm dần**)
  2. **Gán màu** cho mỗi nút tối ưu
  3. **Hiển thị kết quả** gồm:
     - Tên nút và màu được gán
     - **Số lượng màu tối thiểu** cần thiết

## Thuật Toán Welch-Powell

### Nguyên Tắc Hoạt Động
1. **Bước 1**: Sắp xếp các đỉnh theo bậc **giảm dần** (nút có nhiều cạnh nhất lên trước)
2. **Bước 2**: Gán màu đầu tiên cho đỉnh có bậc cao nhất
3. **Bước 3**: Cho mỗi đỉnh tiếp theo:
   - Tìm tất cả **màu đã dùng** bởi các đỉnh **lân cận**
   - Gán **màu nhỏ nhất** chưa được sử dụng
4. **Bước 4**: Lặp lại cho đến hết tất cả các đỉnh

### Ưu Điểm
✅ Nhanh và hiệu quả (độ phức tạp O(n²))  
✅ Cho kết quả tốt cho hầu hết các đồ thị  
✅ Dễ hiểu và dễ cài đặt  

### Hạn Chế
⚠️ Không đảm bảo số màu **tối ưu** trong mọi trường hợp (NP-hard)  
⚠️ Kết quả phụ thuộc vào **thứ tự sắp xếp** ban đầu  

## Ký Hiệu & Giao Diện

| Ký Hiệu | Ý Nghĩa |
|---------|---------|
| 🔵 | Nút (đỉnh) của đồ thị |
| ━━ | Cạnh nối giữa 2 nút |
| 🎨 | Màu được gán bởi thuật toán |

## Ví Dụ Minh Họa

### Ví dụ 1: Đồ thị tam giác (K3)
```
Nút:        A --- B
            |   /
            | /
            C

Bậc:        A: 2, B: 2, C: 2
Kết quả:    3 màu cần thiết
            A: Màu 1, B: Màu 2, C: Màu 3
```

### Ví dụ 2: Đồ thị sao
```
Nút:          B
              |
          A---D---C
              |
              E

Bậc:        D: 4, A: 1, B: 1, C: 1, E: 1
Kết quả:    2 màu cần thiết
            D: Màu 1, A/B/C/E: Màu 2
```

## Lưu Ý Quan Trọng

⚠️ **Cảnh báo**: Không tạo nhiều cạnh lặp lại (cạnh kép) giữa cùng 2 nút  
⚠️ **Cảnh báo**: Không tạo cạnh tự nối (vòng lặp) từ nút đến chính nó  
✅ **Mẹo**: Sắp xếp các nút có bậc cao gần biên canvas để dễ quản lý

## Các Phím Tắt

| Phím | Tác Vụ |
|------|--------|
| Click | Tạo nút mới |
| Kéo chuột | Di chuyển nút |
| Ctrl + Click | Tạo cạnh (2 lần) |
| Right-click | Xóa cạnh |
| Double-click | Xóa nút |
| **SPACE** | **Áp dụng Welch-Powell** |

## Xử Lý Sự Cố

### Vấn đề: Không thấy cửa sổ ứng dụng
**Giải pháp**: 
- Kiểm tra thanh tác vụ (taskbar)
- Bấm **Alt + Tab** để chuyển cửa sổ
- Có thể cửa sổ nằm ngoài màn hình

### Vấn đề: Thuật toán chạy chậm
**Giải pháp**:
- Giảm số lượng nút (cố gắng < 50 nút)
- Đồ thị quá lớn có thể chạy chậm

### Vấn đề: Cạnh không vẽ đúng
**Giải pháp**:
- Xóa cạnh cũ (right-click) và vẽ lại
- Đảm bảo CTRL được giữ khi click

## Tác Giả
Phát triển với ❤️ bằng Python & Tkinter

## Phiên Bản
v1.0 - 2026
