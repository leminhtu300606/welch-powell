import tkinter as tk


def setup_interface(app):
    app.root.title("Thuat toan Welch-Powell")
    app.root.geometry("1100x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    tk.Label(
        app.toolbar,
        text="Cong Cu",
        font=("Arial", 11, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=10)

    app.node_btn = tk.Button(
        app.toolbar,
        text="+ Nut Moi",
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
        text="Tac vu:",
        font=("Arial", 10, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=5)

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
            command=lambda m=mode: app.toggle_mode(m)
        )
        check.pack(anchor="w", padx=10, pady=4, fill="x")
        app.tool_checks[mode] = check
        app.tool_vars[mode] = var

    add_tool_check("Xoa nut", "delete")
    add_tool_check("Noi nut", "connect")
    add_tool_check("Xoa canh", "delete_edge")

    app.update_tool_button_styles()

    tk.Label(app.toolbar, bg="#2c3e50").pack(pady=20, expand=True)

    app.run_btn = tk.Button(
        app.toolbar,
        text="> Chay",
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

    h_scroll = tk.Scrollbar(
        canvas_frame,
        orient="horizontal",
        width=18,
        troughcolor="#e6e6e6",
        bg="#bdbdbd",
        activebackground="#9b9b9b"
    )
    v_scroll = tk.Scrollbar(
        canvas_frame,
        orient="vertical",
        width=18,
        troughcolor="#e6e6e6",
        bg="#bdbdbd",
        activebackground="#9b9b9b"
    )

    app.canvas = tk.Canvas(
        canvas_frame,
        bg="lightblue",
        cursor="arrow",
        xscrollcommand=h_scroll.set,
        yscrollcommand=v_scroll.set
    )

    h_scroll.config(command=app.canvas.xview)
    v_scroll.config(command=app.canvas.yview)

    app.h_scroll = h_scroll
    app.v_scroll = v_scroll

    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    app.canvas.pack(fill="both", expand=True)

    app.canvas.bind("<Button-1>", app.on_canvas_click)
    app.canvas.bind("<B1-Motion>", app.on_canvas_drag)
