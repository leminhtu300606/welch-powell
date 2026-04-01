"""
events.py - Xử lý sự kiện người dùng trên giao diện
Chứa tất cả các hàm xử lý các thao tác của người dùng: click, drag, scroll, ...
"""

from tkinter import messagebox


def zoom_in(app, factor=1.2):
    """Phong to (zoom in)."""
    app.scale *= factor
    app.redraw_edges()


def zoom_out(app, factor=1.2):
    """Thu nho (zoom out)."""
    app.scale /= factor
    if app.scale < 0.1:
        app.scale = 0.1
    app.redraw_edges()


def update_tool_button_styles(app):
    """Dong bo trang thai tick voi mode hien tai."""
    active_mode = app.mode_var.get()
    for mode, check in app.tool_checks.items():
        is_active = active_mode == mode
        app.tool_vars[mode].set(is_active)
        check.config(
            bg="#1f618d" if is_active else "#2c3e50",
            selectcolor="#1f618d" if is_active else "#34495e",
        )


def toggle_mode(app, mode):
    """Bat/tat che do thao tac bang checkbox; mac dinh la 'move'."""
    current_mode = app.mode_var.get()
    mode_is_checked = app.tool_vars[mode].get()

    if mode_is_checked:
        app.mode_var.set(mode)
        for other_mode, var in app.tool_vars.items():
            if other_mode != mode:
                var.set(False)
    elif current_mode == mode:
        app.mode_var.set("move")

    if app.mode_var.get() != "connect":
        app._clear_connection_highlight()

    update_tool_button_styles(app)


def on_canvas_click(app, event):
    """Xử lý khi click trên canvas"""
    app.selected_node = app.get_node_at(event.x, event.y)
    mode = app.mode_var.get()

    if mode == "delete" and app.selected_node:
        app.delete_node(app.selected_node)
    elif mode == "connect" and app.selected_node:
        if app.first_node_for_connection is None:
            app.first_node_for_connection = app.selected_node
            app.canvas.itemconfig(app.selected_node["circle"], width=4, outline="red")
        elif app.selected_node == app.first_node_for_connection:
            app._clear_connection_highlight()
        else:
            app.connect_nodes(app.first_node_for_connection, app.selected_node)
            app._clear_connection_highlight()
    elif mode == "delete_edge":
        edge = app.get_edge_at(event.x, event.y)
        if edge:
            app.delete_edge(edge)
        else:
            messagebox.showwarning("Thông báo", "Không có cạnh nào tại vị trí này!")
    elif app.selected_node:
        app.canvas.itemconfig(app.selected_node["circle"], width=3)
        app.drag_start = (event.x, event.y)


def on_canvas_drag(app, event):
    """Xử lý khi kéo chuột trên canvas"""
    if app.mode_var.get() == "move" and app.selected_node and app.drag_start:
        dwx = (event.x - app.drag_start[0]) / app.scale
        dwy = (event.y - app.drag_start[1]) / app.scale

        app.selected_node["x"] += dwx
        app.selected_node["y"] += dwy

        app.drag_start = (event.x, event.y)
        app.redraw_edges()


def on_mouse_wheel(app, event):
    """Xử lý zoom bằng scroll wheel"""
    if event.num == 5 or event.delta < 0:
        zoom_out(app)
    elif event.num == 4 or event.delta > 0:
        zoom_in(app)


def on_toolbar_button_release(app, event):
    """Xử lý khi thả nút từ toolbar"""
    app.root.config(cursor="arrow")

    canvas_x = app.canvas.winfo_rootx()
    canvas_y = app.canvas.winfo_rooty()
    canvas_width = app.canvas.winfo_width()
    canvas_height = app.canvas.winfo_height()

    inside_canvas = (canvas_x <= event.x_root <= canvas_x + canvas_width and
                    canvas_y <= event.y_root <= canvas_y + canvas_height)

    if inside_canvas:
        cx, cy = event.x_root - canvas_x, event.y_root - canvas_y
        x, y = app._canvas_to_world(cx, cy)
    else:
        x, y = canvas_width // 2, canvas_height // 2

    max_label = max([int(node["label"]) for node in app.nodes], default=0)
    app.create_node(x, y, str(max_label + 1), "white")
