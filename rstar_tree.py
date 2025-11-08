"""
rstar_tree.py — Stable R-Tree / R*-Tree implementation
- Flexible make_point_rect(x, y [, size]) OR (x1, y1, x2, y2)
- Safe parent pointer handling on split
- Base R-tree (linear split) + R*-tree (single-pass forced reinsertion)
- Range query + node visit counter for experiments
- Added: clustered_points() for generating Gaussian clusters
"""

import random
from typing import List, Tuple, Any, Optional


# ==========================================================
# Geometry: axis-aligned rectangle (MBR)
# ==========================================================

class Rect:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        # normalize
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)

    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)

    def enlarge(self, other: "Rect") -> "Rect":
        return Rect(
            min(self.x1, other.x1),
            min(self.y1, other.y1),
            max(self.x2, other.x2),
            max(self.y2, other.y2),
        )

    def intersects(self, other: "Rect") -> bool:
        return not (self.x2 < other.x1 or self.x1 > other.x2 or
                    self.y2 < other.y1 or self.y1 > other.y2)


# ==========================================================
# Helpers (flexible rect + synthetic data)
# ==========================================================

def make_point_rect(*args) -> Rect:
    """
    Flexible rectangle creation:
      - (x, y)                 -> zero-area point rect
      - (x, y, size)           -> [x, x+size] × [y, y+size]
      - (x1, y1, x2, y2)       -> explicit rectangle
    """
    if len(args) == 2:
        x, y = args
        return Rect(x, y, x, y)
    elif len(args) == 3:
        x, y, size = args
        return Rect(x, y, x + size, y + size)
    elif len(args) == 4:
        x1, y1, x2, y2 = args
        return Rect(x1, y1, x2, y2)
    else:
        raise TypeError(f"make_point_rect() takes 2, 3, or 4 arguments ({len(args)} given)")


def random_points(n: int) -> List[Tuple[float, float]]:
    """Generate n uniformly random points in [0, 1] × [0, 1]"""
    return [(random.random(), random.random()) for _ in range(n)]


def clustered_points(n: int, num_clusters: int = 4) -> List[Tuple[float, float]]:
    """
    Generate clustered points using Gaussian distribution.
    Creates num_clusters centers, then generates points around each.
    
    Parameters:
    - n: total number of points
    - num_clusters: number of cluster centers
    
    Returns:
    - List of (x, y) coordinates
    """
    points = []
    cluster_size = n // num_clusters
    
    for _ in range(num_clusters):
        # Random cluster center
        cx = random.random()
        cy = random.random()
        
        # Generate points around center (std=0.08 for moderate clustering)
        for _ in range(cluster_size):
            x = random.gauss(cx, 0.08)
            y = random.gauss(cy, 0.08)
            # Clamp to [0, 1]
            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))
            points.append((x, y))
    
    # Handle remainder if n not divisible by num_clusters
    remainder = n - len(points)
    if remainder > 0:
        cx = random.random()
        cy = random.random()
        for _ in range(remainder):
            x = max(0.0, min(1.0, random.gauss(cx, 0.08)))
            y = max(0.0, min(1.0, random.gauss(cy, 0.08)))
            points.append((x, y))
    
    return points


# ==========================================================
# Node
# ==========================================================

class Node:
    def __init__(self, leaf: bool = False):
        self.leaf = leaf
        # entries: List[Tuple[Rect, Node|Any]]
        self.entries: List[Tuple[Rect, Any]] = []
        self.parent: Optional["Node"] = None

    def add(self, rect: Rect, child_or_data: Any):
        # if internal child is Node, wire parent pointer
        if isinstance(child_or_data, Node):
            child_or_data.parent = self
        self.entries.append((rect, child_or_data))

    def mbr(self) -> Rect:
        assert self.entries, "mbr() called on empty node"
        r, _ = self.entries[0]
        for i in range(1, len(self.entries)):
            r = r.enlarge(self.entries[i][0])
        return r


# ==========================================================
# Base R-Tree (linear split; adequate for course experiment)
# ==========================================================

class RTree:
    def __init__(self, max_entries: int = 8):
        self.max_entries = max_entries
        self.root = Node(leaf=True)
        self.node_visits = 0

    # ---- metric helpers ----
    def _reset(self):
        self.node_visits = 0

    def _visit(self):
        self.node_visits += 1

    # ---- queries ----
    def range_query(self, rect: Rect, node: Optional[Node] = None):
        if node is None:
            node = self.root
        self._visit()

        out = []
        for r, c in node.entries:
            if not rect.intersects(r):
                continue
            if node.leaf:
                out.append(c)  # data
            else:
                out.extend(self.range_query(rect, c))
        return out

    # ---- insert path ----
    def choose_leaf(self, node: Node, rect: Rect) -> Node:
        # heuristic: minimal area enlargement; tie by area
        if node.leaf:
            return node
        best_child = None
        best_key = None
        for r, child in node.entries:
            inc = r.enlarge(rect).area() - r.area()
            key = (inc, r.area())
            if best_key is None or key < best_key:
                best_key = key
                best_child = child
        return self.choose_leaf(best_child, rect)

    def insert(self, rect: Rect, data: Any):
        leaf = self.choose_leaf(self.root, rect)
        leaf.add(rect, data)
        if len(leaf.entries) > self.max_entries:
            self.adjust_after_split(leaf)

    # ---- split + upward adjust (SAFE PARENT VERSION) ----
    def split_node(self, node: Node) -> Node:
        """
        Linear split: cut entries into two halves.
        Also fixes children's parent pointers for both halves.
        """
        half = max(1, len(node.entries) // 2)
        new_node = Node(leaf=node.leaf)

        # slice
        right_half = node.entries[half:]
        node.entries = node.entries[:half]
        new_node.entries = right_half

        # fix parent pointers in both halves (internal only)
        if not node.leaf:
            for _, child in node.entries:
                child.parent = node
            for _, child in new_node.entries:
                child.parent = new_node

        return new_node

    def adjust_after_split(self, node: Node):
        """
        After overflow at 'node', split once, then
        - if node was root: create new root and wire parents
        - else: add new_node to parent; recurse if parent overflows
        """
        new_node = self.split_node(node)

        if node is self.root:
            new_root = Node(leaf=False)
            new_root.add(node.mbr(), node)
            new_root.add(new_node.mbr(), new_node)
            node.parent = new_root
            new_node.parent = new_root
            self.root = new_root
            return

        parent = node.parent
        parent.add(new_node.mbr(), new_node)
        if len(parent.entries) > self.max_entries:
            self.adjust_after_split(parent)

    # convenience (used by R*-tree reinsertion to update mbrs up the path)
    def _bubble_up_mbr(self, node: Optional[Node]):
        while node and node.parent:
            p = node.parent
            new_m = node.mbr()
            for i, (r, c) in enumerate(p.entries):
                if c is node:
                    p.entries[i] = (new_m, c)
                    break
            node = p


# ==========================================================
# R*-Tree: forced reinsertion (single-pass; safe)
# ==========================================================

class RStarTree(RTree):
    def __init__(self, max_entries: int = 8, reinsertion_ratio: float = 0.3):
        super().__init__(max_entries=max_entries)
        self.reinsertion_ratio = reinsertion_ratio  # 0.2–0.3 recommended

    def insert(self, rect: Rect, data: Any):
        leaf = self.choose_leaf(self.root, rect)
        leaf.add(rect, data)

        if len(leaf.entries) > self.max_entries:
            self._forced_reinsert_once(leaf)

        # still overflow? split
        if len(leaf.entries) > self.max_entries:
            self.adjust_after_split(leaf)
        else:
            self._bubble_up_mbr(leaf)

    def _forced_reinsert_once(self, node: Node):
        """
        Remove farthest k entries from node and reinsert from the root.
        Only once for the current overflow to avoid ping-pong loops.
        """
        entries = list(node.entries)
        if len(entries) <= self.max_entries:
            return

        m = node.mbr()
        cx = (m.x1 + m.x2) / 2.0
        cy = (m.y1 + m.y2) / 2.0

        ranked = sorted(
            entries,
            key=lambda rc: ((rc[0].x1 + rc[0].x2) / 2.0 - cx) ** 2 +
                           ((rc[0].y1 + rc[0].y2) / 2.0 - cy) ** 2,
            reverse=True
        )

        k = max(1, int(round(self.reinsertion_ratio * len(entries))))
        k = min(k, len(entries) - 1)  # keep at least one

        to_reinsert = ranked[:k]
        keep = [e for e in entries if e not in to_reinsert]
        node.entries = keep

        for r, payload in to_reinsert:
            super().insert(r, payload)

        self._bubble_up_mbr(node)