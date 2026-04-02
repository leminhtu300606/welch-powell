"""
events.py - Xử lý sự kiện người dùng trên giao diện
Chứa tất cả các hàm xử lý các thao tác của người dùng: click, drag, scroll, ...
"""

from tkinter import messagebox
from graph_actions import connect_nodes, delete_edge, delete_node


def on_canvas_click(app, event):
    """Xử lý khi click trên canvas"""
    mode = app.mode_var.get()
    app.selected_node = app.get_node_at(event.x, event.y)

    if mode == "delete":
        if app.selected_node:
            delete_node(app, app.selected_node)
        return

    if mode == "connect":
        if not app.selected_node:
            return
        if app.first_node_for_connection is None:
            app.first_node_for_connection = app.selected_node
            app.canvas.itemconfig(app.selected_node["circle"], width=4, outline="red")
        elif app.selected_node == app.first_node_for_connection:
            app._clear_connection_highlight()
        else:
            ok, error_message = connect_nodes(app, app.first_node_for_connection, app.selected_node)
            if not ok:
                messagebox.showwarning("Lỗi", error_message)
            app._clear_connection_highlight()
        return

    if mode == "delete_edge":
        edge = app.get_edge_at(event.x, event.y)
        if edge:
            delete_edge(app, edge)
        else:
            messagebox.showwarning("Thông báo", "Không có cạnh nào tại vị trí này!")
        return

    if app.selected_node:
        app.canvas.itemconfig(app.selected_node["circle"], width=3)
        app.drag_start = (event.x, event.y)


def on_canvas_drag(app, event):
    """Xử lý khi kéo chuột trên canvas"""
    if app.mode_var.get() == "move" and app.selected_node and app.drag_start:
        dx = (event.x - app.drag_start[0]) / app.scale
        dy = (event.y - app.drag_start[1]) / app.scale
        app.selected_node["x"] += dx
        app.selected_node["y"] += dy

        app.drag_start = (event.x, event.y)
        app.redraw_edges()


def on_mouse_wheel(app, event):
    """Xử lý zoom bằng scroll wheel"""
    if event.num == 5 or event.delta < 0:
        app.zoom_out()
    elif event.num == 4 or event.delta > 0:
        app.zoom_in()


def on_toolbar_button_release(app, event):
    """Xử lý khi thả nút từ toolbar"""
    app.root.config(cursor="arrow")

    canvas_x = app.canvas.winfo_rootx()
    canvas_y = app.canvas.winfo_rooty()
    canvas_width = app.canvas.winfo_width()
    canvas_height = app.canvas.winfo_height()

    inside_canvas = (
        canvas_x <= event.x_root <= canvas_x + canvas_width
        and canvas_y <= event.y_root <= canvas_y + canvas_height
    )

    x, y = (
        app._canvas_to_world(event.x_root - canvas_x, event.y_root - canvas_y)
        if inside_canvas
        else (canvas_width // 2, canvas_height // 2)
    )

    max_label = max((int(node["label"]) for node in app.nodes), default=0)
    app.create_node(x, y, str(max_label + 1), "white")
