"""
Test script to verify all submission requirements are met.
Run this before submitting your project.

Tests:
1. Code executes without errors
2. All expected output files are generated
3. CSV files contain valid data
4. PNG plots are created
"""

import os
import sys
import subprocess
from pathlib import Path


def test_requirements():
    """Check if required packages are installed."""
    print("=" * 60)
    print("TEST 1: Checking Dependencies")
    print("=" * 60)
    
    required = ['matplotlib', 'pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages: pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All dependencies are installed\n")
    return True


def test_code_imports():
    """Test if main code files can be imported."""
    print("=" * 60)
    print("TEST 2: Checking Code Imports")
    print("=" * 60)
    
    try:
        import rstar_tree
        print("✓ rstar_tree.py imports successfully")
        
        # Check for required classes
        if hasattr(rstar_tree, 'RTree'):
            print("✓ RTree class found")
        if hasattr(rstar_tree, 'RStarTree'):
            print("✓ RStarTree class found")
            
    except Exception as e:
        print(f"✗ Error importing rstar_tree.py: {e}")
        return False
    
    try:
        import experiment
        print("✓ experiment.py imports successfully")
    except Exception as e:
        print(f"✗ Error importing experiment.py: {e}")
        return False
    
    print("\n✓ All code files import successfully\n")
    return True


def test_experiment_execution():
    """Run experiments and check for output files."""
    print("=" * 60)
    print("TEST 3: Running Experiments")
    print("=" * 60)
    print("This may take a few minutes...\n")
    
    # Create results directory if it doesn't exist
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    try:
        # Run all experiments
        result = subprocess.run(
            ["python", "experiment.py", "--all"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"✗ experiment.py failed with error:")
            print(result.stderr)
            return False
        
        print("✓ experiment.py executed successfully\n")
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Experiment execution timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Error running experiments: {e}")
        return False


def test_output_files():
    """Check if all expected output files were generated."""
    print("=" * 60)
    print("TEST 4: Checking Output Files")
    print("=" * 60)
    
    results_dir = Path("results")
    
    expected_files = [
        "exp1_distribution.csv",
        "exp1_distribution.png",
        "exp2_scalability.csv",
        "exp2_scalability.png",
        "exp3_max_entries.csv",
        "exp3_max_entries.png"
    ]
    
    all_exist = True
    for filename in expected_files:
        filepath = results_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✓ {filename} exists ({size:,} bytes)")
        else:
            print(f"✗ {filename} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✓ All expected output files were generated\n")
    else:
        print("\n✗ Some output files are missing\n")
    
    return all_exist


def test_csv_data():
    """Validate CSV files contain data."""
    print("=" * 60)
    print("TEST 5: Validating CSV Data")
    print("=" * 60)
    
    import pandas as pd
    
    results_dir = Path("results")
    csv_files = [
        "exp1_distribution.csv",
        "exp2_scalability.csv",
        "exp3_max_entries.csv"
    ]
    
    all_valid = True
    for filename in csv_files:
        filepath = results_dir / filename
        try:
            df = pd.read_csv(filepath)
            rows = len(df)
            cols = len(df.columns)
            print(f"✓ {filename}: {rows} rows, {cols} columns")
            
            if rows == 0:
                print(f"  ⚠ Warning: CSV file is empty")
                all_valid = False
                
        except Exception as e:
            print(f"✗ Error reading {filename}: {e}")
            all_valid = False
    
    if all_valid:
        print("\n✓ All CSV files contain valid data\n")
    else:
        print("\n✗ Some CSV files have issues\n")
    
    return all_valid


def test_documentation():
    """Check for code documentation."""
    print("=" * 60)
    print("TEST 6: Checking Code Documentation")
    print("=" * 60)
    
    with open("rstar_tree.py", "r") as f:
        content = f.read()
    
    # Check for docstrings
    has_module_doc = '"""' in content[:500]
    has_class_docs = content.count('class ') <= content.count('"""')
    
    if has_module_doc:
        print("✓ Module-level docstring found")
    else:
        print("⚠ No module-level docstring found")
    
    # Check for comments
    comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
    print(f"✓ Found {len(comment_lines)} comment lines")
    
    if len(comment_lines) > 10:
        print("✓ Code appears well-commented")
    else:
        print("⚠ Code may need more comments")
    
    print()
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PROJECT SUBMISSION VERIFICATION")
    print("=" * 60 + "\n")
    
    tests = [
        ("Dependencies", test_requirements),
        ("Code Imports", test_code_imports),
        ("Experiment Execution", test_experiment_execution),
        ("Output Files", test_output_files),
        ("CSV Data", test_csv_data),
        ("Documentation", test_documentation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}\n")
            results[test_name] = False
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ PROJECT IS READY FOR SUBMISSION ✓✓✓")
        return 0
    else:
        print("\n✗✗✗ FIX ISSUES BEFORE SUBMITTING ✗✗✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())