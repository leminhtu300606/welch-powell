"""welsh_powell.py - Cài đặt thuật toán Welsh-Powell cho tô màu đỉnh đồ thị."""

from typing import Dict, List


def welsh_powell_coloring(nodes: List[Dict], edges: List[Dict]) -> List[int]:
    """Color graph vertices with Welsh-Powell heuristic.

    Returns a color index list aligned with the input ``nodes`` order.
    """
    node_count = len(nodes)
    if node_count == 0:
        return []

    ordered_indices = sorted(
        range(node_count),
        key=lambda idx: nodes[idx].get("degree", 0),
        reverse=True,
    )

    id_to_index = {
        node.get("id", index): index
        for index, node in enumerate(nodes)
    }
    adjacency = [set() for _ in range(node_count)]

    for edge in edges:
        left = id_to_index.get(edge.get("node1_id"))
        right = id_to_index.get(edge.get("node2_id"))
        if left is None or right is None or left == right:
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)

    assigned_colors = [-1] * node_count
    uncolored_count = node_count
    current_color = 0

    while uncolored_count:
        same_color_nodes = set()

        for node_index in ordered_indices:
            if assigned_colors[node_index] != -1:
                continue
            if adjacency[node_index] & same_color_nodes:
                continue

            assigned_colors[node_index] = current_color
            same_color_nodes.add(node_index)
            uncolored_count -= 1

        current_color += 1

    return assigned_colors
