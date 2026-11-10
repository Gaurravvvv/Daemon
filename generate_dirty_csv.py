import csv
import random
import time

def generate_dirty_csv(filename: str = "dirty_benchmark_sample.csv", num_rows: int = 50000):
    print(f"Generating realistic dirty CSV dataset with {num_rows} rows -> {filename}...")
    start_time = time.time()

    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "Alex", "Fatima", "Chen", "Aarav", "Elena"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Patel", "Kumar", "Wong", "Ivanov"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "enterprise.org", "research.edu"]
    statuses = ["Active", "Pending", "Suspended", "VIP", "Review"]
    sentinel_nulls = ["N/A", "NA", "null", "None", "?", "-", "--", ""]

    headers = ["Customer ID (#)", " Full Name ", "Email Address", "Phone Number", "Signup Date", "Total Purchase ($)", "Account Status"]

    rows = []
    
    # Generate base unique pool
    for i in range(num_rows):
        cid = f"CUST-{100000 + i}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"

        # 1. Email (sometimes null, sometimes dirty)
        if random.random() < 0.12:
            email = random.choice(sentinel_nulls)
        else:
            email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 99)}@{random.choice(domains)}"

        # 2. Phone (various unformatted styles or null)
        if random.random() < 0.15:
            phone = random.choice(sentinel_nulls)
        else:
            p1 = random.randint(200, 999)
            p2 = random.randint(100, 999)
            p3 = random.randint(1000, 9999)
            style = random.choice(["hyphen", "parens", "plus", "plain"])
            if style == "hyphen":
                phone = f"{p1}-{p2}-{p3}"
            elif style == "parens":
                phone = f"({p1}) {p2}-{p3}"
            elif style == "plus":
                phone = f"+1-{p1}-{p2}-{p3}"
            else:
                phone = f"{p1}{p2}{p3}"

        # 3. Date (inconsistent formats or null)
        if random.random() < 0.08:
            date_str = random.choice(sentinel_nulls)
        else:
            y = random.randint(2020, 2026)
            m = random.randint(1, 12)
            d = random.randint(1, 28)
            dstyle = random.choice(["iso", "slash_dmy", "slash_ymd", "hyphen_dmy"])
            if dstyle == "iso":
                date_str = f"{y}-{m:02d}-{d:02d}"
            elif dstyle == "slash_dmy":
                date_str = f"{d:02d}/{m:02d}/{y}"
            elif dstyle == "slash_ymd":
                date_str = f"{y}/{m:02d}/{d:02d}"
            else:
                date_str = f"{d:02d}-{m:02d}-{y}"

        # 4. Purchase ($ formatting, commas, nulls)
        if random.random() < 0.10:
            spend = random.choice(sentinel_nulls)
        else:
            val = round(random.uniform(10.0, 5000.0), 2)
            spend = f"${val:,.2f}" if random.random() < 0.5 else str(val)

        # 5. Status
        if random.random() < 0.05:
            status = random.choice(sentinel_nulls)
        else:
            status = f"  {random.choice(statuses)}  "  # intentional trailing whitespace

        rows.append([cid, name, email, phone, date_str, spend, status])

    # Inject 10% exact duplicate rows
    duplicate_count = int(num_rows * 0.10)
    for _ in range(duplicate_count):
        dup_row = list(random.choice(rows))
        rows.append(dup_row)

    random.shuffle(rows)

    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    elapsed = round(time.time() - start_time, 2)
    print(f"Generated {len(rows)} total rows ({duplicate_count} injected duplicates) in {elapsed}s.")
    print(f"File saved to: {filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate realistic dirty CSV benchmarks for DaeMon")
    parser.add_argument("--rows", type=int, default=50000, help="Number of unique base rows to generate")
    parser.add_argument("--output", type=str, default="dirty_benchmark_sample.csv", help="Output CSV file path")
    args = parser.parse_args()

    generate_dirty_csv(args.output, num_rows=args.rows)
