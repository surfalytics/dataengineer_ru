"""Глава 1: алгоритм выполнения графа задач (без Airflow, чистый Python).
Граф из книги про зонты: две независимые ветки, join, train, deploy."""

# task -> список upstream-задач, от которых она зависит
graph = {
    "fetch_weather": [],
    "clean_weather": ["fetch_weather"],
    "fetch_sales": [],
    "clean_sales": ["fetch_sales"],
    "join_datasets": ["clean_weather", "clean_sales"],
    "train_model": ["join_datasets"],
    "deploy_model": ["train_model"],
}

done = set()
loop = 0
while len(done) < len(graph):
    loop += 1
    # шаг 1: открытые задачи, у которых все upstream готовы
    ready = sorted(t for t, up in graph.items() if t not in done and all(u in done for u in up))
    print(f"loop {loop}: в очередь идут {ready}")
    # шаг 2: выполняем очередь и отмечаем задачи готовыми
    done.update(ready)
print("все tasks выполнены")
