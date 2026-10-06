import os
import zipfile
import json
import random

def generate_math_payload():
    print("Generating Math Benchmark Dataset (10 Matrix Partitions)...")
    os.makedirs("test_data_math", exist_ok=True)
    
    files = []
    for i in range(10):
        filename = f"test_data_math/matrix_chunk_{i}.json"
        # Generate 50x50 numerical matrices for distributed matrix multiplication
        data = {
            "chunk_index": i,
            "operation": "distributed_matrix_multiplication",
            "dimension": 50,
            "matrix_A_row_slice": [[random.uniform(1.0, 100.0) for _ in range(50)] for _ in range(5)],
            "matrix_B": [[random.uniform(1.0, 100.0) for _ in range(50)] for _ in range(50)],
            "monte_carlo_samples": 500000
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        files.append(filename)
        print(f"Created {filename}")
        
    print("Packaging into math_payload.zip...")
    with zipfile.ZipFile("math_payload.zip", "w") as zf:
        for f in files:
            zf.write(f, arcname=os.path.basename(f))
            
    print("Done! You can now upload math_payload.zip via the DaeMon Dashboard.")

if __name__ == "__main__":
    generate_math_payload()
