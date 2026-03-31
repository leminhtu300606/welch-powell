
from typing import List, Dict

def welsh_powell_coloring(nodes: List[Dict], edges: List[Dict]) -> List[int]:
    """Tính chỉ số màu của từng nút theo thuật toán Welsh-Powell."""
    if not nodes:
        return []

    indexed_nodes = sorted(
        enumerate(nodes),
        key=lambda pair: pair[1]["degree"],
        reverse=True
    )

    assigned_colors = [-1] * len(nodes)
    first_node_index = indexed_nodes[0][0]
    assigned_colors[first_node_index] = 0

    for node_index, _node_data in indexed_nodes[1:]:
        used_neighbor_colors = set()
        for edge in edges:
            if edge["node1_id"] == node_index:
                neighbor_index = edge["node2_id"]
                neighbor_color = assigned_colors[neighbor_index]
                if neighbor_color != -1:
                    used_neighbor_colors.add(neighbor_color)
            elif edge["node2_id"] == node_index:
                neighbor_index = edge["node1_id"]
                neighbor_color = assigned_colors[neighbor_index]
                if neighbor_color != -1:
                    used_neighbor_colors.add(neighbor_color)

        color_to_assign = 0
        while color_to_assign in used_neighbor_colors:
            color_to_assign += 1

        assigned_colors[node_index] = color_to_assign

    return assigned_colors
