"""core/events.py - Xử lý sự kiện"""
from statistics import mode
from tkinter import messagebox, simpledialog
from core.graph_actions import (
    connect_nodes, delete_edge, delete_node
)


def _ask_positive_weight_vi(parent, title, prompt, initialvalue=None):
    """Nhập trọng số nguyên dương với thông báo lỗi tiếng Việt."""
    while True:
        raw_value = simpledialog.askstring(
            title,
            prompt,
            initialvalue="" if initialvalue is None else str(initialvalue),
            parent=parent,
        )

        if raw_value is None:
            return None

        raw_value = raw_value.strip()
        if raw_value == "":
            messagebox.showwarning("Lỗi nhập liệu", "Trọng số không được để trống.")
            continue

        try:
            weight = int(raw_value)
        except ValueError:
            messagebox.showwarning("Lỗi nhập liệu", "Trọng số phải là số nguyên.")
            continue

        if weight < 1:
            messagebox.showwarning("Lỗi nhập liệu", "Trọng số phải lớn hơn hoặc bằng 1.")
            continue

        return weight

def _get_next_label(app):
    """Sinh nhãn A, B, C..."""
    existing_labels = {str(node["label"]).upper() for node in app.nodes}
    for i in range(26):
        char = chr(65 + i)
        if char not in existing_labels:
            return char
    return f"V{len(app.nodes)}"

def on_canvas_click(app, event):
    mode = app.mode_var.get()
    selected_node = app.get_node_at(event.x, event.y)
    app.selected_node = selected_node

    if mode == "delete":
        if selected_node: delete_node(app, selected_node)
        return

    if mode == "connect":
        if not selected_node: return
        first = app.first_node_for_connection
        if first is None:
            app.first_node_for_connection = selected_node
            app.canvas.itemconfig(selected_node["circle"], width=4, outline="red")
            return
        if selected_node == first:
            app._clear_connection_highlight()
        else:
            weight = None
            if getattr(app, "algorithm_mode", "") in ["dijkstra", "prim", "kruskal"]:
                w_input = _ask_positive_weight_vi(
                    app.root,
                    "Nhập trọng số",
                    f"Nhập trọng số cho cạnh {first['label']} - {selected_node['label']}:",
                )
                if w_input is None:
                    app._clear_connection_highlight()
                    return
                weight = w_input
            ok, error_message = connect_nodes(app, first, selected_node, weight)
            if not ok: messagebox.showwarning("Lỗi", error_message)
            app._clear_connection_highlight()
        return

    if mode == "delete_edge":
        edge = app.get_edge_at(event.x, event.y)
        if edge: delete_edge(app, edge)
        else: messagebox.showwarning("Thông báo", "Không có cạnh tại đây!")
        return

    if mode == "edit_weight":
        edge = app.get_edge_at(event.x, event.y)
        if edge:
            n1, n2 = app.nodes[edge["node1_id"]]["label"], app.nodes[edge["node2_id"]]["label"]
            new_w = _ask_positive_weight_vi(
                app.root,
                "Sửa trọng số",
                f"Nhập trọng số mới cho cạnh {n1} - {n2}:",
                initialvalue=edge.get("weight", 1),
            )
            if new_w is not None:
                edge["weight"] = new_w
                app.render_graph()
        return

    if mode == "edit_label":
        if selected_node:
            new_label = simpledialog.askstring(
                "Sửa tên đỉnh", 
                f"Nhập tên/chữ cái mới cho đỉnh '{selected_node['label']}':", 
                initialvalue=selected_node['label'], 
                parent=app.root
            )
            if new_label and new_label.strip() != "":
                selected_node["label"] = new_label.strip()
                app.render_graph()
        return

    if mode == "dijkstra_select":
        if selected_node:
            if not hasattr(app, "dijkstra_nodes"): app.dijkstra_nodes = []
            if selected_node in app.dijkstra_nodes: return
            if len(app.dijkstra_nodes) >= 2:
                app.dijkstra_nodes = []
            
            app.dijkstra_nodes.append(selected_node)
            app.render_graph()
            if len(app.dijkstra_nodes) == 2:
                messagebox.showinfo("Thông báo", "Đã chọn xong điểm đầu và cuối.\nNhấn '> Tìm đường'")
        return
    # ================= PRIM SELECT EDGE =================
    if mode == "prim_select":
        edge = app.get_edge_at(event.x, event.y)
        if not edge:
            messagebox.showwarning("Thông báo", "Hãy click trực tiếp lên một cạnh để chọn cạnh bắt đầu.")
            return

        app.prim_start_edge = (edge["node1_id"], edge["node2_id"])
        app.highlighted_path = []
        app.highlighted_color = "#2980b9"
        app.highlighted_edges = [edge]
        app.render_graph()
        return
    
    if selected_node:
        app.canvas.itemconfig(selected_node["circle"], width=3)
        app.drag_start = (event.x, event.y)
        app.is_panning = False
    elif mode == "move":
        app.drag_start = (event.x, event.y)
        app.is_panning = True

def on_canvas_drag(app, event):
    if app.mode_var.get() != "move" or not app.drag_start: return
    dx, dy = event.x - app.drag_start[0], event.y - app.drag_start[1]
    if app.selected_node:
        app.selected_node["x"] += dx / app.scale
        app.selected_node["y"] += dy / app.scale
    elif app.is_panning:
        app.view_offset_x += dx
        app.view_offset_y += dy
    else: return
    app.drag_start = (event.x, event.y)
    app.render_graph()

def on_canvas_release(app, _event):
    app.drag_start = app.selected_node = None
    app.is_panning = False

def on_mouse_wheel(app, event):
    if event.num == 5 or event.delta < 0: app.zoom_out()
    elif event.num == 4 or event.delta > 0: app.zoom_in()

def on_toolbar_button_release(app, event):
    app.root.config(cursor="arrow")
    canvas_x, canvas_y = app.canvas.winfo_rootx(), app.canvas.winfo_rooty()
    canvas_w, canvas_h = app.canvas.winfo_width(), app.canvas.winfo_height()
    
    if (canvas_x <= event.x_root <= canvas_x + canvas_w and canvas_y <= event.y_root <= canvas_y + canvas_h):
        x, y = app._canvas_to_world(event.x_root - canvas_x, event.y_root - canvas_y)
    else:
        x, y = canvas_w // 2, canvas_h // 2
        
    # --- KIỂM TRA CHẾ ĐỘ ĐỂ CẤP PHÁT TÊN ĐỈNH TƯƠNG ỨNG ---
    if getattr(app, "algorithm_mode", "") in ["dijkstra", "prim", "kruskal"]:
        new_label = _get_next_label(app)
    else:
        max_label = max((int(node["label"]) for node in app.nodes if str(node["label"]).isdigit()), default=0)
        new_label = str(max_label + 1)
        
    app.create_node(x, y, new_label, "white")