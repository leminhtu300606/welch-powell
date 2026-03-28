import tkinter as tk
from tkinter import messagebox
import string
from node_manager import NodeManager
from edge_manager import EdgeManager
from drag_manager import DragManager
from stats import ColoringStats

class WelshPowellApp(NodeManager, EdgeManager, DragManager, ColoringStats):
    def __init__(self, root):
        self.root = root
        self.root.title("Thuật toán Welch-Powell ")
        self.root.geometry("1100x700")

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
        self.toolbar.pack(side="left", fill="y", padx=5, pady=5)
        self.toolbar.pack_propagate(False)

        tk.Label(
            self.toolbar,
            text="🛠️ Công Cụ",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=10)

        self.node_btn = tk.Button(
            self.toolbar,
            text="➕ Nút Mới",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            width=12,
            height=2
        )
        self.node_btn.pack(pady=10)
        self.node_btn.bind("<Button-1>", self.on_toolbar_button_press)
        self.node_btn.bind("<B1-Motion>", self.on_toolbar_button_drag)
        self.node_btn.bind("<ButtonRelease-1>", self.on_toolbar_button_release)

        tk.Label(self.toolbar, bg="#2c3e50").pack(pady=10)

        tk.Label(
            self.toolbar,
            text="Chế độ:",
            font=("Arial", 10, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=5)

        self.mode_var = tk.StringVar(value="move")

        tk.Radiobutton(
            self.toolbar, text="Di chuyển",
            variable=self.mode_var, value="move",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)

        tk.Radiobutton(
            self.toolbar, text="Xóa nút",
            variable=self.mode_var, value="delete",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)

        tk.Radiobutton(
            self.toolbar, text="Nối nút",
            variable=self.mode_var, value="connect",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)

        tk.Radiobutton(
            self.toolbar, text="Xóa cạnh",
            variable=self.mode_var, value="delete_edge",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)

        tk.Label(self.toolbar, bg="#2c3e50").pack(pady=20, expand=True)

        self.run_btn = tk.Button(
            self.toolbar,
            text="▶ Chạy",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            width=12,
            height=2,
            command=self.on_apply_algorithm
        )
        self.run_btn.pack(pady=10)

        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
        self.canvas.pack(fill="both", expand=True)

        self.info_label = tk.Label(
            self.root,
            text="💡 Kéo 'Nút Mới' từ toolbar vào canvas | Chọn chế độ: Di chuyển (kéo nút), Xóa nút (click nút), Nối nút (click 2 nút), Xóa cạnh (click cạnh) | ▶ để chạy thuật toán",
            bg="lightyellow",
            padx=10,
            pady=8,
            wraplength=1000,
            justify="left"
        )
        self.info_label.pack(fill="x")

        self.nodes = []
        self.selected_node = None
        self.drag_start = None

        self.edges = []
        self.first_node_for_connection = None

        self.dragging_from_toolbar = False

        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B88B", "#81ECEC"
        ]

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Control-Button-1>", self.on_ctrl_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.create_node(200, 150, "A", "white")
        self.create_node(400, 150, "B", "white")
        self.create_node(600, 150, "C", "white")
