"""gui/prim_ui.py - Giao diện trực quan cho thuật toán Prim"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.graph_actions import run_prim_algorithm


def setup_prim_ui(app, add_tool_check, create_toolbar_button):

    # ===== TOOL =====
    add_tool_check(app, "Xóa nút", "delete")
    add_tool_check(app, "Nối nút (Trọng Số)", "connect")
    add_tool_check(app, "Sửa Trọng Số", "edit_weight")
    add_tool_check(app, "Xóa cạnh", "delete_edge")
    add_tool_check(app, "Chọn cây khung", "prim_select")

    # ===== BUTTON RUN =====
    app.run_btn = create_toolbar_button(
        app,
        "▶ Chạy Prim",
        "#f39c12",
        lambda: run_prim_animation(app)
    )

    # ===== CLEAR UI =====
    for widget in app.info_frame.winfo_children():
        widget.destroy()

    tk.Label(app.info_frame, text="Bảng chạy Prim", font=("Arial", 10, "bold"), bg="#ecf0f1").pack(pady=(10,5))

    # ===== TABLE =====
    app.tree = ttk.Treeview(app.info_frame, show='headings', height=20)
    app.tree.pack(fill="both", expand=True, padx=5, pady=5)

    app.result_frame = tk.Frame(app.info_frame, bg="#ecf0f1")
    app.result_frame.pack(fill="x", expand=False, padx=5, pady=5)


def run_prim_animation(app):
    if not hasattr(app, "prim_start") or app.prim_start is None:
        messagebox.showwarning("Lỗi", "Hãy chọn đỉnh bắt đầu!")
        return

    mst_edges = run_prim_algorithm(app, app.prim_start)

    if not mst_edges:
        messagebox.showerror("Lỗi", "Không tìm được cây khung (graph có thể không liên thông)")
        return

    # ===== RESET =====
    app.highlighted_edges = []
    app.highlighted_path = []
    app.render_graph()
    app.run_btn.config(state="disabled")

    # clear bảng
    for item in app.tree.get_children():
        app.tree.delete(item)

    # clear result
    for widget in app.result_frame.winfo_children():
        widget.destroy()

    delay_ms = getattr(app, "animation_delay_ms", 350)

    # ===== TABLE =====
    columns = ["Cạnh chọn", "Trọng số", "Tổng"]
    app.tree["columns"] = columns

    for col in columns:
        app.tree.heading(col, text=col)
        app.tree.column(col, width=90, anchor='center')

    total_weight = 0

    # ===== ANIMATION =====
    def animate(i=0):
        nonlocal total_weight

        if i < len(mst_edges):
            edge = mst_edges[i]

            n1 = app.nodes[edge["node1_id"]]["label"]
            n2 = app.nodes[edge["node2_id"]]["label"]
            w = edge.get("weight", 1)

            total_weight += w

            # highlight cạnh
            app.highlighted_edges.append(edge)
            app.render_graph()

            # bảng
            app.tree.insert('', tk.END, values=(f"{n1} - {n2}", w, total_weight))
            app.tree.yview_moveto(1)

            app.root.after(delay_ms, lambda: animate(i + 1))

        else:
            app.run_btn.config(state="normal")

            tk.Label(
                app.result_frame,
                text=f"Tổng trọng số MST: {total_weight}",
                fg="#27ae60",
                bg="#ecf0f1",
                font=("Arial", 10, "bold")
            ).pack(anchor="w")

    animate()