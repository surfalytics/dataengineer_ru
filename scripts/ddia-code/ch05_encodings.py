#!/usr/bin/env python3
"""DDIA2, глава 5: одна запись в четырёх форматах - JSON, MessagePack, Protocol Buffers, Avro.
Кодировщики написаны вручную, только стандартная библиотека. Запуск: python3 -I ch05_encodings.py"""
import json

record = {"userName": "Martin", "favoriteNumber": 1337, "interests": ["daydreaming", "hacking"]}


def varint(n):
    """Число без знака: по 7 бит в байте, старший бит = 'дальше есть ещё байты'."""
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def zigzag(n):
    """Avro: 0, -1, 1, -2, 2 ... -> 0, 1, 2, 3, 4, чтобы малые отрицательные числа тоже были короткими."""
    return (n << 1) ^ (n >> 63)


def msgpack(obj):
    """Минимальный MessagePack: только типы из нашей записи."""
    if isinstance(obj, dict):
        out = bytes([0x80 | len(obj)])
        for k, v in obj.items():
            out += msgpack(k) + msgpack(v)
        return out
    if isinstance(obj, list):
        return bytes([0x90 | len(obj)]) + b"".join(msgpack(x) for x in obj)
    if isinstance(obj, str):
        data = obj.encode()
        return bytes([0xA0 | len(data)]) + data
    if isinstance(obj, int) and obj < 65536:
        return bytes([0xCD]) + obj.to_bytes(2, "big")
    raise TypeError(obj)


def protobuf(rec):
    """proto3: user_name = 1, favorite_number = 2, repeated interests = 3."""
    def field(tag, wire_type):
        return varint(tag << 3 | wire_type)

    def text(tag, s):
        data = s.encode()
        return field(tag, 2) + varint(len(data)) + data

    out = text(1, rec["userName"])
    out += field(2, 0) + varint(rec["favoriteNumber"])
    for s in rec["interests"]:
        out += text(3, s)
    return out


def avro(rec):
    """Только значения подряд в порядке схемы: ни имён, ни тегов, ни типов."""
    def text(s):
        data = s.encode()
        return varint(zigzag(len(data))) + data

    out = text(rec["userName"])
    out += varint(zigzag(1)) + varint(zigzag(rec["favoriteNumber"]))  # union {null, long}: ветка 1
    out += varint(zigzag(len(rec["interests"])))  # блок массива из 2 элементов
    for s in rec["interests"]:
        out += text(s)
    out += b"\x00"  # конец массива
    return out


encoded = {
    "JSON": json.dumps(record, separators=(",", ":")).encode(),
    "MessagePack": msgpack(record),
    "Protocol Buffers": protobuf(record),
    "Avro": avro(record),
}
print(f"{'формат':17} байтов  первые байты")
for name, data in encoded.items():
    print(f"{name:17} {len(data):6}  {data[:10].hex(' ')} ...")

print()
print("1337 как varint:", varint(1337).hex(" "))
for n in (63, 64, 8191, 8192):
    print(f"Avro long {n:5} -> байтов: {len(varint(zigzag(n)))}")

print()
post_id = 2**53 + 1  # такой ID не помещается в double без потерь
as_js = json.loads(json.dumps({"id": post_id}), parse_int=float)  # так читает JavaScript
print("ID в JSON:", post_id, "| прочитан как double:", int(as_js["id"]))
