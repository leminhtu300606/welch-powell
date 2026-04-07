"""core/events.py - Xử lý sự kiện"""
from tkinter import messagebox, simpledialog
from core.graph_actions import connect_nodes, delete_edge, delete_node

def _get_next_label(app):
    """Hàm tự động sinh nhãn chữ cái A, B, C... cho đỉnh mới (Dành cho Dijkstra)"""
    existing_labels = {str(node["label"]).upper() for node in app.nodes}
    for i in range(26):
        char = chr(65 + i) # Từ A đến Z
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
            weight = 1
            if getattr(app, "algorithm_mode", "") == "dijkstra":
                w_input = simpledialog.askinteger("Trọng số", f"Trọng số {first['label']} -> {selected_node['label']}:", minvalue=1, parent=app.root)
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
            new_w = simpledialog.askinteger("Sửa trọng số", f"Trọng số mới ({n1} - {n2}):", initialvalue=edge.get("weight", 1), minvalue=1, parent=app.root)
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
                for node in app.dijkstra_nodes:
                    app.canvas.itemconfig(node["circle"], outline="black", width=2)
                app.dijkstra_nodes = []
            
            app.dijkstra_nodes.append(selected_node)
            app.canvas.itemconfig(selected_node["circle"], outline="green", width=4)
            if len(app.dijkstra_nodes) == 2:
                messagebox.showinfo("Thông báo", "Đã chọn xong điểm đầu và cuối.\nNhấn '> Tìm đường'")
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
    if getattr(app, "algorithm_mode", "") == "dijkstra":
        # Dùng chữ cái A, B, C... cho Dijkstra
        new_label = _get_next_label(app)
    else:
        # Dùng số 1, 2, 3... cho Welsh-Powell
        max_label = max((int(node["label"]) for node in app.nodes if str(node["label"]).isdigit()), default=0)
        new_label = str(max_label + 1)
        
    app.create_node(x, y, new_label, "white")