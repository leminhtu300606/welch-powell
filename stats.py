import tkinter as tk
from tkinter import messagebox

class ColoringStats:
    def on_apply_algorithm(self, event=None):
        if not self.nodes:
            messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
            return
        self.welsh_powell_coloring()

    def welsh_powell_coloring(self):
        if not self.nodes:
            return

        adjacency = self._build_adjacency()
        order = sorted(range(len(self.nodes)), key=lambda i: self.nodes[i]["degree"], reverse=True)
        node_colors = [-1] * len(self.nodes)

        for node_index in order:
            forbidden = {node_colors[neighbor] for neighbor in adjacency[node_index] if node_colors[neighbor] != -1}
            color = 0
            while color in forbidden:
                color += 1
            node_colors[node_index] = color

        self._apply_colors(node_colors)
        self._show_result(node_colors)

    def _build_adjacency(self):
        adjacency = [set() for _ in self.nodes]
        for edge in self.edges:
            adjacency[edge["node1_id"]].add(edge["node2_id"])
            adjacency[edge["node2_id"]].add(edge["node1_id"])
        return adjacency

    def _apply_colors(self, node_colors):
        for i, color_idx in enumerate(node_colors):
            self.nodes[i]["color"] = self.colors[color_idx % len(self.colors)]
            self.canvas.itemconfig(self.nodes[i]["circle"], fill=self.nodes[i]["color"])

    def _show_result(self, node_colors):
        max_color = max(node_colors)
        result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
        for color_idx in range(max_color + 1):
            nodes_in_color = [self.nodes[i]["label"] for i, c in enumerate(node_colors) if c == color_idx]
            result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"

        result += "\nHướng dẫn chọn:"
        result += "\n- Chọn chế độ 'Di chuyển' để kéo nút trên canvas."
        result += "\n- Chọn chế độ 'Xóa nút' để click nút cần xóa."
        result += "\n- Chọn chế độ 'Nối nút' để click 2 nút để tạo cạnh."
        result += "\n- Chọn chế độ 'Xóa cạnh' để click cạnh muốn xóa."

        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("430x360")
        tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()