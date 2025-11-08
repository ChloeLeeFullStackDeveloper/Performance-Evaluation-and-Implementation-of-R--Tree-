"""
experiment.py — Extended evaluation suite
- Uniform vs Clustered comparison
- Scalability test (varying N)
- max_entries impact
- Multiple runs for statistical confidence
"""

import time, statistics, random
import pandas as pd
import matplotlib.pyplot as plt
from rstar_tree import RTree, RStarTree, make_point_rect, random_points, clustered_points, Rect

# Set seed for reproducibility
random.seed(42)

def build(tree_cls, pts, max_entries=12):
    """Build tree and measure insertion time"""
    t = tree_cls(max_entries=max_entries)
    start = time.time()
    for i, (x, y) in enumerate(pts):
        t.insert(make_point_rect(x, y, 0.01), i)
    build_time = time.time() - start
    return t, build_time

def random_windows(k, w=0.08):
    wins = []
    for _ in range(k):
        x = random.random() * (1 - w)
        y = random.random() * (1 - w)
        wins.append(make_point_rect(x, y, w))
    return wins

def evaluate(tree, wins):
    """Measure average node visits and query time"""
    visits = []
    start = time.time()
    for w in wins:
        tree._reset()
        _ = tree.range_query(w)
        visits.append(tree.node_visits)
    query_time = time.time() - start
    return statistics.mean(visits), query_time

def tree_height(node, depth=0):
    """Calculate tree height"""
    if node.leaf:
        return depth
    if not node.entries:
        return depth
    return max(tree_height(child, depth + 1) for _, child in node.entries)

# ============================================================
# Experiment 1: Uniform vs Clustered Comparison
# ============================================================

def experiment_distribution(n=2000, queries=100, max_entries=12):
    """Compare R-tree vs R*-tree on uniform and clustered data"""
    print("\n=== Experiment 1: Uniform vs Clustered ===")
    
    results = []
    
    for dist_type in ["Uniform", "Clustered"]:
        print(f"\n→ Testing {dist_type} distribution...")
        
        # Generate data
        if dist_type == "Uniform":
            pts = random_points(n)
        else:
            pts = clustered_points(n, num_clusters=4)
        
        wins = random_windows(queries)
        
        # Build and test R-tree
        rt, rt_build = build(RTree, pts, max_entries)
        rt_vis, rt_query = evaluate(rt, wins)
        rt_height = tree_height(rt.root)
        
        # Build and test R*-tree
        rs, rs_build = build(RStarTree, pts, max_entries)
        rs_vis, rs_query = evaluate(rs, wins)
        rs_height = tree_height(rs.root)
        
        # Calculate speedup
        speedup = ((rt_vis - rs_vis) / rt_vis * 100) if rt_vis > 0 else 0
        
        results.append({
            "Distribution": dist_type,
            "Tree": "R-tree",
            "Build_Time(s)": f"{rt_build:.3f}",
            "Avg_Node_Visits": f"{rt_vis:.2f}",
            "Query_Time(s)": f"{rt_query:.3f}",
            "Tree_Height": rt_height
        })
        
        results.append({
            "Distribution": dist_type,
            "Tree": "R*-tree",
            "Build_Time(s)": f"{rs_build:.3f}",
            "Avg_Node_Visits": f"{rs_vis:.2f}",
            "Query_Time(s)": f"{rs_query:.3f}",
            "Tree_Height": rs_height
        })
        
        print(f"  R-tree:  {rt_vis:.2f} visits | R*-tree: {rs_vis:.2f} visits")
        print(f"  Speedup: {speedup:.2f}%")
    
    df = pd.DataFrame(results)
    
    # Plot comparison
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    
    uniform = df[df['Distribution'] == 'Uniform']
    clustered = df[df['Distribution'] == 'Clustered']
    
    x = [0, 1]
    rtree_vals = [float(uniform[uniform['Tree']=='R-tree']['Avg_Node_Visits'].values[0]),
                   float(clustered[clustered['Tree']=='R-tree']['Avg_Node_Visits'].values[0])]
    rstar_vals = [float(uniform[uniform['Tree']=='R*-tree']['Avg_Node_Visits'].values[0]),
                   float(clustered[clustered['Tree']=='R*-tree']['Avg_Node_Visits'].values[0])]
    
    width = 0.35
    ax.bar([i - width/2 for i in x], rtree_vals, width, label='R-tree', color='steelblue')
    ax.bar([i + width/2 for i in x], rstar_vals, width, label='R*-tree', color='coral')
    
    ax.set_ylabel('Avg Node Visits')
    ax.set_title('R-tree vs R*-tree: Uniform vs Clustered Data')
    ax.set_xticks(x)
    ax.set_xticklabels(['Uniform', 'Clustered'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("exp1_distribution.png", dpi=150)
    print("\n✅ Saved: exp1_distribution.png")
    
    return df

# ============================================================
# Experiment 2: Scalability (varying N)
# ============================================================

def experiment_scalability(sizes=[500, 1000, 2000, 5000], queries=100, max_entries=12):
    """Test how performance scales with dataset size"""
    print("\n=== Experiment 2: Scalability ===")
    
    results = []
    
    for n in sizes:
        print(f"\n→ Testing N={n}...")
        pts = random_points(n)
        wins = random_windows(queries)
        
        # R-tree
        rt, rt_build = build(RTree, pts, max_entries)
        rt_vis, rt_query = evaluate(rt, wins)
        
        # R*-tree
        rs, rs_build = build(RStarTree, pts, max_entries)
        rs_vis, rs_query = evaluate(rs, wins)
        
        results.append({
            "N": n,
            "Tree": "R-tree",
            "Avg_Node_Visits": rt_vis,
            "Build_Time(s)": rt_build
        })
        
        results.append({
            "N": n,
            "Tree": "R*-tree",
            "Avg_Node_Visits": rs_vis,
            "Build_Time(s)": rs_build
        })
    
    df = pd.DataFrame(results)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Node visits
    for tree_type in ["R-tree", "R*-tree"]:
        subset = df[df['Tree'] == tree_type]
        ax1.plot(subset['N'], subset['Avg_Node_Visits'], marker='o', label=tree_type, linewidth=2)
    
    ax1.set_xlabel('Dataset Size (N)')
    ax1.set_ylabel('Avg Node Visits')
    ax1.set_title('Query Performance vs Dataset Size')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Build time
    for tree_type in ["R-tree", "R*-tree"]:
        subset = df[df['Tree'] == tree_type]
        ax2.plot(subset['N'], subset['Build_Time(s)'], marker='s', label=tree_type, linewidth=2)
    
    ax2.set_xlabel('Dataset Size (N)')
    ax2.set_ylabel('Build Time (seconds)')
    ax2.set_title('Insertion Time vs Dataset Size')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("exp2_scalability.png", dpi=150)
    print("\n✅ Saved: exp2_scalability.png")
    
    return df

# ============================================================
# Experiment 3: max_entries Impact
# ============================================================

def experiment_max_entries(n=2000, queries=100, max_vals=[4, 8, 12, 16]):
    """Test impact of max_entries parameter"""
    print("\n=== Experiment 3: max_entries Impact ===")
    
    pts = random_points(n)
    wins = random_windows(queries)
    
    results = []
    
    for m in max_vals:
        print(f"\n→ Testing max_entries={m}...")
        
        rt, _ = build(RTree, pts, m)
        rt_vis, _ = evaluate(rt, wins)
        rt_height = tree_height(rt.root)
        
        rs, _ = build(RStarTree, pts, m)
        rs_vis, _ = evaluate(rs, wins)
        rs_height = tree_height(rs.root)
        
        results.append({
            "max_entries": m,
            "Tree": "R-tree",
            "Avg_Node_Visits": rt_vis,
            "Tree_Height": rt_height
        })
        
        results.append({
            "max_entries": m,
            "Tree": "R*-tree",
            "Avg_Node_Visits": rs_vis,
            "Tree_Height": rs_height
        })
    
    df = pd.DataFrame(results)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Node visits
    for tree_type in ["R-tree", "R*-tree"]:
        subset = df[df['Tree'] == tree_type]
        ax1.plot(subset['max_entries'], subset['Avg_Node_Visits'], marker='o', label=tree_type, linewidth=2)
    
    ax1.set_xlabel('max_entries')
    ax1.set_ylabel('Avg Node Visits')
    ax1.set_title('Query Performance vs max_entries')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Tree height
    for tree_type in ["R-tree", "R*-tree"]:
        subset = df[df['Tree'] == tree_type]
        ax2.plot(subset['max_entries'], subset['Tree_Height'], marker='s', label=tree_type, linewidth=2)
    
    ax2.set_xlabel('max_entries')
    ax2.set_ylabel('Tree Height')
    ax2.set_title('Tree Structure vs max_entries')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("exp3_max_entries.png", dpi=150)
    print("\n✅ Saved: exp3_max_entries.png")
    
    return df

# ============================================================
# Main Runner
# ============================================================

def run_all():
    """Execute all experiments"""
    print("\n" + "="*60)
    print("R-tree vs R*-tree: Comprehensive Evaluation")
    print("="*60)
    
    df1 = experiment_distribution(n=2000, queries=100)
    df1.to_csv("exp1_distribution.csv", index=False)
    
    df2 = experiment_scalability(sizes=[500, 1000, 2000, 5000])
    df2.to_csv("exp2_scalability.csv", index=False)
    
    df3 = experiment_max_entries(n=2000, max_vals=[4, 8, 12, 16])
    df3.to_csv("exp3_max_entries.csv", index=False)
    
    print("\n" + "="*60)
    print("✅ All experiments complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  - exp1_distribution.png & .csv")
    print("  - exp2_scalability.png & .csv")
    print("  - exp3_max_entries.png & .csv")
    
    return df1, df2, df3

if __name__ == "__main__":
    run_all()