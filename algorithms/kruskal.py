def find(parent, u):
    """Tìm gốc của u (có nén đường đi)"""
    if parent[u] != u:
        parent[u] = find(parent, parent[u])
    return parent[u]


def union(parent, rank, u, v):
    """Hợp nhất 2 tập hợp"""
    root_u = find(parent, u)
    root_v = find(parent, v)

    if root_u == root_v:
        return False  # tạo chu trình

    if rank[root_u] < rank[root_v]:
        parent[root_u] = root_v
    else:
        parent[root_v] = root_u
        if rank[root_u] == rank[root_v]:
            rank[root_u] += 1

    return True


def kruskal(nodes, edges):
    """
    Thuật toán Kruskal tìm cây khung nhỏ nhất (MST)
    Trả về danh sách cạnh dạng (u, v)
    """

    n = len(nodes)
    if n == 0:
        return []

    parent = list(range(n))
    rank = [0] * n

    # Sắp xếp cạnh theo trọng số tăng dần
    sorted_edges = sorted(edges, key=lambda e: e.get("weight", 1))

    mst_edges = []

    for e in sorted_edges:
        u = e["node1_id"]
        v = e["node2_id"]

        if union(parent, rank, u, v):
            mst_edges.append((u, v))

    return mst_edges