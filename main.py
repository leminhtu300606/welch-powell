"""main.py - Điểm khởi chạy ứng dụng (Welsh-Powell, Dijkstra, Prim, Kruskal)."""

import tkinter as tk
from gui.ui import setup_interface
from core.app_methods import AppMethods


class GraphApp(AppMethods):
    def __init__(self, root, mode, on_back_callback=None):
        self.root = root
        self.algorithm_mode = mode  # thêm prim, kruskal
        self.on_back_callback = on_back_callback
        self.init_state()
        setup_interface(self)


def go_back_to_menu(root):
    """Đóng cửa sổ thuật toán và quay lại menu chính"""
    root.destroy()
    show_launcher()


def show_launcher():
    """Hiển thị cửa sổ chọn thuật toán"""
    launcher = tk.Tk()
    launcher.title("Chọn Thuật Toán")
    launcher.geometry("350x300")

    tk.Label(
        launcher,
        text="HỆ THỐNG MÔ PHỎNG ĐỒ THỊ",
        font=("Arial", 12, "bold"),
        fg="#2c3e50"
    ).pack(pady=15)

    # ================= WELSH POWELL =================
    tk.Button(
        launcher,
        text="Tô màu đồ thị (Welsh-Powell)",
        width=35, height=2,
        bg="#3498db", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app(launcher, "welsh_powell")
    ).pack(pady=5)

    # ================= DIJKSTRA =================
    tk.Button(
        launcher,
        text="Tìm đường ngắn nhất (Dijkstra)",
        width=35, height=2,
        bg="#27ae60", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app(launcher, "dijkstra")
    ).pack(pady=5)

    # ================= PRIM =================
    tk.Button(
        launcher,
        text="Cây khung nhỏ nhất (Prim)",
        width=35, height=2,
        bg="#f39c12", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app(launcher, "prim")
    ).pack(pady=5)

    # ================= KRUSKAL =================
    tk.Button(
        launcher,
        text="Cây khung nhỏ nhất (Kruskal)",
        width=35, height=2,
        bg="#9b59b6", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app(launcher, "kruskal")
    ).pack(pady=5)

    launcher.mainloop()


def start_app(launcher, mode):
    launcher.destroy()
    root = tk.Tk()
    root.state('zoomed')  # Hiển thị toàn màn hình
    app = GraphApp(root, mode, on_back_callback=lambda: go_back_to_menu(root))
    root.mainloop()


if __name__ == "__main__":
    show_launcher()