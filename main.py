import tkinter as tk
from tkinter import messagebox
import string
from ui import setup_interface
from welsh_powell import welsh_powell_coloring

class WelshPowellApp:
    def __init__(self, root):
        self.root = root
        self.nodes = []
        self.selected_node = None
        self.drag_start = None

        self.edges = []
        self.first_node_for_connection = None

        self.dragging_from_toolbar = False
        self.toolbar_dragged = False

        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B88B", "#81ECEC"
        ]

        setup_interface(self)

    def _clear_connection_highlight(self):
        """Xóa highlight khỏi nút được chọn để kết nối."""
        if self.first_node_for_connection is not None:
            self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
            self.first_node_for_connection = None

    def toggle_mode(self, mode):
        """Bật/tắt chế độ thao tác bằng checkbox; mặc định là 'move'."""
        current_mode = self.mode_var.get()
        mode_is_checked = self.tool_vars[mode].get()

        if mode_is_checked:
            self.mode_var.set(mode)
            for other_mode, var in self.tool_vars.items():
                if other_mode != mode:
                    var.set(False)
        elif current_mode == mode:
            self.mode_var.set("move")

        if self.mode_var.get() != "connect":
            self._clear_connection_highlight()

        self.update_tool_button_styles()

    def update_tool_button_styles(self):
        """Đồng bộ trạng thái tick với mode hiện tại."""
        active_mode = self.mode_var.get()
        for mode, check in self.tool_checks.items():
            is_active = active_mode == mode
            self.tool_vars[mode].set(is_active)
            check.config(bg="#1f618d" if is_active else "#2c3e50",
                        selectcolor="#1f618d" if is_active else "#34495e")

    def _reindex_nodes(self):
        """Giữ id nút khớp với vị trí trong danh sách để tránh lệch tham chiếu cạnh."""
        old_to_new_id = {node["id"]: i for i, node in enumerate(self.nodes)}

        for i, node in enumerate(self.nodes):
            node["id"] = i

        self.edges = [
            {**e, "node1_id": old_to_new_id[e["node1_id"]], "node2_id": old_to_new_id[e["node2_id"]]}
            for e in self.edges if e["node1_id"] in old_to_new_id and e["node2_id"] in old_to_new_id
        ]

    def create_node(self, x, y, label, color):
        """Tạo một nút hình tròn"""
        radius = 35
        node_data = {
            "id": len(self.nodes),
            "x": x, "y": y, "radius": radius,
            "label": label, "color": color,
            "circle": None, "text": None, "degree": 0
        }
        
        node_data["circle"] = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="black", width=2
        )
        node_data["text"] = self.canvas.create_text(
            x, y, text=label, fill="black", font=("Arial", 12, "bold")
        )
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        """Tìm nút tại vị trí (x, y)"""
        return next((node for node in reversed(self.nodes) 
                    if (x - node["x"]) ** 2 + (y - node["y"]) ** 2 <= node["radius"] ** 2), None)

    def redraw_edges(self):
        """Vẽ lại tất cả các cạnh hiện có"""
        for edge in self.edges:
            if edge.get("line"):
                self.canvas.delete(edge["line"])
                edge["line"] = None
        
        for edge in self.edges:
            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            edge["line"] = self.canvas.create_line(
                n1["x"], n1["y"], n2["x"], n2["y"],
                fill="gray", width=2, tags="edge"
            )

    def get_edge_at(self, x, y, tolerance=5):
        """Tìm cạnh gần điểm click"""
        overlap = self.canvas.find_overlapping(x - tolerance, y - tolerance, x + tolerance, y + tolerance)
        for item in overlap:
            edge = next((e for e in self.edges if e.get("line") == item), None)
            if edge:
                return edge

        tol_sq = tolerance ** 2
        for edge in self.edges:
            if not edge.get("line"):
                continue

            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            x1, y1, x2, y2 = n1["x"], n1["y"], n2["x"], n2["y"]

            if not (min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance and
                    min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance):
                continue

            dx, dy = x2 - x1, y2 - y1
            dd = dx * dx + dy * dy
            if dd == 0:
                continue

            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / dd))
            closest_x, closest_y = x1 + t * dx, y1 + t * dy
            dist_sq = (x - closest_x) ** 2 + (y - closest_y) ** 2
            
            if dist_sq <= tol_sq:
                return edge
        return None

    def on_canvas_drag(self, event):
        """Xử lý khi kéo chuột trên canvas"""
        if self.mode_var.get() == "move" and self.selected_node and self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]

            self.selected_node["x"] += dx
            self.selected_node["y"] += dy

            radius = self.selected_node["radius"]
            self.canvas.coords(self.selected_node["circle"],
                              self.selected_node["x"] - radius,
                              self.selected_node["y"] - radius,
                              self.selected_node["x"] + radius,
                              self.selected_node["y"] + radius)
            self.canvas.coords(self.selected_node["text"],
                              self.selected_node["x"],
                              self.selected_node["y"])
            self.drag_start = (event.x, event.y)
            self.redraw_edges()

    def on_canvas_click(self, event):
        """Xử lý khi click trên canvas"""
        self.selected_node = self.get_node_at(event.x, event.y)
        mode = self.mode_var.get()

        if mode == "delete" and self.selected_node:
            self.delete_node(self.selected_node)
        elif mode == "connect" and self.selected_node:
            if self.first_node_for_connection is None:
                self.first_node_for_connection = self.selected_node
                self.canvas.itemconfig(self.selected_node["circle"], width=4, outline="red")
            elif self.selected_node == self.first_node_for_connection:
                self._clear_connection_highlight()
            else:
                self.connect_nodes(self.first_node_for_connection, self.selected_node)
                self._clear_connection_highlight()
        elif mode == "delete_edge":
            edge = self.get_edge_at(event.x, event.y)
            if edge:
                self.delete_edge(edge)
            else:
                messagebox.showwarning("Thông báo", "Không có cạnh nào tại vị trí này!")
        elif self.selected_node:
            self.canvas.itemconfig(self.selected_node["circle"], width=3)
            self.drag_start = (event.x, event.y)

    def delete_node(self, node):
        """Xóa một nút"""
        self.canvas.delete(node["circle"])
        self.canvas.delete(node["text"])
        
        # Xóa tất cả các cạnh liên quan và cập nhật bậc
        edges_to_remove = [e for e in self.edges if e["node1_id"] == node["id"] or e["node2_id"] == node["id"]]
        for edge in edges_to_remove:
            if edge.get("line"):
                self.canvas.delete(edge["line"])
            other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
            if 0 <= other_node_id < len(self.nodes):
                self.nodes[other_node_id]["degree"] -= 1
        
        self.edges = [e for e in self.edges if e not in edges_to_remove]
        self.nodes.remove(node)

        if self.selected_node == node:
            self.selected_node = None
        if self.first_node_for_connection == node:
            self._clear_connection_highlight()

        self._reindex_nodes()
        self.redraw_edges()
        
    
    def _edge_exists(self, node1_id, node2_id):
        """Kiểm tra cạnh đã tồn tại giữa hai nút."""
        return any((e["node1_id"] == node1_id and e["node2_id"] == node2_id) or 
                   (e["node1_id"] == node2_id and e["node2_id"] == node1_id) 
                   for e in self.edges)

    def connect_nodes(self, node1, node2):
        """Liên kết hai nút"""
        if node1["id"] == node2["id"]:
            messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
        elif self._edge_exists(node1["id"], node2["id"]):
            messagebox.showwarning("Lỗi", "Cạnh này đã tồn tại!")
        else:
            self.edges.append({"node1_id": node1["id"], "node2_id": node2["id"], "line": None})
            node1["degree"] += 1
            node2["degree"] += 1
            self.redraw_edges()
    
    def delete_edge(self, edge):
        """Xóa một cạnh"""
        node1 = self.nodes[edge["node1_id"]]
        node2 = self.nodes[edge["node2_id"]]
        node1["degree"] -= 1
        node2["degree"] -= 1
        
        if edge.get("line"):
            self.canvas.delete(edge["line"])
        self.edges.remove(edge)
        self.redraw_edges()

    def on_toolbar_button_release(self, event):
        """Xử lý khi thả nút từ toolbar"""
        self.dragging_from_toolbar = False
        self.root.config(cursor="arrow")

        canvas_x = self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_rooty()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        inside_canvas = (canvas_x <= event.x_root <= canvas_x + canvas_width and
                        canvas_y <= event.y_root <= canvas_y + canvas_height)

        if inside_canvas:
            x, y = event.x_root - canvas_x, event.y_root - canvas_y
        elif self.toolbar_dragged:
            return
        else:
            x, y = canvas_width // 2, canvas_height // 2

        max_label = max([int(node["label"]) for node in self.nodes], default=0)
        self.create_node(x, y, str(max_label + 1), "white")

    def welsh_powell_coloring(self):
        """Gọi hàm Welsh-Powell đã tách riêng và cập nhật giao diện."""
        node_colors = welsh_powell_coloring(self.nodes, self.edges)
        if not node_colors:
            messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
            return

        max_color = max(node_colors)
        color_groups = [[] for _ in range(max_color + 1)]
        
        # Cập nhật màu nút và gom nhóm theo màu
        for i, color_idx in enumerate(node_colors):
            self.nodes[i]["color"] = self.colors[color_idx % len(self.colors)]
            self.canvas.itemconfig(self.nodes[i]["circle"], fill=self.nodes[i]["color"])
            color_groups[color_idx].append(self.nodes[i]["label"])

        # Tạo kết quả hiển thị
        result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
        for color_idx, nodes_in_color in enumerate(color_groups):
            result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"

        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
