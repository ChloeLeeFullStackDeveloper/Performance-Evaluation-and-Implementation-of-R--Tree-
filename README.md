# Performance Evaluation and Implementation of R*-Tree (vs R-Tree)

This project implements **R-tree** and **R\*-tree** from scratch in Python and evaluates
their performance under three conditions:

1. Different data distributions (uniform vs clustered)
2. Scalability with dataset size (N = 500 → 5000)
3. Effect of varying `max_entries` (node capacity)

All experiment results (plots + raw CSV data) are automatically generated when running the main script.

---

## 🚀 How to Run

### 1. (Optional) Create & activate a virtual environment
```bash
source .venv/bin/activate        # macOS / Linux
.\.venv\Scripts\activate         # Windows   
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run all experiments (generates 3 CSV + 3 PNG plots)
```bash
python experiment.py --all
```
Or, run individually:
```bash
python experiment.py --distribution     # uniform vs clustered
python experiment.py --scalability      # N = {500,1000,2000,5000}
python experiment.py --max-entries      # max_entries = {4,8,12,16}
```

## After execution, the generated files appear in:
```
/results
  ├── exp1_distribution.csv
  ├── exp1_distribution.png
  ├── exp2_scalability.csv
  ├── exp2_scalability.png
  ├── exp3_max_entries.csv
  └── exp3_max_entries.png
```

## 📂 Project Structure
```
.
├── experiment.py              # runs experiments, generates plots + CSV
├── rstar_tree.py              # R-tree & R*-tree implementation
├── results/                   # generated experiment outputs
├── README.md
└── requirements.txt
Experiment functions:
run_experiment_distribution()   # uniform vs clustered datasets
run_experiment_scalability()    # dataset grows from 500 to 5000
run_experiment_max_entries()    # compare different max_entries values
```