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

        if self.mode_var.get() != "connect" and self.first_node_for_connection is not None:
            self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
            self.first_node_for_connection = None

        self.update_tool_button_styles()

    def update_tool_button_styles(self):
        """Đồng bộ trạng thái tick với mode hiện tại."""
        active_mode = self.mode_var.get()
        for mode, check in self.tool_checks.items():
            is_active = active_mode == mode
            self.tool_vars[mode].set(is_active)
            check.config(
                bg="#1f618d" if is_active else "#2c3e50",
                selectcolor="#1f618d" if is_active else "#34495e"
            )

    def _reindex_nodes(self):
        """Giữ id nút khớp với vị trí trong danh sách để tránh lệch tham chiếu cạnh."""
        old_to_new_id = {node["id"]: index for index, node in enumerate(self.nodes)}

        for new_id, node in enumerate(self.nodes):
            node["id"] = new_id

        valid_edges = []
        for edge in self.edges:
            old_n1 = edge["node1_id"]
            old_n2 = edge["node2_id"]
            if old_n1 in old_to_new_id and old_n2 in old_to_new_id:
                edge["node1_id"] = old_to_new_id[old_n1]
                edge["node2_id"] = old_to_new_id[old_n2]
                valid_edges.append(edge)
        self.edges = valid_edges

    def create_node(self, x, y, label, color):
        """Tạo một nút hình tròn"""
        node_id = len(self.nodes)
        radius = 35
        
        node_data = {
            "id": node_id,
            "x": x,
            "y": y,
            "radius": radius,
            "label": label,
            "color": color,
            "circle": None,
            "text": None,
            "degree": 0
        }
        
        node_data["circle"] = self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color,
            outline="black",
            width=2
        )
        
        node_data["text"] = self.canvas.create_text(
            x, y,
            text=label,
            fill="black",
            font=("Arial", 12, "bold")
        )
        
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        """Tìm nút tại vị trí (x, y)"""
        for node in reversed(self.nodes):
            if (x - node["x"]) ** 2 + (y - node["y"]) ** 2 <= node["radius"] ** 2:
                return node
        return None

    def redraw_edges(self):
        """Vẽ lại tất cả các cạnh hiện có"""
        for edge in self.edges:
            if "line" in edge and edge["line"] is not None:
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
        # Dùng canvas.find_overlapping để tìm cạnh nếu có.
        overlap = self.canvas.find_overlapping(
            x - tolerance, y - tolerance,
            x + tolerance, y + tolerance
        )
        for item in overlap:
            for edge in self.edges:
                if edge.get("line") == item:
                    return edge

        # Nếu không tìm thấy bằng canvas, dùng dự phòng bằng toán học.
        tol_sq = tolerance ** 2
        for edge in self.edges:
            if "line" not in edge or edge["line"] is None:
                continue

            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            x1, y1 = n1["x"], n1["y"]
            x2, y2 = n2["x"], n2["y"]

            if not (min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance and
                    min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance):
                continue

            dx = x2 - x1
            dy = y2 - y1
            dd = dx * dx + dy * dy
            if dd == 0:
                continue

            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / dd))
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

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
            self.canvas.coords(
                self.selected_node["circle"],
                self.selected_node["x"] - radius,
                self.selected_node["y"] - radius,
                self.selected_node["x"] + radius,
                self.selected_node["y"] + radius
            )
            self.canvas.coords(
                self.selected_node["text"],
                self.selected_node["x"],
                self.selected_node["y"]
            )
            self.drag_start = (event.x, event.y)
            self.redraw_edges()

    def on_apply_algorithm(self, event=None):
        """Khởi động thuật toán tô màu"""
        if not self.nodes:
            messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
            return
        self.welsh_powell_coloring()

    def on_canvas_click(self, event):
        """Xử lý khi click trên canvas"""
        self.selected_node = self.get_node_at(event.x, event.y)

        mode = self.mode_var.get()

        if mode == "delete":
            if self.selected_node:
                self.delete_node(self.selected_node)
        elif mode == "connect":
            if self.selected_node:
                if self.first_node_for_connection is None:
                    self.first_node_for_connection = self.selected_node
                    self.canvas.itemconfig(self.selected_node["circle"], width=4, outline="red")
                elif self.selected_node == self.first_node_for_connection:
                    self.canvas.itemconfig(self.selected_node["circle"], width=2, outline="black")
                    self.first_node_for_connection = None
                else:
                    self.connect_nodes(self.first_node_for_connection, self.selected_node)
                    self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
                    self.first_node_for_connection = None
        elif mode == "delete_edge":
            edge = self.get_edge_at(event.x, event.y)
            if edge:
                self.delete_edge(edge)
            else:
                messagebox.showwarning("Thông báo", "Không có cạnh nào tại vị trí này!")
        else:
            if self.selected_node:
                self.canvas.itemconfig(self.selected_node["circle"], width=3)
            self.drag_start = (event.x, event.y)

    def delete_node(self, node):
        """Xóa một nút"""
        # Xóa đường vẽ
        self.canvas.delete(node["circle"])
        self.canvas.delete(node["text"])
        
        # Xóa tất cả các cạnh liên quan đến nút này
        edges_to_remove = [
            e for e in self.edges
            if e["node1_id"] == node["id"] or e["node2_id"] == node["id"]
        ]
        
        # Cập nhật bậc khi xóa cạnh
        for edge in edges_to_remove:
            if edge.get("line") is not None:
                self.canvas.delete(edge["line"])
            other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
            if 0 <= other_node_id < len(self.nodes):
                self.nodes[other_node_id]["degree"] = max(0, self.nodes[other_node_id]["degree"] - 1)
        
        self.edges = [e for e in self.edges if e not in edges_to_remove]
        
        # Xóa nút khỏi danh sách
        self.nodes.remove(node)

        if self.selected_node == node:
            self.selected_node = None
        if self.first_node_for_connection == node:
            self.first_node_for_connection = None

        self._reindex_nodes()
        
        # Vẽ lại các cạnh
        self.redraw_edges()
        
        # messagebox.showinfo("Đã xóa", f"Nút {node['label']} đã bị xóa!")
    
    def connect_nodes(self, node1, node2):
        """Liên kết hai nút"""
        if node1["id"] == node2["id"]:
            messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
        else:
            n1_id, n2_id = node1["id"], node2["id"]
            
            # Kiểm tra cạnh tồn tại - tối ưu
            if any((e["node1_id"] == n1_id and e["node2_id"] == n2_id) or 
                   (e["node1_id"] == n2_id and e["node2_id"] == n1_id) for e in self.edges):
                messagebox.showwarning("Lỗi", "Cạnh này đã tồn tại!")
            else:
                self.edges.append({"node1_id": n1_id, "node2_id": n2_id, "line": None})
                self.nodes[n1_id]["degree"] += 1
                self.nodes[n2_id]["degree"] += 1
                self.redraw_edges()
                # messagebox.showinfo("Liên kết", f"Đã liên kết {node1['label']} ↔ {node2['label']}")
    
    def delete_edge(self, edge):
        """Xóa một cạnh"""
        node1 = self.nodes[edge["node1_id"]]
        node2 = self.nodes[edge["node2_id"]]

        # Cập nhật bậc
        node1["degree"] -= 1
        node2["degree"] -= 1

        if edge.get("line") is not None:
            self.canvas.delete(edge["line"])
        self.edges.remove(edge)
        self.redraw_edges()
    
    def on_toolbar_button_press(self, event):
        """Xử lý khi bấm nút 'Nút Mới' trong toolbar"""
        self.dragging_from_toolbar = True
        self.toolbar_dragged = False

    def on_toolbar_button_click(self):
        """Xử lý click bình thường trên nút 'Nút Mới'"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = canvas_width // 2
        y = canvas_height // 2
        new_node_count = len(self.nodes)
        label = str(new_node_count + 1)
        self.create_node(x, y, label, "white")

    def on_toolbar_button_drag(self, event):
        """Xử lý khi kéo nút 'Nút Mới' từ toolbar"""
        if self.dragging_from_toolbar:
            self.toolbar_dragged = True
            self.root.config(cursor="hand2")

    def on_toolbar_button_release(self, event):
        """Xử lý khi thả nút từ toolbar"""
        self.dragging_from_toolbar = False
        self.root.config(cursor="arrow")

        canvas_x = self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_rooty()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        inside_canvas = (
            canvas_x <= event.x_root <= canvas_x + canvas_width and
            canvas_y <= event.y_root <= canvas_y + canvas_height
        )

        if inside_canvas:
            x = event.x_root - canvas_x
            y = event.y_root - canvas_y
        elif not self.toolbar_dragged:
            x = canvas_width // 2
            y = canvas_height // 2
        else:
            return

        new_node_count = len(self.nodes)
        label = str(new_node_count + 1)
        self.create_node(x, y, label, "white")

    def welsh_powell_coloring(self):
        """Gọi hàm Welsh-Powell đã tách riêng và cập nhật giao diện."""
        node_colors = welsh_powell_coloring(self.nodes, self.edges)
        if not node_colors:
            messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
            return

        max_color = max(node_colors)
        for i, color_idx in enumerate(node_colors):
            self.nodes[i]["color"] = self.colors[color_idx % len(self.colors)]
            self.canvas.itemconfig(self.nodes[i]["circle"], fill=self.nodes[i]["color"])

        result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
        for color_idx in range(max_color + 1):
            nodes_in_color = [self.nodes[i]['label'] for i, c in enumerate(node_colors) if c == color_idx]
            result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"

        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
