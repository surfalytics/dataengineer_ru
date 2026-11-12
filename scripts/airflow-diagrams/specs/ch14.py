from lib import N, E, Z, T
D = {}

D["ch14-ingestion-dag"] = dict(items=[
    N("up", "Рецепты (JSON)\nв MinIO, по дням", 0, 0, "n"),
    N("pre", "preprocess_recipes\nchunks + UUID", 0, 150, "p"),
    N("col", "create_collection\nесли ещё нет", 0, 300, "p"),
    N("cmp", "compare_objects\ncreate / update / skip", 0, 450, "pu"),
    N("del", "delete_outdated_\nobjects", 0, 600, "y"),
    N("save", "save_in_vectordb\nWeaviate", 0, 750, "db"),
    T("Каждый task запускает\nDockerOperator с образом\nvectorflow", 330, 150),
    T("Файлы-посредники в MinIO:\npreprocessed.parquet,\ncompared.parquet", 330, 450),
    T("Повтор task безопасен:\nUUID зависит от текста", 330, 750),
], edges=[
    E("up", "pre"), E("pre", "col"), E("col", "cmp"),
    E("cmp", "del"), E("del", "save"),
])

D["ch14-rag-flow"] = dict(items=[
    N("q", "Вопрос\nпользователя", 0, 0, "n"),
    N("emb", "Embedding model\nвопрос в вектор", 300, 0, "pu"),
    N("vs", "Weaviate\nпоиск по cosine\nsimilarity", 600, 0, "db"),
    N("ans", "Ответ\nпо рецептам", 0, 200, "g"),
    N("llm", "LLM\nгенерирует ответ", 300, 200, "p"),
    N("pr", "Prompt template:\nвопрос + история +\nнайденные рецепты", 600, 200, "y"),
], edges=[
    E("q", "emb"), E("emb", "vs"), E("vs", "pr", "top-k"),
    E("pr", "llm"), E("llm", "ans"),
])
