"""gui/kruskal_ui.py - Giao diện trực quan cho thuật toán Kruskal"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.graph_actions import run_kruskal_algorithm


def setup_kruskal_ui(app, add_tool_check, create_toolbar_button):

    # ===== TOOL =====
    add_tool_check(app, "Xóa nút", "delete")
    add_tool_check(app, "Nối nút (Trọng Số)", "connect")
    add_tool_check(app, "Sửa Trọng Số", "edit_weight")
    add_tool_check(app, "Xóa cạnh", "delete_edge")

    # ===== BUTTON RUN =====
    app.run_btn = create_toolbar_button(
        app,
        "▶ Chạy Kruskal",
        "#9b59b6",
        lambda: run_kruskal_animation(app)
    )

    # ===== CLEAR UI =====
    for widget in app.info_frame.winfo_children():
        widget.destroy()

    tk.Label(
        app.info_frame,
        text="Bảng chạy Kruskal",
        font=("Arial", 10, "bold"),
        bg="#ecf0f1"
    ).pack(pady=(10, 5))

    # ===== TABLE =====
    app.tree = ttk.Treeview(app.info_frame, show='headings', height=20)
    app.tree.pack(fill="both", expand=True, padx=5, pady=5)

    app.result_frame = tk.Frame(app.info_frame, bg="#ecf0f1")
    app.result_frame.pack(fill="x", expand=False, padx=5, pady=5)


def run_kruskal_animation(app):

    # ===== CHẠY THUẬT TOÁN =====
    result = run_kruskal_algorithm(app)

    if not result:
        messagebox.showwarning("Lỗi", "Không thể chạy Kruskal!")
        return

    mst_edges, sorted_edges = result

    # reset highlight
    app.highlighted_edges = []
    app.render_graph()
    app.run_btn.config(state="disabled")

    delay_ms = getattr(app, "animation_delay_ms", 350)

    # ===== TABLE SETUP =====
    columns = ["Cạnh", "Trọng số", "Trạng thái", "Tổng"]
    app.tree["columns"] = columns

    for col in columns:
        app.tree.heading(col, text=col)
        app.tree.column(col, width=90, anchor='center')

    total_weight = 0

    # ===== TẠO SET MST (SO SÁNH NHANH & CHUẨN) =====
    mst_set = {
        (min(e["node1_id"], e["node2_id"]),
         max(e["node1_id"], e["node2_id"]))
        for e in mst_edges
    }

    # ===== ANIMATION =====
    def animate(i=0):
        nonlocal total_weight

        if i < len(sorted_edges):
            edge = sorted_edges[i]

            n1 = app.nodes[edge["node1_id"]]["label"]
            n2 = app.nodes[edge["node2_id"]]["label"]
            w = edge.get("weight", 1)

            edge_pair = (
                min(edge["node1_id"], edge["node2_id"]),
                max(edge["node1_id"], edge["node2_id"])
            )

            # ===== CHECK MST =====
            if edge_pair in mst_set:
                status = "✔ Chọn"
                total_weight += w
                app.highlighted_edges.append(edge)
            else:
                status = "✖ Bỏ"

            # vẽ lại graph
            app.render_graph()

            # thêm dòng vào bảng
            app.tree.insert(
                '',
                tk.END,
                values=(f"{n1} - {n2}", w, status, total_weight)
            )
            app.tree.yview_moveto(1)

            app.root.after(delay_ms, lambda: animate(i + 1))

        else:
            app.run_btn.config(state="normal")

            # ===== RESULT =====
            for widget in app.result_frame.winfo_children():
                widget.destroy()

            tk.Label(
                app.result_frame,
                text=f"Tổng trọng số MST: {total_weight}",
                fg="#27ae60",
                bg="#ecf0f1",
                font=("Arial", 10, "bold")
            ).pack(anchor="w")

    animate()