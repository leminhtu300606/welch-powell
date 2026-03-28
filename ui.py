import tkinter as tk


def setup_interface(app):
    app.root.title("Thuật toán Welch-Powell ")
    app.root.geometry("1100x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    tk.Label(
        app.toolbar,
        text="🛠️ Công Cụ",
        font=("Arial", 11, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=10)

    app.node_btn = tk.Button(
        app.toolbar,
        text="➕ Nút Mới",
        font=("Arial", 10, "bold"),
        bg="#3498db",
        fg="white",
        cursor="hand2",
        width=12,
        height=2
    )
    app.node_btn.pack(pady=10)
    app.node_btn.bind("<Button-1>", app.on_toolbar_button_press)
    app.node_btn.bind("<B1-Motion>", app.on_toolbar_button_drag)
    app.node_btn.bind("<ButtonRelease-1>", app.on_toolbar_button_release)

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=10)

    tk.Label(
        app.toolbar,
        text="Chế độ:",
        font=("Arial", 10, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=5)

    app.mode_var = tk.StringVar(value="move")

    tk.Radiobutton(
        app.toolbar, text="Di chuyển",
        variable=app.mode_var, value="move",
        bg="#2c3e50", fg="white", selectcolor="#34495e",
        font=("Arial", 9)
    ).pack(anchor="w", padx=10)

    tk.Radiobutton(
        app.toolbar, text="Xóa nút",
        variable=app.mode_var, value="delete",
        bg="#2c3e50", fg="white", selectcolor="#34495e",
        font=("Arial", 9)
    ).pack(anchor="w", padx=10)

    tk.Radiobutton(
        app.toolbar, text="Nối nút",
        variable=app.mode_var, value="connect",
        bg="#2c3e50", fg="white", selectcolor="#34495e",
        font=("Arial", 9)
    ).pack(anchor="w", padx=10)

    tk.Radiobutton(
        app.toolbar, text="Xóa cạnh",
        variable=app.mode_var, value="delete_edge",
        bg="#2c3e50", fg="white", selectcolor="#34495e",
        font=("Arial", 9)
    ).pack(anchor="w", padx=10)

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=20, expand=True)

    app.run_btn = tk.Button(
        app.toolbar,
        text="▶ Chạy",
        font=("Arial", 11, "bold"),
        bg="#27ae60",
        fg="white",
        cursor="hand2",
        width=12,
        height=2,
        command=app.on_apply_algorithm
    )
    app.run_btn.pack(pady=10)

    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

    app.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
    app.canvas.pack(fill="both", expand=True)

    app.canvas.bind("<Button-1>", app.on_canvas_click)
    app.canvas.bind("<B1-Motion>", app.on_canvas_drag)
    app.canvas.bind("<Control-Button-1>", app.on_ctrl_click)
    app.canvas.bind("<Button-3>", app.on_right_click)
