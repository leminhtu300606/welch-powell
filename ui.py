import tkinter as tk
from events import (
    on_canvas_click,
    on_canvas_drag,
    on_mouse_wheel,
    on_toolbar_button_release,
    toggle_mode,
    update_tool_button_styles,
)

def setup_interface(app):
    app.root.title("Thuật toán Welch-Powell")
    app.root.geometry("1100x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    tk.Label(
        app.toolbar,
        text="Công Cụ",
        font=("Arial", 11, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=10)

    app.node_btn = tk.Button(
        app.toolbar,
        text="+ Nút Mới",
        font=("Arial", 10, "bold"),
        bg="#3498db",
        fg="white",
        cursor="hand2",
        width=12,
        height=2
    )
    app.node_btn.pack(pady=10)
    app.node_btn.bind("<ButtonRelease-1>", lambda event: on_toolbar_button_release(app, event))

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=10)

    tk.Label(
        app.toolbar,
        text="Tác vụ:",
        font=("Arial", 10, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=5)

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
            command=lambda m=mode: toggle_mode(app, m)
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
        command=app.welsh_powell_coloring
    )
    app.run_btn.pack(pady=10)

    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

    app.canvas = tk.Canvas(
        canvas_frame,
        bg="lightblue",
        cursor="arrow"
    )

    app.canvas.pack(fill="both", expand=True)

    app.canvas.bind("<Button-1>", lambda event: on_canvas_click(app, event))
    app.canvas.bind("<B1-Motion>", lambda event: on_canvas_drag(app, event))
    
    app.canvas.bind("<MouseWheel>", lambda event: on_mouse_wheel(app, event))
    app.canvas.bind("<Button-4>", lambda event: on_mouse_wheel(app, event))
    app.canvas.bind("<Button-5>", lambda event: on_mouse_wheel(app, event))

    app.canvas.bind("<Control-0>", app.reset_zoom)
    app.root.bind("<Control-0>", app.reset_zoom)
