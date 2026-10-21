import os
import zipfile
import json
import hashlib
import random
import string

def generate_crypto_payload():
    print("Generating Cryptography Benchmark Dataset (10 Keyspace Batches)...")
    os.makedirs("test_data_crypto", exist_ok=True)
    
    files = []
    for i in range(10):
        filename = f"test_data_crypto/crypto_batch_{i}.json"
        
        # Generate target hashes and keyspace slices
        target_keys = ["".join(random.choices(string.ascii_lowercase + string.digits, k=4)) for _ in range(5)]
        target_sha256 = [hashlib.sha256(k.encode()).hexdigest() for k in target_keys]
        
        data = {
            "chunk_index": i,
            "algorithm": "SHA-256",
            "keyspace_range": {
                "start": i * 100000,
                "end": (i + 1) * 100000 - 1
            },
            "target_hashes": target_sha256,
            "difficulty_prefix": "0000"
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        files.append(filename)
        print(f"Created {filename}")
        
    print("Packaging into crypto_payload.zip...")
    with zipfile.ZipFile("crypto_payload.zip", "w") as zf:
        for f in files:
            zf.write(f, arcname=os.path.basename(f))
            
    print("Done! You can now upload crypto_payload.zip via the DaeMon Dashboard.")

if __name__ == "__main__":
    generate_crypto_payload()
