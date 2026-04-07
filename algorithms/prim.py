import heapq

def prim(nodes, edges, start_id=0):
    """
    Thuật toán Prim tìm cây khung nhỏ nhất (MST)
    Trả về danh sách cạnh dạng (u, v)
    """

    n = len(nodes)
    if n == 0:
        return []

    # Tạo adjacency list
    adj = [[] for _ in range(n)]
    for e in edges:
        u = e["node1_id"]
        v = e["node2_id"]
        w = e.get("weight", 1)

        adj[u].append((w, v))
        adj[v].append((w, u))

    visited = [False] * n
    min_heap = [(0, start_id, -1)]  # (weight, node, parent)

    mst_edges = []

    while min_heap:
        weight, u, parent = heapq.heappop(min_heap)

        if visited[u]:
            continue

        visited[u] = True

        # Nếu không phải node bắt đầu
        if parent != -1:
            mst_edges.append((parent, u))

        for w, v in adj[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (w, v, u))

    return mst_edges