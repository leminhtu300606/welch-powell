"""gui/dijkstra_ui.py - Giao diện dành riêng cho thuật toán Dijkstra"""
import tkinter as tk
from tkinter import ttk, messagebox
from algorithms.dijkstra import dijkstra_table_and_paths
from core.graph_actions import run_prim_algorithm, run_kruskal_algorithm


def _set_dijkstra_notice(app, text, color="#2c3e50"):
    if hasattr(app, "dijkstra_notice_var"):
        app.dijkstra_notice_var.set(text)
    if hasattr(app, "dijkstra_notice_label"):
        app.dijkstra_notice_label.config(fg=color)


def _sync_dijkstra_select_mode(app):
    if not hasattr(app, "mode_var"):
        return
    app.mode_var.set("dijkstra_select")
    if hasattr(app, "tool_vars"):
        for mode_name, var in app.tool_vars.items():
            var.set(mode_name == "dijkstra_select")
    if hasattr(app, "tool_checks"):
        for mode_name, check in app.tool_checks.items():
            bg = "#1f618d" if mode_name == "dijkstra_select" else "#2c3e50"
            check.config(bg=bg, selectcolor=bg if mode_name == "dijkstra_select" else "#34495e")


def setup_dijkstra_ui(app, add_tool_check, create_toolbar_button):
    
    add_tool_check(app, "Xóa nút", "delete")
    add_tool_check(app, "Nối nút (Trọng Số)", "connect")
    add_tool_check(app, "Sửa Trọng Số", "edit_weight")
    add_tool_check(app, "Sửa Tên Đỉnh", "edit_label") 
    add_tool_check(app, "Xóa cạnh", "delete_edge")
    app.run_btn = create_toolbar_button(
    app,
    "> Chạy",
    "#e67e22",
    lambda: run_algorithm(app)
)
    
    for widget in app.info_frame.winfo_children(): widget.destroy()

    tk.Label(app.info_frame, text="Bảng chạy Dijkstra", font=("Arial", 10, "bold"), bg="#ecf0f1").pack(pady=(10,5))

    app.dijkstra_notice_var = tk.StringVar(value="Nhấn '> Chạy' để bắt đầu chọn điểm BĐ và KT.")
    app.dijkstra_notice_label = tk.Label(
        app.info_frame,
        textvariable=app.dijkstra_notice_var,
        font=("Arial", 9, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50",
        wraplength=250,
        justify="left",
    )
    app.dijkstra_notice_label.pack(fill="x", padx=8, pady=(0, 6))
    
    app.tree = ttk.Treeview(app.info_frame, show='headings', height=20)
    app.tree.pack(fill="both", expand=True, padx=5, pady=5)

    app.result_frame = tk.Frame(app.info_frame, bg="#ecf0f1")
    app.result_frame.pack(fill="x", expand=False, padx=5, pady=5)

def run_algorithm(app):
    from tkinter import messagebox

    # ================= DIJKSTRA =================
    if app.algorithm_mode == "dijkstra":
        run_dijkstra_animation(app)
        return

    # ================= PRIM =================
    elif app.algorithm_mode == "prim":
        if not app.edges:
            messagebox.showwarning("Lỗi", "Đồ thị chưa có cạnh để chạy Prim.")
            return

        run_prim_algorithm(app, getattr(app, "prim_start_edge", None))
        app.render_graph()

        messagebox.showinfo("Kết quả", "Đã tìm xong cây khung nhỏ nhất (Prim)")
        return

    # ================= KRUSKAL =================
    elif app.algorithm_mode == "kruskal":
        run_kruskal_algorithm(app)
        app.render_graph()

        messagebox.showinfo("Kết quả", "Đã tìm xong cây khung nhỏ nhất (Kruskal)")
        return

def run_dijkstra_animation(app):
    if (
        not hasattr(app, "dijkstra_nodes")
        or len(app.dijkstra_nodes) != 2
        or app.dijkstra_nodes[0] is None
        or app.dijkstra_nodes[1] is None
    ):
        _sync_dijkstra_select_mode(app)
        _set_dijkstra_notice(app, "Chọn điểm bắt đầu (BĐ) và điểm kết thúc (KT), sau đó nhấn '> Chạy' lần nữa.", "#c0392b")
        return

    _set_dijkstra_notice(app, "Đang chạy thuật toán Dijkstra...", "#2c3e50")

    start_id, end_id = app.dijkstra_nodes[0]["id"], app.dijkstra_nodes[1]["id"]
    history_table, all_paths, min_dist = dijkstra_table_and_paths(app.nodes, app.edges, start_id, end_id)
    
    app.highlighted_path = []
    app.render_graph()
    app.run_btn.config(state="disabled")

    # --- SẮP XẾP CỘT THEO CHIỀU LAN TỎA TỪ ĐỈNH START ---
    # Lấy thứ tự các đỉnh được thuật toán duyệt (finalized)
    column_order_ids = [row["finalized_node"] for row in history_table]
    # Gắn thêm các đỉnh bị cô lập (không thể đi tới) vào cuối bảng
    for n in app.nodes:
        if n["id"] not in column_order_ids:
            column_order_ids.append(n["id"])
            
    # Lấy nhãn (A, B, C...) dựa theo thứ tự đã sắp xếp
    node_labels = [str(app.nodes[i]["label"]) for i in column_order_ids]
    
    app.tree["columns"] = node_labels
    for label in node_labels:
        app.tree.heading(label, text=label)
        app.tree.column(label, width=55, anchor='center')

    delay_ms = getattr(app, "animation_delay_ms", 350)
    
    # Hàm điền dữ liệu vào bảng
    def format_row(row_data, path_pred):
        values = []
        for i in column_order_ids:  # CHÚ Ý: Lặp theo thứ tự cột mới đã sắp xếp
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
    
    def animate_table(idx=0):
        if idx < len(history_table):
            row_data = history_table[idx]
            final_node = app.nodes[row_data["finalized_node"]]
            app.canvas.itemconfig(final_node["circle"], outline="yellow", width=4)
            
            app.tree.insert('', tk.END, values=format_row(row_data, current_path_pred))
            app.tree.yview_moveto(1)
            app.root.after(delay_ms, lambda: animate_table(idx + 1))
        else:
            app.run_btn.config(state="normal")
            app.dijkstra_nodes = []
            _set_dijkstra_notice(app, "Nhấn '> Chạy' để chọn lại điểm BĐ/KT cho lần chạy tiếp theo.", "#2c3e50")
            for widget in app.result_frame.winfo_children(): widget.destroy()
            
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
                    for item in app.tree.get_children(): app.tree.delete(item)
                    for row_data in history_table:
                        app.tree.insert('', tk.END, values=format_row(row_data, path_pred))
                    
                    if animate:
                        app.highlighted_color = color
                        def draw_segment(step=0):
                            if step < len(path):
                                app.highlighted_path = path[:step+1]
                                app.render_graph()
                                app.root.after(delay_ms, lambda: draw_segment(step + 1))
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