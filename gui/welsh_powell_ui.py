"""gui/welsh_powell_ui.py - Giao diện dành riêng cho thuật toán Welsh-Powell"""
import tkinter as tk
from tkinter import messagebox
from core.graph_actions import apply_welsh_powell_coloring

def setup_welsh_powell_ui(app, add_tool_check, create_toolbar_button):
    add_tool_check(app, "Nối nút", "connect")
    add_tool_check(app, "Xóa", "delete")
    app.run_btn = create_toolbar_button(app, "> Tô màu", "#27ae60", lambda: run_coloring(app))
    
    # 1. Dọn dẹp các khung cũ (nếu có do file ui.py gọi nhầm)
    for widget in app.info_frame.winfo_children():
        widget.destroy()

    # 2. Tạo bảng Quan hệ các nút (Giữ nguyên gốc)
    tk.Label(app.info_frame, text="Quan hệ giữa các nút", font=("Arial", 11, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=(10, 6))
    app.relation_listbox = tk.Listbox(app.info_frame, font=("Arial", 10), height=12)
    app.relation_listbox.pack(fill="x", padx=10, pady=(0, 8))
    
    # 3. Gắn hàm cập nhật vào biến toàn cục của app
    app.refresh_relationship_panel = lambda: _refresh_relationship_panel(app)
    app.refresh_relationship_panel()

def _refresh_relationship_panel(app):
    """Lấy danh sách cạnh và in ra bảng"""
    if not hasattr(app, "relation_listbox"): return
    app.relation_listbox.delete(0, tk.END)
    for edge in app.edges:
        n1_id, n2_id = edge["node1_id"], edge["node2_id"]
        if n1_id >= len(app.nodes) or n2_id >= len(app.nodes): continue
        n1_label = app.nodes[n1_id]['label']
        n2_label = app.nodes[n2_id]['label']
        app.relation_listbox.insert(tk.END, f"{n1_label} - {n2_label}")

def run_coloring(app):
    if hasattr(app, "refresh_relationship_panel"):
        app.refresh_relationship_panel()

    result = apply_welsh_powell_coloring(app)
    if result is None:
        messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
        return

    max_color, color_groups, coloring_plan = result
    delay_ms = getattr(app, "animation_delay_ms", 350)
    app.run_btn.config(state="disabled")

    def show_result_window():
        text = "\n".join([
            "Kết quả Welch-Powell:", "",
            f"Số màu cần thiết: {max_color + 1}", "",
            "Phân bổ màu:",
            *(f"Màu {idx}: {', '.join(nodes)}" for idx, nodes in enumerate(color_groups)),
        ])
        result_window = tk.Toplevel(app.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        tk.Label(result_window, text=text, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

    def animate_step(index=0, previous_node=None):
        if previous_node is not None:
            app.canvas.itemconfig(previous_node["circle"], width=2, outline="black")

        if index >= len(coloring_plan):
            app.run_btn.config(state="normal")
            show_result_window()
            return

        current_node, color_value = coloring_plan[index]
        current_node["color"] = color_value
        app.canvas.itemconfig(current_node["circle"], fill=color_value, width=4, outline="#e67e22")
        app.root.after(delay_ms, lambda: animate_step(index + 1, current_node))

    animate_step()