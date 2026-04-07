"""main.py - Điểm khởi chạy ứng dụng (Welsh-Powell, Dijkstra, Prim, Kruskal)."""

import tkinter as tk
from gui.ui import setup_interface
from core.app_methods import AppMethods


class GraphApp(AppMethods):
    def __init__(self, root, mode):
        self.root = root
        self.algorithm_mode = mode  # thêm prim, kruskal
        self.init_state()
        setup_interface(self)


def start_app(mode):
    launcher.destroy()
    root = tk.Tk()
    app = GraphApp(root, mode)
    root.mainloop()


if __name__ == "__main__":
    launcher = tk.Tk()
    launcher.title("Chọn Thuật Toán")
    launcher.geometry("350x300")  # tăng chiều cao

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
        command=lambda: start_app("welsh_powell")
    ).pack(pady=5)

    # ================= DIJKSTRA =================
    tk.Button(
        launcher,
        text="Tìm đường ngắn nhất (Dijkstra)",
        width=35, height=2,
        bg="#27ae60", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app("dijkstra")
    ).pack(pady=5)

    # ================= PRIM =================
    tk.Button(
        launcher,
        text="Cây khung nhỏ nhất (Prim)",
        width=35, height=2,
        bg="#f39c12", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app("prim")
    ).pack(pady=5)

    # ================= KRUSKAL =================
    tk.Button(
        launcher,
        text="Cây khung nhỏ nhất (Kruskal)",
        width=35, height=2,
        bg="#9b59b6", fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        command=lambda: start_app("kruskal")
    ).pack(pady=5)

    launcher.mainloop()