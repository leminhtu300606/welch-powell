import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Chính - Trình Khởi Chạy")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Tâm của cửa sổ
        self.center_window()
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        
        title_label = tk.Label(
            header_frame,
            text="🚀 Trung Tâm Ứng Dụng",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Chọn ứng dụng bạn muốn chạy",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Ứng dụng tô màu đồ thị
        frame1 = tk.Frame(content_frame, bg="#ecf0f1", relief="raised", bd=2)
        frame1.pack(fill="x", pady=10)
        
        tk.Label(
            frame1,
            text="📊 Ứng dụng Tô Màu Đồ Thị - Welch-Powell",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(
            frame1,
            text="• Vẽ các nút hình tròn (mặc định trắng)\n• Vẽ cạnh nối giữa các nút\n• Áp dụng thuật toán Welch-Powell\n• Tô màu tự động với số màu tối thiểu",
            font=("Arial", 10),
            bg="#ecf0f1",
            justify="left"
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Button(
            frame1,
            text="▶ Chạy Ứng dụng Tô Màu Đồ Thị",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.run_drag_drop,
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(pady=10)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#34495e", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        tk.Label(
            footer_frame,
            text="Nhập Ctrl+Q để thoát | Phiên bản 1.0",
            font=("Arial", 9),
            bg="#34495e",
            fg="white"
        ).pack(pady=8)
        
        # Bind phím tắt
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        
        # Đặt focus
        self.root.focus()
    
    def center_window(self):
        """Đặt cửa sổ ở giữa màn hình"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run_drag_drop(self):
        """Chạy ứng dụng vẽ đồ thị"""
        try:
            # Lấy đường dẫn của file hiện tại
            current_dir = os.path.dirname(os.path.abspath(__file__))
            drag_drop_path = os.path.join(current_dir, "drag_drop.py")
            
            # Chạy ứng dụng trong background
            subprocess.Popen([sys.executable, drag_drop_path])
            messagebox.showinfo(
                "Khởi động",
                "Ứng dụng Đồ Thị đang được mở...\nVui lòng chờ một chút!"
            )
        except Exception as e:
            messagebox.showerror(
                "Lỗi",
                f"Không thể mở ứng dụng Đồ Thị:\n{str(e)}"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
