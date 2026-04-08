"""core/events.py - Xử lý sự kiện"""
from tkinter import messagebox, simpledialog
from core.graph_actions import (
    connect_nodes, delete_edge, delete_node, set_edge_weight
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
        edge = app.get_edge_at(event.x, event.y)
        if selected_node: delete_node(app, selected_node)
        elif edge: delete_edge(app, edge)
        else: messagebox.showwarning("Thông báo", "Không có cạnh tại đây!")
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
            edge_exists = False
            for edge in app.edges:
                if (edge["node1_id"] == first["id"] and edge["node2_id"] == selected_node["id"]) or \
                   (edge["node1_id"] == selected_node["id"] and edge["node2_id"] == first["id"]):
                    edge_exists = True
                    break
            
            if edge_exists:
                messagebox.showwarning("Lỗi", "Cạnh nối giữa 2 đỉnh này đã tồn tại!")
                app._clear_connection_highlight()
                return

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
        # edge = app.get_edge_at(event.x, event.y)
        # if edge: delete_edge(app, edge)
        # else: messagebox.showwarning("Thông báo", "Không có cạnh tại đây!")
        return

    if mode == "edit_weight":
        edge = app.get_edge_at(event.x, event.y)
        if not edge:
            messagebox.showwarning("Thông báo", "Hãy click trực tiếp lên một cạnh để sửa trọng số!")
            return

        current_weight = edge.get("weight", 1)
        new_weight = _ask_positive_weight_vi(
            app.root,
            "Sửa trọng số",
            f"Nhập trọng số mới cho cạnh {app.nodes[edge['node1_id']]['label']} - {app.nodes[edge['node2_id']]['label']}:",
            initialvalue=current_weight,
        )
        if new_weight is None:
            return

        set_edge_weight(app, edge, new_weight)
        return

    if mode == "edit_label":
        if selected_node:
            new_label = simpledialog.askstring(
                "Sửa tên đỉnh", 
                f"Nhập tên/chữ cái mới cho đỉnh '{selected_node['label']}':", 
                initialvalue=selected_node['label'], 
                parent=app.root
            )
            
            if new_label is not None:  # Người dùng không bấm Cancel
                new_label = new_label.strip()
                if new_label == "":
                    messagebox.showwarning("Lỗi nhập liệu", "Tên đỉnh không được để trống!")
                    return
                    
                if new_label == str(selected_node["label"]):
                    return  # Giữ nguyên tên cũ thì không làm gì cả
                
                # BẪY LỖI: Kiểm tra xem tên mới đã bị đỉnh nào khác lấy chưa
                existing_labels = {str(n["label"]).upper() for n in app.nodes if n["id"] != selected_node["id"]}
                if new_label.upper() in existing_labels:
                    messagebox.showwarning("Lỗi trùng lặp", f"Đỉnh mang tên '{new_label}' đã tồn tại trên đồ thị!\nVui lòng chọn tên khác.")
                else:
                    selected_node["label"] = new_label
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
            if not hasattr(app, "dijkstra_nodes") or len(app.dijkstra_nodes) != 2:
                app.dijkstra_nodes = [None, None]

            selected_id = selected_node["id"]

            # Click lại vào điểm đã chọn để hủy chọn điểm đó.
            for idx, chosen_node in enumerate(app.dijkstra_nodes):
                if chosen_node is not None and chosen_node["id"] == selected_id:
                    app.dijkstra_nodes[idx] = None
                    if hasattr(app, "dijkstra_notice_var"):
                        app.dijkstra_notice_var.set("Đã hủy chọn. Hãy chọn lại điểm BĐ và KT rồi nhấn '> Chạy'.")
                    if hasattr(app, "dijkstra_notice_label"):
                        app.dijkstra_notice_label.config(fg="#c0392b")
                    app.render_graph()
                    return

            if app.dijkstra_nodes[0] is None:
                app.dijkstra_nodes[0] = selected_node
            elif app.dijkstra_nodes[1] is None:
                app.dijkstra_nodes[1] = selected_node
            else:
                # Nếu đã đủ 2 điểm, chọn điểm mới sẽ bắt đầu lại từ điểm đầu.
                app.dijkstra_nodes = [selected_node, None]

            app.render_graph()
            if app.dijkstra_nodes[0] is not None and app.dijkstra_nodes[1] is not None:
                if hasattr(app, "dijkstra_notice_var"):
                    app.dijkstra_notice_var.set("Đã chọn đủ BĐ và KT. Nhấn '> Chạy' để bắt đầu xử lý.")
                if hasattr(app, "dijkstra_notice_label"):
                    app.dijkstra_notice_label.config(fg="#27ae60")
                messagebox.showinfo("Thông báo", "Đã chọn xong điểm đầu và cuối.\nNhấn '> Tìm đường'")
            elif app.dijkstra_nodes[0] is not None:
                if hasattr(app, "dijkstra_notice_var"):
                    app.dijkstra_notice_var.set("Đã chọn BĐ. Hãy chọn thêm điểm KT.")
                if hasattr(app, "dijkstra_notice_label"):
                    app.dijkstra_notice_label.config(fg="#2c3e50")
            else:
                if hasattr(app, "dijkstra_notice_var"):
                    app.dijkstra_notice_var.set("Hãy chọn điểm BĐ.")
                if hasattr(app, "dijkstra_notice_label"):
                    app.dijkstra_notice_label.config(fg="#2c3e50")
        return
    # ================= PRIM SELECT VERTEX =================
    if mode == "prim_select":
        node = app.get_node_at(event.x, event.y)
        if not node:
            messagebox.showwarning("Thông báo", "Hãy click trực tiếp lên một đỉnh để chọn đỉnh bắt đầu.")
            return

        app.prim_start_vertex = node["id"]
        app.highlighted_path = []
        app.highlighted_color = "#2980b9"
        app.highlighted_edges = []
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