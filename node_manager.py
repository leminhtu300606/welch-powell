class NodeManager:
    def create_node(self, x, y, label, color):
        """Tạo một nút mới"""
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

        circle_id = self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color,
            outline="black",
            width=2
        )

        text_id = self.canvas.create_text(
            x, y,
            text=label,
            fill="black",
            font=("Arial", 12, "bold")
        )

        node_data["circle"] = circle_id
        node_data["text"] = text_id
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        """Tìm nút tại vị trí cho trước"""
        for node in reversed(self.nodes):
            if (x - node["x"]) ** 2 + (y - node["y"]) ** 2 <= node["radius"] ** 2:
                return node
        return None

    def delete_node(self, node):
        """Xóa một nút và các cạnh liên quan"""
        self.canvas.delete(node["circle"])
        self.canvas.delete(node["text"])

        edges_to_remove = [
            e for e in self.edges
            if e["node1_id"] == node["id"] or e["node2_id"] == node["id"]
        ]

        for edge in edges_to_remove:
            other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
            self.nodes[other_node_id]["degree"] -= 1

        self.edges = [e for e in self.edges if e not in edges_to_remove]
        self.nodes.remove(node)
        self.redraw_edges()