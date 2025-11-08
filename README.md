# Performance Evaluation and Implementation of R*-Tree (vs R-Tree)

**CPSC 4660 - Database Management Systems (Fall 2025)**

**Team:** Project Group B  
---

This project implements **R-tree** and **R\*-tree** from scratch in Python and evaluates
their performance under three conditions:

1. Different data distributions (uniform vs clustered)
2. Scalability with dataset size (N = 500 → 5000)
3. Effect of varying `max_entries` (node capacity)

All experiment results (plots + raw CSV data) are automatically generated when running the main script.

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/ChloeLeeFullStackDeveloper/Performance-Evaluation-and-Implementation-of-R--Tree-.git
cd Performance-Evaluation-and-Implementation-of-R--Tree-
```

### 2. (Optional) Create & activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.\.venv\Scripts\activate         # Windows   
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run all experiments (generates 3 CSV + 3 PNG plots)
```bash
python experiment.py --all
```

Or, run individually:
```bash
python experiment.py --distribution     # uniform vs clustered
python experiment.py --scalability      # N = {500,1000,2000,5000}
python experiment.py --max-entries      # max_entries = {4,8,12,16}
```

### 5. View results
After execution, the generated files appear in the `results/` directory:
```
results/
  ├── exp1_distribution.csv
  ├── exp1_distribution.png
  ├── exp2_scalability.csv
  ├── exp2_scalability.png
  ├── exp3_max_entries.csv
  └── exp3_max_entries.png
```

---

## 📂 Project Structure

```
.
├── rstar_tree.py              # R-tree & R*-tree implementation
├── experiment.py              # Experiment runner and benchmark
├── results/                   # Generated experiment outputs
│   ├── exp1_distribution.csv
│   ├── exp1_distribution.png
│   ├── exp2_scalability.csv
│   ├── exp2_scalability.png
│   ├── exp3_max_entries.csv
│   └── exp3_max_entries.png
├── README.md                  # Setup and usage instructions
└── requirements.txt           # Python dependencies
```

### Key Files

**rstar_tree.py**
- `Rect`: Minimum Bounding Rectangle (MBR) with geometric operations
- `Node`: Tree node with safe parent pointer handling
- `RTree`: Base R-tree with linear split
- `RStarTree`: Advanced R*-tree with forced reinsertion

**experiment.py**
- `experiment_distribution()`: Compare uniform vs clustered datasets
- `experiment_scalability()`: Test dataset sizes from 500 to 5000 points
- `experiment_max_entries()`: Evaluate different max_entries values

---

## 🧪 Testing

Run the automated test suite to verify everything works:

```bash
python test_submission.py
```

This will check:
- ✅ Dependencies installed
- ✅ Code imports successfully
- ✅ Experiments run without errors
- ✅ Output files generated correctly
- ✅ CSV data is valid
- ✅ Code documentation exists

---

## 📊 Experiments

### Experiment 1: Data Distribution
Compares R-tree vs R*-tree performance on:
- Uniformly distributed points
- Clustered points (Gaussian distribution)

**Metric:** Average node visits per range query

### Experiment 2: Scalability
Tests how performance scales with dataset size:
- N = 500, 1000, 2000, 5000 points

**Metrics:** Node visits and build time

### Experiment 3: max_entries Impact
Evaluates effect of node capacity parameter:
- max_entries = 4, 8, 12, 16

**Metrics:** Node visits and tree height

---

## 🎯 Key Results

- **R*-tree consistently outperforms R-tree** in query efficiency
- **Forced reinsertion reduces node overlap**, leading to fewer node visits
- **Performance gain is more significant on clustered data**
- **Larger max_entries reduces tree height** but may increase per-node processing

See the final report for detailed analysis and visualizations.

---

## 🔧 Implementation Details

### R-tree Features
- Linear split algorithm
- Minimum area enlargement heuristic for insertion
- Range query with node visit tracking

### R*-tree Enhancements
- **Forced reinsertion**: Removes 30% of farthest entries before splitting
- **Optimized split axis**: Evaluates both x and y axes
- **Overlap minimization**: Reduces MBR overlap for faster queries

### Data Generation
- `random_points()`: Uniform distribution in [0,1] × [0,1]
- `clustered_points()`: Gaussian clusters with σ=0.08

---

## 📚 References

Beckmann, N., Kriegel, H. P., Schneider, R., & Seeger, B. (1990). The R*-tree: An efficient and robust access method for points and rectangles. *ACM SIGMOD Record, 19*(2), 322-331.

Guttman, A. (1984). R-trees: A dynamic index structure for spatial searching. *ACM SIGMOD Record, 14*(2), 47-57.

---

## 📝 License

This project is for educational purposes as part of CPSC 4660 coursework.