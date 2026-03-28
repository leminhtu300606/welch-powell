import tkinter as tk
from tkinter import messagebox
import string

class WelshPowellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thuật toán Welch-Powell ")
        self.root.geometry("1100x700")
        
        # Frame chính chứa toolbar + canvas
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # ========== TOOLBAR BÊN TRÁI ==========
        self.toolbar = tk.Frame(main_frame, bg="#2c3e50", width=120, relief="sunken", bd=2)
        self.toolbar.pack(side="left", fill="y", padx=5, pady=5)
        self.toolbar.pack_propagate(False)
        
        # Tiêu đề toolbar
        tk.Label(
            self.toolbar,
            text="🛠️ Công Cụ",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=10)
        
        # Nút thêm nút
        self.node_btn = tk.Button(
            self.toolbar,
            text="➕ Nút Mới",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            width=12,
            height=2
        )
        self.node_btn.pack(pady=10)
        self.node_btn.bind("<Button-1>", self.on_toolbar_button_press)
        self.node_btn.bind("<B1-Motion>", self.on_toolbar_button_drag)
        self.node_btn.bind("<ButtonRelease-1>", self.on_toolbar_button_release)
        
        # Khoảng cách
        tk.Label(self.toolbar, bg="#2c3e50").pack(pady=10)
        
        # Chế độ
        tk.Label(
            self.toolbar,
            text="Chế độ:",
            font=("Arial", 10, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=5)
        
        self.mode_var = tk.StringVar(value="move")
        
        tk.Radiobutton(
            self.toolbar, text="Di chuyển",
            variable=self.mode_var, value="move",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)
        
        tk.Radiobutton(
            self.toolbar, text="Xóa nút",
            variable=self.mode_var, value="delete",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)
        
        tk.Radiobutton(
            self.toolbar, text="Nối nút",
            variable=self.mode_var, value="connect",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)
        
        tk.Radiobutton(
            self.toolbar, text="Xóa cạnh",
            variable=self.mode_var, value="delete_edge",
            bg="#2c3e50", fg="white", selectcolor="#34495e",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)
        
        # Khoảng cách
        tk.Label(self.toolbar, bg="#2c3e50").pack(pady=20, expand=True)
        
        # Nút chạy thuật toán
        self.run_btn = tk.Button(
            self.toolbar,
            text="▶ Chạy",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            width=12,
            height=2,
            command=self.on_apply_algorithm
        )
        self.run_btn.pack(pady=10)
        
        # ========== CANVAS GIỮA ==========
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="lightblue", cursor="arrow")
        self.canvas.pack(fill="both", expand=True)
        
        # Danh sách các nút
        self.nodes = []
        self.selected_node = None
        self.drag_start = None
        
        # Danh sách các cạnh
        self.edges = []
        self.first_node_for_connection = None
        
        # Cho drag từ toolbar
        self.dragging_from_toolbar = False
        
        # Màu sắc
        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B88B", "#81ECEC"
        ]
        
        # Bind sự kiện canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Control-Button-1>", self.on_ctrl_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        # Tạo vài nút mặc định
        self.create_node(200, 150, "A", "white")
        self.create_node(400, 150, "B", "white")
        self.create_node(600, 150, "C", "white")
    
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

    def on_ctrl_click(self, event):
        """Xử lý CTRL+click để nối hai nút"""
        node = self.get_node_at(event.x, event.y)
        if node:
            if self.first_node_for_connection is None:
                self.first_node_for_connection = node
                self.canvas.itemconfig(node["circle"], outline="red", width=3)
                messagebox.showinfo("Liên kết", f"Đã chọn nút {node['label']}. CTRL+Click nút thứ 2!")
            else:
                if node["id"] == self.first_node_for_connection["id"]:
                    messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
                else:
                    self.connect_nodes(self.first_node_for_connection, node)
                self.canvas.itemconfig(self.first_node_for_connection["circle"], outline="black", width=2)
                self.first_node_for_connection = None

    def on_right_click(self, event):
        """Xử lý click phải để xóa cạnh"""
        edge = self.get_edge_at(event.x, event.y)
        if edge:
            node1 = self.nodes[edge["node1_id"]]
            node2 = self.nodes[edge["node2_id"]]
            result = messagebox.askyesno("Xóa cạnh", f"Bạn có muốn xóa cạnh giữa {node1['label']} và {node2['label']}?")
            if result:
                self.delete_edge(edge)
        else:
            messagebox.showinfo("Thông báo", "Không có cạnh nào tại vị trí này!")

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
                    # Highlight
                    self.canvas.itemconfig(self.selected_node["circle"], width=4, outline="red")
                elif self.selected_node == self.first_node_for_connection:
                    # Deselect if clicking the same node
                    self.canvas.itemconfig(self.selected_node["circle"], width=2, outline="black")
                    self.first_node_for_connection = None
                else:
                    # Connect to different node
                    self.connect_nodes(self.first_node_for_connection, self.selected_node)
                    # Reset highlight
                    self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
                    self.first_node_for_connection = None
        elif mode == "delete_edge":
            edge = self.get_edge_at(event.x, event.y)
            if edge:
                self.delete_edge(edge)
            else:
                messagebox.showwarning("Thông báo", "Không có cạnh nào tại vị trí này!")
        else:  # move
            if self.selected_node:
                # Highlight nút được chọn
                self.canvas.itemconfig(
                    self.selected_node["circle"],
                    width=3
                )
            
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
            other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
            self.nodes[other_node_id]["degree"] -= 1
        
        self.edges = [e for e in self.edges if e not in edges_to_remove]
        
        # Xóa nút khỏi danh sách
        self.nodes.remove(node)
        
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
    
    def on_toolbar_button_drag(self, event):
        """Xử lý khi kéo nút 'Nút Mới' từ toolbar"""
        if self.dragging_from_toolbar:
            # Đổi con trỏ chuột
            self.root.config(cursor="hand2")
    
    def on_toolbar_button_release(self, event):
        """Xử lý khi thả nút từ toolbar"""
        self.dragging_from_toolbar = False
        self.root.config(cursor="arrow")
        
        # Kiểm tra xem có thả vào canvas không
        canvas_x = self.canvas.winfo_x()
        canvas_y = self.canvas.winfo_y()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if (canvas_x <= event.x_root <= canvas_x + canvas_width and
            canvas_y <= event.y_root <= canvas_y + canvas_height):
            # Tạo nút mới tại vị trí thả
            x = event.x_root - canvas_x
            y = event.y_root - canvas_y
            
            new_node_count = len(self.nodes)
            alphabet = list(string.ascii_uppercase)
            label = alphabet[new_node_count] if new_node_count < 26 else f"N{new_node_count}"
            
            self.create_node(x, y, label, "white")

    def welsh_powell_coloring(self):
        """Thuật toán Welch-Powell - tối ưu"""
        # Bước 1: Sắp xếp nút theo bậc giảm dần
        sorted_nodes = sorted(enumerate(self.nodes), key=lambda x: x[1]["degree"], reverse=True)
        
        # Bước 2-3: Gán màu
        node_colors = [-1] * len(self.nodes)
        node_colors[sorted_nodes[0][0]] = 0
        
        for idx, _ in sorted_nodes[1:]:
            # Tìm màu các hàng xóm - tối ưu
            neighbor_colors = set()
            for edge in self.edges:
                if edge["node1_id"] == idx and node_colors[edge["node2_id"]] != -1:
                    neighbor_colors.add(node_colors[edge["node2_id"]])
                elif edge["node2_id"] == idx and node_colors[edge["node1_id"]] != -1:
                    neighbor_colors.add(node_colors[edge["node1_id"]])
            
            # Tìm màu nhỏ nhất
            color = 0
            while color in neighbor_colors:
                color += 1
            
            node_colors[idx] = color
        
        # Cập nhật canvas
        max_color = max(node_colors)
        for i, color_idx in enumerate(node_colors):
            self.nodes[i]["color"] = self.colors[color_idx % len(self.colors)]
            self.canvas.itemconfig(self.nodes[i]["circle"], fill=self.nodes[i]["color"])
        
        # Hiển thị kết quả - tối ưu
        result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
        for color_idx in range(max_color + 1):
            nodes_in_color = [self.nodes[i]['label'] for i, c in enumerate(node_colors) if c == color_idx]
            result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"
        
        # Tạo cửa sổ kết quả
        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        
        tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
