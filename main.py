import tkinter as tk
from ui import setup_interface
from app_methods import AppMethods

class WelshPowellApp(AppMethods):
    def __init__(self, root):
        self.root = root
        self.nodes = []
        self.selected_node = None
        self.drag_start = None

        self.edges = []
        self.first_node_for_connection = None

        self.scale = 1.0

        setup_interface(self)

if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
