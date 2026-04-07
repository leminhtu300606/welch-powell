"""ui.py - Khởi tạo giao diện, toolbar và luồng thao tác tô màu."""

import tkinter as tk
from tkinter import messagebox
from events import (
    on_canvas_click,
    on_canvas_drag,
    on_canvas_release,
    on_mouse_wheel,
    on_toolbar_button_release,
)
from graph_actions import apply_welsh_powell_coloring
from file_manager import load_graph_from_file, save_graph_to_file


ANIMATION_SPEED_LEVELS = [
    ("Chậm", 700),
    ("Vừa", 350),
    ("Nhanh", 180),
]


def update_tool_button_styles(app):
    active_mode = app.mode_var.get()
    for mode, check in app.tool_checks.items():
        is_active = active_mode == mode
        app.tool_vars[mode].set(is_active)
        bg = "#1f618d" if is_active else "#2c3e50"
        check.config(bg=bg, selectcolor=bg if is_active else "#34495e")


def toggle_mode(app, mode):
    current_mode = app.mode_var.get()
    if app.tool_vars[mode].get():
        app.mode_var.set(mode)
        for other_mode, var in app.tool_vars.items():
            var.set(other_mode == mode)
    elif current_mode == mode:
        app.mode_var.set("move")

    if app.mode_var.get() != "connect":
        app._clear_connection_highlight()

    update_tool_button_styles(app)


def cycle_animation_speed(app):
    labels = [label for label, _ in ANIMATION_SPEED_LEVELS]
    current = getattr(app, "animation_speed_label", "Vừa")
    next_index = (labels.index(current) + 1) % len(labels) if current in labels else 1
    next_label, next_delay = ANIMATION_SPEED_LEVELS[next_index]
    app.animation_speed_label = next_label
    app.animation_delay_ms = next_delay
    app.speed_btn.config(text=f"Tốc độ: {next_label}")


def run_coloring(app):
    if hasattr(app, "refresh_relationship_panel"):
        app.refresh_relationship_panel()

    result = apply_welsh_powell_coloring(app)
    if result is None:
        messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
        return

    max_color, color_groups, coloring_plan = result
    delay_ms = getattr(app, "animation_delay_ms", 350)
    app.run_btn.config(state="disabled")

    def show_result_window():
        text = "\n".join(
            [
                "Kết quả Welch-Powell:",
                "",
                f"Số màu cần thiết: {max_color + 1}",
                "",
                "Phân bổ màu:",
                *(f"Màu {idx}: {', '.join(nodes)}" for idx, nodes in enumerate(color_groups)),
            ]
        )

        result_window = tk.Toplevel(app.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        tk.Label(result_window, text=text, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

    def animate_step(index=0, previous_node=None):
        if previous_node is not None:
            app.canvas.itemconfig(previous_node["circle"], width=2, outline="black")

        if index >= len(coloring_plan):
            app.run_btn.config(state="normal")
            show_result_window()
            return

        current_node, color_value = coloring_plan[index]
        current_node["color"] = color_value
        app.canvas.itemconfig(current_node["circle"], fill=color_value, width=4, outline="#e67e22")
        app.root.after(delay_ms, lambda: animate_step(index + 1, current_node))

    animate_step()


def _refresh_relationship_panel(app):
    if not hasattr(app, "relation_listbox"):
        return

    app.relation_listbox.delete(0, tk.END)
    app.relationship_edge_refs = []

    for edge in app.edges:
        n1_id, n2_id = edge["node1_id"], edge["node2_id"]
        if n1_id >= len(app.nodes) or n2_id >= len(app.nodes):
            continue
        node1, node2 = app.nodes[n1_id], app.nodes[n2_id]
        app.relation_listbox.insert(tk.END, f"{node1['label']} {node2['label']}")
        app.relationship_edge_refs.append(edge)


def setup_interface(app):
    app.root.title("Ứng dụng mô phỏng thuật toán Welch-Powell")
    app.root.geometry("1100x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    tk.Label(app.toolbar, text="Công Cụ", font=("Arial", 11, "bold"), bg="#2c3e50", fg="white").pack(pady=10)

    def create_toolbar_button(text, bg, command, *, font=("Arial", 10, "bold"), height=2):
        return tk.Button(
            app.toolbar,
            text=text,
            font=font,
            bg=bg,
            fg="white",
            cursor="hand2",
            width=12,
            height=height,
            command=command,
        )

    app.node_btn = create_toolbar_button("+ Nút Mới", "#3498db", None)
    app.node_btn.pack(pady=10)
    app.node_btn.bind("<ButtonRelease-1>", lambda event: on_toolbar_button_release(app, event))

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=10)

    tk.Label(app.toolbar, text="Tác vụ:", font=("Arial", 10, "bold"), bg="#2c3e50", fg="white").pack(pady=5)

    # Keep move mode as default, but do not expose it in the toolbar.
    app.mode_var = tk.StringVar(value="move")
    app.tool_checks = {}
    app.tool_vars = {}

    def add_tool_check(text, mode):
        var = tk.BooleanVar(value=False)
        check = tk.Checkbutton(
            app.toolbar,
            text=text,
            variable=var,
            font=("Arial", 9, "bold"),
            bg="#2c3e50",
            fg="white",
            activebackground="#2c3e50",
            activeforeground="white",
            selectcolor="#34495e",
            cursor="hand2",
            anchor="w",
            command=lambda m=mode: toggle_mode(app, m),
        )
        check.pack(anchor="w", padx=10, pady=4, fill="x")
        app.tool_checks[mode] = check
        app.tool_vars[mode] = var

    add_tool_check("Xóa nút", "delete")
    add_tool_check("Nối nút", "connect")
    add_tool_check("Xóa cạnh", "delete_edge")

    update_tool_button_styles(app)

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=20, expand=True)

    app.open_btn = create_toolbar_button("📂 Mở", "#9b59b6", lambda: load_graph_from_file(app))
    app.open_btn.pack(pady=6)

    app.save_btn = create_toolbar_button("💾 Lưu", "#e74c3c", lambda: save_graph_to_file(app))
    app.save_btn.pack(pady=6)

    app.run_btn = create_toolbar_button("> Chạy", "#27ae60", lambda: run_coloring(app), font=("Arial", 11, "bold"))

    app.animation_speed_label = "Vừa"
    app.animation_delay_ms = 350
    app.speed_btn = create_toolbar_button(
        "Tốc độ: Vừa",
        "#f39c12",
        lambda: cycle_animation_speed(app),
        font=("Arial", 9, "bold"),
        height=1,
    )
    app.speed_btn.pack(pady=6)

    app.run_btn.pack(pady=10)

    relation_frame = tk.Frame(main_frame, bg="#ecf0f1", width=260, relief="sunken", bd=2)
    relation_frame.pack(side="right", fill="y", padx=5, pady=5)
    relation_frame.pack_propagate(False)

    tk.Label(
        relation_frame,
        text="Quan hệ giữa các nút",
        font=("Arial", 11, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50",
    ).pack(pady=(10, 6))

    app.relation_listbox = tk.Listbox(relation_frame, font=("Arial", 10), height=12)
    app.relation_listbox.pack(fill="x", padx=10, pady=(0, 8))
    app.relationship_edge_refs = []

    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

    app.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
    app.canvas.pack(fill="both", expand=True)

    app.canvas.bind("<Button-1>", lambda event: on_canvas_click(app, event))
    app.canvas.bind("<B1-Motion>", lambda event: on_canvas_drag(app, event))
    app.canvas.bind("<ButtonRelease-1>", lambda event: on_canvas_release(app, event))
    
    # Zoom bằng scroll wheel
    app.canvas.bind("<MouseWheel>", lambda event: on_mouse_wheel(app, event))  # Windows
    app.canvas.bind("<Button-4>", lambda event: on_mouse_wheel(app, event))     # Linux scroll up
    app.canvas.bind("<Button-5>", lambda event: on_mouse_wheel(app, event))     # Linux scroll down

    app.refresh_relationship_panel = lambda: _refresh_relationship_panel(app)
    app.refresh_relationship_panel()

