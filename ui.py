import tkinter as tk
from tkinter import messagebox
from events import (
    on_canvas_click,
    on_canvas_drag,
    on_mouse_wheel,
    on_toolbar_button_release,
)
from graph_actions import apply_welsh_powell_coloring


def update_tool_button_styles(app):
    active_mode = app.mode_var.get()
    for mode, check in app.tool_checks.items():
        is_active = active_mode == mode
        app.tool_vars[mode].set(is_active)
        check.config(
            bg="#1f618d" if is_active else "#2c3e50",
            selectcolor="#1f618d" if is_active else "#34495e",
        )


def toggle_mode(app, mode):
    current_mode, mode_is_checked = app.mode_var.get(), app.tool_vars[mode].get()

    if mode_is_checked:
        app.mode_var.set(mode)
        for other_mode, var in app.tool_vars.items():
            var.set(other_mode == mode)
    elif current_mode == mode:
        app.mode_var.set("move")

    if app.mode_var.get() != "connect":
        app._clear_connection_highlight()

    update_tool_button_styles(app)


def run_coloring(app):
    result = apply_welsh_powell_coloring(app)
    if result is None:
        messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
        return

    max_color, color_groups = result
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


def setup_interface(app):
    app.root.title("Ứng dụng mô phỏng thuật toán Welch-Powell")
    app.root.geometry("1100x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    tk.Label(app.toolbar, text="Công Cụ", font=("Arial", 11, "bold"), bg="#2c3e50", fg="white").pack(pady=10)

    app.node_btn = tk.Button(
        app.toolbar,
        text="+ Nút Mới",
        font=("Arial", 10, "bold"),
        bg="#3498db",
        fg="white",
        cursor="hand2",
        width=12,
        height=2,
    )
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

    app.run_btn = tk.Button(
        app.toolbar,
        text="> Chạy",
        font=("Arial", 11, "bold"),
        bg="#27ae60",
        fg="white",
        cursor="hand2",
        width=12,
        height=2,
        command=lambda app=app: run_coloring(app),
    )
    app.run_btn.pack(pady=10)

    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

    app.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
    app.canvas.pack(fill="both", expand=True)

    app.canvas.bind("<Button-1>", lambda event: on_canvas_click(app, event))
    app.canvas.bind("<B1-Motion>", lambda event: on_canvas_drag(app, event))
    
    # Zoom bằng scroll wheel
    app.canvas.bind("<MouseWheel>", lambda event: on_mouse_wheel(app, event))  # Windows
    app.canvas.bind("<Button-4>", lambda event: on_mouse_wheel(app, event))     # Linux scroll up
    app.canvas.bind("<Button-5>", lambda event: on_mouse_wheel(app, event))     # Linux scroll down

