"""Thuật toán Welsh-Powell tách riêng khỏi giao diện.

Hàm trong module này chỉ xử lý việc gán màu cho các nút dựa trên
độ lớn của bậc và danh sách các cạnh.
"""

from typing import List, Dict


def welsh_powell_coloring(nodes: List[Dict], edges: List[Dict]) -> List[int]:
    """Trả về danh sách màu cho từng nút theo thuật toán Welsh-Powell."""
    if not nodes:
        return []

    sorted_nodes = sorted(
        enumerate(nodes),
        key=lambda x: x[1]["degree"],
        reverse=True
    )

    node_colors = [-1] * len(nodes)
    node_colors[sorted_nodes[0][0]] = 0

    for idx, _ in sorted_nodes[1:]:
        neighbor_colors = set()
        for edge in edges:
            if edge["node1_id"] == idx and node_colors[edge["node2_id"]] != -1:
                neighbor_colors.add(node_colors[edge["node2_id"]])
            elif edge["node2_id"] == idx and node_colors[edge["node1_id"]] != -1:
                neighbor_colors.add(node_colors[edge["node1_id"]])

        color = 0
        while color in neighbor_colors:
            color += 1

        node_colors[idx] = color

    return node_colors
