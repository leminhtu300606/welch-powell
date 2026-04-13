"""gui/ui.py - Khởi tạo bộ khung và phân nhánh giao diện."""
import tkinter as tk
from core.events import on_canvas_click, on_canvas_drag, on_canvas_release, on_mouse_wheel, on_toolbar_button_release
from utils.file_manager import prompt_save_if_needed,save_graph_as,create_new_graph, save_graph_to_file, load_graph_from_file
from gui.animation_utils import advance_manual_animation, cancel_scheduled_animation

from gui.welsh_powell_ui import setup_welsh_powell_ui
from gui.dijkstra_ui import setup_dijkstra_ui
from gui.prim_ui import setup_prim_ui
from gui.kruskal_ui import setup_kruskal_ui

DEFAULT_ANIMATION_DELAY_MS = 2000


def set_auto_mode(app, enabled):
    app.animation_auto_mode = enabled
    app.animation_delay_ms = DEFAULT_ANIMATION_DELAY_MS if enabled else None
    if hasattr(app, "auto_btn"):
        app.auto_btn.config(text="Tự động: Bật" if enabled else "Tự động: Tắt")

    if enabled:
        advance_manual_animation(app)
    else:
        # Khi chuyển sang tay, giữ lại bước đang hẹn để click tiếp tục đúng chỗ.
        cancel_scheduled_animation(app, keep_as_pending=True)


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


def add_tool_check(app, text, mode):
    var = tk.BooleanVar(value=False)
    check = tk.Checkbutton(
        app.toolbar,
        text=text,
        variable=var,
        font=("Arial", 9, "bold"),
        bg="#2c3e50",
        fg="white",
        selectcolor="#34495e",
        cursor="hand2",
        anchor="w",
        command=lambda: toggle_mode(app, mode)
    )
    check.pack(anchor="w", padx=10, pady=4, fill="x")
    app.tool_checks[mode], app.tool_vars[mode] = check, var


def create_toolbar_button(app, text, bg, command, height=2):
    return tk.Button(
        app.toolbar,
        text=text,
        bg=bg,
        fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
        width=12,
        height=height,
        command=command
    )


def setup_interface(app):

    def handle_canvas_click(event):
        # Ở chế độ tay, click vào canvas sẽ đi tiếp 1 bước nếu đang chờ.
        if not getattr(app, "animation_auto_mode", False) and getattr(app, "pending_animation_step", None) is not None:
            advance_manual_animation(app)
            return
        on_canvas_click(app, event)

    # ===== TITLE =====
    if app.algorithm_mode == "welsh_powell":
        title_text = "Tô màu Welsh-Powell"
    elif app.algorithm_mode == "dijkstra":
        title_text = "Tìm đường Dijkstra"
    elif app.algorithm_mode == "prim":
        title_text = "Cây khung nhỏ nhất (Prim)"
    elif app.algorithm_mode == "kruskal":
        title_text = "Cây khung nhỏ nhất (Kruskal)"
    else:
        title_text = "Graph App"

    app.root.title(f"Mô phỏng: {title_text}")

    main_frame = tk.Frame(app.root)
    main_frame.pack(fill="both", expand=True)

    # ===== TOOLBAR =====
    app.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=140, relief="sunken", bd=2)
    app.toolbar.pack(side="left", fill="y", padx=5, pady=5)
    app.toolbar.pack_propagate(False)

    app.mode_var = tk.StringVar(value="move")
    app.tool_checks, app.tool_vars = {}, {}

    tk.Label(app.toolbar, text="CÔNG CỤ", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(pady=10)

    node_btn = create_toolbar_button(app, "+ Nút Mới", "#3498db", None)
    node_btn.pack(pady=5)
    node_btn.bind("<ButtonRelease-1>", lambda e: on_toolbar_button_release(app, e))

    # ===== LAYOUT =====
    app.paned_window = tk.PanedWindow(
        main_frame,
        orient=tk.HORIZONTAL,
        sashwidth=6,
        sashrelief="raised",
        bg="#bdc3c7",
        cursor="sb_h_double_arrow"
    )
    app.paned_window.pack(fill="both", expand=True, side="left", padx=5, pady=5)

    # ===== CANVAS =====
    canvas_frame = tk.Frame(app.paned_window, cursor="arrow")
    app.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
    app.canvas.pack(fill="both", expand=True)
    app.paned_window.add(canvas_frame, stretch="always")

    # ===== INFO PANEL =====
    app.info_frame = tk.Frame(
        app.paned_window,
        bg="#ecf0f1",
        width=280,
        height=1200,
        relief="sunken",
        bd=2,
        cursor="arrow"
    )
    app.info_frame.pack_propagate(False)
    app.paned_window.add(app.info_frame, stretch="never")

    # ===== CHỌN UI THEO THUẬT TOÁN =====
    if app.algorithm_mode == "welsh_powell":
        setup_welsh_powell_ui(app, add_tool_check, create_toolbar_button)

    elif app.algorithm_mode == "dijkstra":
        setup_dijkstra_ui(app, add_tool_check, create_toolbar_button)

    elif app.algorithm_mode == "prim":
        setup_prim_ui(app, add_tool_check, create_toolbar_button)

    elif app.algorithm_mode == "kruskal":
        setup_kruskal_ui(app, add_tool_check, create_toolbar_button)
    # --- CHỨC NĂNG THOÁT AN TOÀN ---
    def on_closing():
        if prompt_save_if_needed(app):
            app.root.destroy() # Chỉ đóng cửa sổ khi hàm trả về True

    # Gắn sự kiện khi bấm nút X đỏ của Windows
    app.root.protocol("WM_DELETE_WINDOW", on_closing)

    # ===== COMMON BUTTON =====
    app.run_btn.pack(pady=15)

    app.animation_auto_mode = False
    app.animation_delay_ms = None
    app.pending_animation_step = None
    app.animation_after_id = None
    app.scheduled_next_step = None

    speed_frame = tk.Frame(app.toolbar, bg="#2c3e50")
    speed_frame.pack(fill="x", padx=8, pady=(5, 2))

    tk.Label(
        speed_frame,
        text="Chế độ chạy",
        bg="#2c3e50",
        fg="white",
        font=("Arial", 9, "bold"),
        anchor="w",
    ).pack(fill="x")

    app.auto_btn = tk.Button(
        speed_frame,
        text="Tự động: Tắt",
        bg="#f39c12",
        fg="white",
        font=("Arial", 9, "bold"),
        cursor="hand2",
        width=14,
        height=1,
        command=lambda: set_auto_mode(app, not getattr(app, "animation_auto_mode", False)),
    )
    app.auto_btn.pack(fill="x", pady=(4, 0))

    app.root.bind("<space>", lambda _event: advance_manual_animation(app))

    create_toolbar_button(app, "Mới", "#54b5e6" ,lambda: create_new_graph(app),height=1).pack(pady=2)
    create_toolbar_button(app, "Mở", "#9b59b6", lambda: load_graph_from_file(app), height=1).pack(pady=2)
    create_toolbar_button(app, "Lưu", "#e74c3c", lambda: save_graph_to_file(app), height=1).pack(pady=2)
    # Đây là một tính năng ẩn: create_toolbar_button(app, "Save as...", "#ee2748", lambda: save_graph_as(app), height=1).pack(pady=2)
    app.root.bind("<Control-n>", lambda event: create_new_graph(app))
    app.root.bind("<Control-o>", lambda event: load_graph_from_file(app))
    app.root.bind("<Control-s>", lambda event: save_graph_to_file(app))
    app.root.bind("<Control-Shift-s>", lambda event: save_graph_as(app))
    # ===== BACK BUTTON =====
    create_toolbar_button(app, "⬅ Quay Lại", "#34495e", lambda: app.on_back_callback(), height=1).pack(pady=2, side="bottom")

    # ===== EVENTS =====
    app.canvas.bind("<Button-1>", handle_canvas_click)
    app.canvas.bind("<B1-Motion>", lambda e: on_canvas_drag(app, e))
    app.canvas.bind("<ButtonRelease-1>", lambda e: on_canvas_release(app, e))
    app.canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(app, e))

    update_tool_button_styles(app)