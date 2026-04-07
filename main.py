"""main.py - Điểm khởi chạy ứng dụng (Welsh-Powell hoặc Dijkstra)."""

import tkinter as tk
from gui.ui import setup_interface
from core.app_methods import AppMethods


class GraphApp(AppMethods):
    def __init__(self, root, mode):
        self.root = root
        self.algorithm_mode = mode  # "welsh_powell" hoặc "dijkstra"
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
    launcher.geometry("350x220")
    
    tk.Label(launcher, text="HỆ THỐNG MÔ PHỎNG ĐỒ THỊ", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=20)
    
    tk.Button(
        launcher, text="Thuật toán Tô màu (Welsh-Powell)", width=35, height=2,
        bg="#3498db", fg="white", font=("Arial", 10, "bold"), cursor="hand2",
        command=lambda: start_app("welsh_powell")
    ).pack(pady=5)
    
    tk.Button(
        launcher, text="Thuật toán Tìm đường (Dijkstra)", width=35, height=2,
        bg="#27ae60", fg="white", font=("Arial", 10, "bold"), cursor="hand2",
        command=lambda: start_app("dijkstra")
    ).pack(pady=5)
    
    launcher.mainloop()