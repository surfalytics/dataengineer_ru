"""Размер KV-кэша: полные головы (MHA), группы (GQA) и один набор (MQA)."""
layers, q_heads, d_head = 32, 32, 128
seq_len = 32_000
bytes_per_number = 2                                # fp16

print(f"Слоёв {layers}, голов query {q_heads}, размер головы {d_head}, контекст {seq_len} токенов")
for name, kv_heads in [("MHA", 32), ("GQA", 8), ("MQA", 1)]:
    # 2 = key и value; кэш хранит их для каждого слоя и каждого токена
    per_token = 2 * layers * kv_heads * d_head * bytes_per_number
    total_gib = per_token * seq_len / 2**30
    print(f"{name}: key/value голов {kv_heads:2d}, на токен {per_token / 1024:6.0f} КиБ,"
          f" весь кэш {total_gib:5.2f} ГиБ")
