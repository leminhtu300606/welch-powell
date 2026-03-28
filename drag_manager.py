import string
from tkinter import messagebox

class DragManager:
    def on_canvas_click(self, event):
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

    def on_canvas_drag(self, event):
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
            self.canvas.coords(self.selected_node["text"], self.selected_node["x"], self.selected_node["y"])
            self.drag_start = (event.x, event.y)
            self.redraw_edges()

    def on_ctrl_click(self, event):
        node = self.get_node_at(event.x, event.y)
        if node:
            if self.first_node_for_connection is None:
                self.first_node_for_connection = node
                self.canvas.itemconfig(node["circle"], outline="red", width=3)
                messagebox.showinfo("Liên kết", f"Đã chọn nút {node['label']}. CTRL+Click nút thứ 2!")
            else:
                self.connect_nodes(self.first_node_for_connection, node)
                self.canvas.itemconfig(self.first_node_for_connection["circle"], outline="black", width=2)
                self.first_node_for_connection = None

    def on_right_click(self, event):
        edge = self.get_edge_at(event.x, event.y)
        if edge:
            node1 = self.nodes[edge["node1_id"]]
            node2 = self.nodes[edge["node2_id"]]
            result = messagebox.askyesno("Xóa cạnh", f"Bạn có muốn xóa cạnh giữa {node1['label']} và {node2['label']}?")
            if result:
                self.delete_edge(edge)
        else:
            messagebox.showinfo("Thông báo", "Không có cạnh nào tại vị trí này!")

    def on_toolbar_button_press(self, event):
        self.dragging_from_toolbar = True

    def on_toolbar_button_drag(self, event):
        if self.dragging_from_toolbar:
            self.root.config(cursor="hand2")

    def on_toolbar_button_release(self, event):
        self.dragging_from_toolbar = False
        self.root.config(cursor="arrow")

        canvas_x = self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_rooty()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (canvas_x <= event.x_root <= canvas_x + canvas_width and
            canvas_y <= event.y_root <= canvas_y + canvas_height):
            x = event.x_root - canvas_x
            y = event.y_root - canvas_y
            new_node_count = len(self.nodes)
            alphabet = list(string.ascii_uppercase)
            label = alphabet[new_node_count] if new_node_count < 26 else f"N{new_node_count}"
            self.create_node(x, y, label, "white")