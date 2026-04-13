"""gui/dijkstra_ui.py - Giao diện dành riêng cho thuật toán Dijkstra"""
import tkinter as tk
from tkinter import ttk, messagebox
from algorithms.dijkstra import dijkstra_table_and_paths
from gui.animation_utils import schedule_animation_step

def setup_dijkstra_ui(app, add_tool_check, create_toolbar_button):
    add_tool_check(app, "Nối nút (Trọng Số)", "connect")
    add_tool_check(app, "Sửa Trọng Số", "edit_weight")
    add_tool_check(app, "Sửa Tên Đỉnh", "edit_label") 
    add_tool_check(app, "Xóa", "delete")
    add_tool_check(app, "Chọn điểm", "dijkstra_select")
    
    app.run_btn = create_toolbar_button(app, "> Tìm đường", "#e67e22", lambda: run_dijkstra_animation(app))
    
    for widget in app.info_frame.winfo_children(): widget.destroy()

    if not hasattr(app, "is_directed"):
        app.is_directed = tk.BooleanVar(value=False)
    
    tk.Checkbutton(
        app.info_frame, text="Đồ thị Có Hướng (Directed)", 
        variable=app.is_directed, bg="#ecf0f1", font=("Arial", 10, "bold"), 
        fg="#2980b9", cursor="hand2", command=app.render_graph
    ).pack(pady=(5, 0))

    tk.Label(app.info_frame, text="Bảng chạy Dijkstra", font=("Arial", 10, "bold"), bg="#ecf0f1").pack(pady=(10,5))
    
    app.tree = ttk.Treeview(app.info_frame, show='headings', height=20)
    app.tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Nút Bật/Tắt nhãn nổi
    if not hasattr(app, "show_floating_labels"):
        app.show_floating_labels = tk.BooleanVar(value=True)

    tk.Checkbutton(
        app.info_frame, text="Hiển thị nhãn giá trị trên đồ thị", 
        variable=app.show_floating_labels, bg="#ecf0f1", font=("Arial",9, "bold"), 
        fg="#d35400", cursor="hand2", command=app.render_graph
    ).pack(anchor="w", padx=5, pady=(0, 2))

    # Nút Bật/Tắt hiển thị giá trị cũ cho đỉnh mang nhãn "-"
    if not hasattr(app, "show_done_labels"):
        app.show_done_labels = tk.BooleanVar(value=True)

    tk.Checkbutton(
        app.info_frame, text="Giữ lại giá trị cho đỉnh đã chốt (-)", 
        variable=app.show_done_labels, bg="#ecf0f1", font=("Arial", 10, "italic bold"), 
        fg="#5825e3", cursor="hand2", command=app.render_graph
    ).pack(anchor="w", padx=5, pady=(0, 5))

    app.result_frame = tk.Frame(app.info_frame, bg="#ecf0f1")
    app.result_frame.pack(fill="x", expand=False, padx=5, pady=5)


def run_dijkstra_animation(app):
    if not hasattr(app, "dijkstra_nodes") or len(app.dijkstra_nodes) != 2 or app.dijkstra_nodes[0] is None or app.dijkstra_nodes[1] is None:
        messagebox.showinfo("Hướng dẫn", "Vui lòng chọn đầy đủ 2 đỉnh (Bắt Đầu & Kết Thúc) bằng công cụ 'Chọn điểm' trước khi tìm đường.")
        return

    for item in app.tree.get_children(): app.tree.delete(item)
    for widget in app.result_frame.winfo_children(): widget.destroy()

    app.highlighted_path = []
    app.render_graph()
    app.run_btn.config(state="disabled")

    start_id, end_id = app.dijkstra_nodes[0]["id"], app.dijkstra_nodes[1]["id"]
    
    is_directed_graph = app.is_directed.get()
    history_table, all_paths, min_dist = dijkstra_table_and_paths(app.nodes, app.edges, start_id, end_id, is_directed_graph)

    # TRUYỀN LỊCH SỬ VÀO APP ĐỂ CANVAS CÓ THỂ LỤC LẠI GIÁ TRỊ CŨ CỦA NHÃN "-"
    app.dijkstra_history_table = history_table

    other_nodes = [n for n in app.nodes if n["id"] not in (start_id, end_id)]
    other_nodes.sort(key=lambda n: str(n["label"]))
    column_order_ids = [start_id] + [n["id"] for n in other_nodes] + [end_id]
    node_labels = [str(app.nodes[i]["label"]) for i in column_order_ids]
    
    app.tree["columns"] = node_labels
    for label in node_labels:
        app.tree.heading(label, text=label)
        app.tree.column(label, width=55, anchor='center')

    delay_ms = getattr(app, "animation_delay_ms", 5000)
    
    def format_row(row_data, path_pred):
        values = []
        for i in column_order_ids:
            state = row_data["states"][i]
            if state["status"] == "done":
                values.append("-")
            else:
                dist, preds = state["dist"], state["preds"]
                if dist == float('inf'):
                    values.append("(∞, -)")
                else:
                    p = None
                    if i in path_pred and path_pred[i] in preds:
                        p = path_pred[i]
                    elif preds:
                        p = preds[0]
                    p_label = app.nodes[p]["label"] if p is not None else "-"
                    text = "0" if (dist == 0 and not preds) else f"({dist}, {p_label})"
                    if state["status"] == "finalizing": text += "*"
                    values.append(text)
        return values

    current_path_pred = {}
    if all_paths:
        current_path_pred = {v: u for u, v in zip(all_paths[0][:-1], all_paths[0][1:])}

    # --- XÂY DỰNG TỪ ĐIỂN VẾT (TRACE-BACK) ---
    full_preds = {}
    for row in history_table:
        u = row["finalized_node"]
        state = row["states"].get(u)
        if state and state.get("preds"):
            full_preds[u] = state["preds"][0]

    def get_path_to_node(target_id):
        path = []
        curr = target_id
        visited = set()
        
        # Lấy từ điển vết của "Cách" đang được chọn hiện tại
        active_path_pred = getattr(app, "current_path_pred", {})

        while curr is not None and curr not in visited:
            path.append(curr)
            visited.add(curr)
            
            # Ưu tiên đi ngược theo Cách đang chọn. 
            # Nếu đỉnh không thuộc nhánh của Cách đó, lấy vết mặc định.
            if curr in active_path_pred:
                curr = active_path_pred[curr]
            else:
                curr = full_preds.get(curr)
                
        path.reverse()
        return path
    
    # ================= TƯƠNG TÁC: CLICK VÀO BẢNG ĐỂ CẬP NHẬT ĐƯỜNG ĐI ĐỎ =================
    def on_tree_click(event):
        if app.run_btn["state"] == "disabled": return
        selected_items = app.tree.selection()
        if not selected_items: return
            
        idx = app.tree.index(selected_items[0])
        if idx < len(history_table):
            row_data = history_table[idx]
            app.current_dijkstra_row = row_data

            finalized_node = row_data["finalized_node"]
            app.highlighted_path = get_path_to_node(finalized_node)
            app.highlighted_color = "red"
            
            app.render_graph()

    app.tree.bind("<ButtonRelease-1>", on_tree_click)

    def animate_table(idx=0):
        if idx < len(history_table):
            row_data = history_table[idx]
            
            app.current_dijkstra_row = row_data
            app.current_path_pred = current_path_pred
            
            finalized_node = row_data["finalized_node"]
            app.highlighted_path = get_path_to_node(finalized_node)
            app.highlighted_color = "red"
            
            app.render_graph()
            
            app.tree.insert('', tk.END, values=format_row(row_data, current_path_pred))
            app.tree.yview_moveto(1)
            schedule_animation_step(app, lambda: animate_table(idx + 1))
        else:
            app.current_dijkstra_row = None
            app.render_graph()

            app.run_btn.config(state="normal")
            app.dijkstra_nodes = []
            
            if not all_paths:
                tk.Label(app.result_frame, text="Không có đường đi!", fg="red", bg="#ecf0f1", font=("Arial", 10, "bold")).pack()
            else:
                tk.Label(app.result_frame, text=f"Tổng chi phí: {min_dist}", fg="#27ae60", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(anchor="w")
                app.selected_path_var = tk.IntVar(value=0)
                colors = ["red", "blue", "green", "purple", "orange"]
                
                def show_selected_path(path_index, animate=False):
                    path = all_paths[path_index]
                    color = colors[path_index % len(colors)]
                    path_pred = {v: u for u, v in zip(path[:-1], path[1:])}
                    
                    # BỔ SUNG DÒNG NÀY: Cập nhật vết đang chọn vào app
                    app.current_path_pred = path_pred 
                    
                    for item in app.tree.get_children(): app.tree.delete(item)
                    for row_data in history_table:
                        app.tree.insert('', tk.END, values=format_row(row_data, path_pred))
                    
                    app.current_dijkstra_row = None
                    
                    if animate:
                        app.highlighted_color = color
                        def draw_segment(step=0):
                            if step < len(path):
                                app.highlighted_path = path[:step+1]
                                app.render_graph()
                                schedule_animation_step(app, lambda: draw_segment(step + 1))
                        draw_segment(0)
                    else:
                        app.highlighted_path = path
                        app.highlighted_color = color
                        app.render_graph()

                for path_idx, path in enumerate(all_paths):
                    tk.Radiobutton(
                        app.result_frame, text=f"Cách {path_idx + 1}: {' -> '.join([app.nodes[i]['label'] for i in path])}", 
                        variable=app.selected_path_var, value=path_idx, bg="#ecf0f1", fg="#2c3e50", font=("Arial", 9, "bold"), cursor="hand2",
                        command=lambda: show_selected_path(app.selected_path_var.get(), animate=False)
                    ).pack(anchor="w", pady=2)
                
                show_selected_path(0, animate=True)
                
    animate_table()