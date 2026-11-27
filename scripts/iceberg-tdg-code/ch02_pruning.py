files = [("a.parquet", 1, 9), ("b.parquet", 10, 19), ("c.parquet", 20, 29)]
low, high = 12, 22
for name, minimum, maximum in files:
    if minimum <= high and maximum >= low:
        print(name)
