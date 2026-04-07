"""gui/ui.py - Khởi tạo bộ khung và phân nhánh giao diện."""
import tkinter as tk
from core.events import on_canvas_click, on_canvas_drag, on_canvas_release, on_mouse_wheel, on_toolbar_button_release
from utils.file_manager import load_graph_from_file, save_graph_to_file

from gui.welsh_powell_ui import setup_welsh_powell_ui
from gui.dijkstra_ui import setup_dijkstra_ui

ANIMATION_SPEED_LEVELS = [("Chậm", 1000), ("Vừa", 450), ("Nhanh", 180)]

def update_tool_button_styles(app):
    active_mode = app.mode_var.get()
    for mode, check in app.tool_checks.items():
        app.tool_vars[mode].set(active_mode == mode)
        bg = "#1f618d" if active_mode == mode else "#2c3e50"
        check.config(bg=bg, selectcolor=bg if active_mode == mode else "#34495e")

def toggle_mode(app, mode):
    if app.tool_vars[mode].get():
        app.mode_var.set(mode)
        for other_mode, var in app.tool_vars.items():
            var.set(other_mode == mode)
    elif app.mode_var.get() == mode:
        app.mode_var.set("move")

    if app.mode_var.get() != "connect":
        app._clear_connection_highlight()
    update_tool_button_styles(app)

def cycle_animation_speed(app):
    labels = [lbl for lbl, _ in ANIMATION_SPEED_LEVELS]
    current = getattr(app, "animation_speed_label", "Vừa")
    next_index = (labels.index(current) + 1) % len(labels) if current in labels else 1
    app.animation_speed_label, app.animation_delay_ms = ANIMATION_SPEED_LEVELS[next_index]
    app.speed_btn.config(text=f"Tốc độ: {app.animation_speed_label}")

def add_tool_check(app, text, mode):
    var = tk.BooleanVar(value=False)
    check = tk.Checkbutton(app.toolbar, text=text, variable=var, font=("Arial", 9, "bold"), bg="#2c3e50", fg="white", selectcolor="#34495e", cursor="hand2", anchor="w", command=lambda: toggle_mode(app, mode))
    check.pack(anchor="w", padx=10, pady=4, fill="x")
    app.tool_checks[mode], app.tool_vars[mode] = check, var

def create_toolbar_button(app, text, bg, command, height=2):
    return tk.Button(app.toolbar, text=text, bg=bg, fg="white", font=("Arial", 10, "bold"), cursor="hand2", width=12, height=height, command=command)

def setup_interface(app):
    title_text = "Tô màu Welsh-Powell" if app.algorithm_mode == "welsh_powell" else "Tìm đường Dijkstra"
    app.root.title(f"Mô phỏng: {title_text}")
    app.root.geometry("1150x700")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=140, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    app.mode_var = tk.StringVar(value="move")
    app.tool_checks, app.tool_vars = {}, {}

    tk.Label(app.toolbar, text="CÔNG CỤ", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(pady=10)
    node_btn = create_toolbar_button(app, "+ Nút Mới", "#3498db", None)
    node_btn.pack(pady=5)
    node_btn.bind("<ButtonRelease-1>", lambda e: on_toolbar_button_release(app, e))

    # Thanh PanedWindow giữ nguyên trỏ kéo thả <->
    app.paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashwidth=6, sashrelief="raised", bg="#bdc3c7", cursor="sb_h_double_arrow")
    app.paned_window.pack(fill="both", expand=True, side="left", padx=5, pady=5)

    # 1. Canvas (Bên trái): Ép về lại trỏ chuột mũi tên bình thường
    canvas_frame = tk.Frame(app.paned_window, cursor="arrow")
    app.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
    app.canvas.pack(fill="both", expand=True)
    app.paned_window.add(canvas_frame, stretch="always")

    # 2. Bảng kết quả (Bên phải): Ép về lại trỏ chuột mũi tên bình thường
    app.info_frame = tk.Frame(app.paned_window, bg="#ecf0f1", width=280,height=1200, relief="sunken", bd=2, cursor="arrow")
    app.info_frame.pack_propagate(False)
    app.paned_window.add(app.info_frame, stretch="never")

    if app.algorithm_mode == "welsh_powell":
        setup_welsh_powell_ui(app, add_tool_check, create_toolbar_button)
    else:
        setup_dijkstra_ui(app, add_tool_check, create_toolbar_button)

    app.run_btn.pack(pady=15)
    app.speed_btn = create_toolbar_button(app, "Tốc độ: Vừa", "#f39c12", lambda: cycle_animation_speed(app), height=1)
    app.speed_btn.pack(pady=5)
    create_toolbar_button(app, "📂 Mở", "#9b59b6", lambda: load_graph_from_file(app), height=1).pack(pady=2)
    create_toolbar_button(app, "💾 Lưu", "#e74c3c", lambda: save_graph_to_file(app), height=1).pack(pady=2)

    # Bind sự kiện
    app.canvas.bind("<Button-1>", lambda e: on_canvas_click(app, e))
    app.canvas.bind("<B1-Motion>", lambda e: on_canvas_drag(app, e))
    app.canvas.bind("<ButtonRelease-1>", lambda e: on_canvas_release(app, e))
    app.canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(app, e))
    
    update_tool_button_styles(app)