# 🚀 R*-Tree vs R-Tree Performance Evaluation
**Course:** CPSC 4660 — Database Management Systems  
**Project Type:** Indexing Component — Advanced Method (R*-Tree)

---

## ✅ Project Goal

Implement the spatial index structure **R-Tree** and enhance it to **R\*-Tree**,  
then compare performance based on:

- average node visits during range search
- dataset distribution (clustered vs uniform)
- insertion & MBR (Minimum Bounding Rectangle) computation

---

## ✅ Why R\*-Tree?

|   Structure  |    Split Strategy   | Reinsertion         |       Performance            |
|--------------|---------------------|---------------------|------------------------------|
| **R-Tree**   |  basic split        | ❌ 없음               |adequate but produces overlap|
| **R\*-Tree** | optimized split     | ✅ forced reinsertion| better query performance    |

R\*-Tree reduces rectangle overlap and improves range-search performance.

---

## 📂 Project Structure
/ (root)
├── rstar_tree.py          # Full implementation of R-tree + R*-Tree
├── experiment.py          # Automatic experiment + benchmark + graph
├── rstar_vs_rtree.ipynb   # Notebook visualization
└── README.md

## 🚀 How to Run

### **1. Install dependencies**
```bash
pip install matplotlib pandas