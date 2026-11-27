snapshots = {
    1: ("orders-01.parquet", "orders-02.parquet"),
    2: ("orders-01.parquet", "orders-03.parquet"),
}
current = 2

for snapshot_id in (1, current):
    files = ", ".join(snapshots[snapshot_id])
    print(f"snapshot {snapshot_id}: {files}")
