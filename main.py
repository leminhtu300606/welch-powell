"""main.py - Điểm khởi chạy ứng dụng Welsh-Powell."""

import tkinter as tk
from ui import setup_interface
from app_methods import AppMethods


class WelshPowellApp(AppMethods):
    def __init__(self, root):
        self.root = root
        self.init_state()
        setup_interface(self)


if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
