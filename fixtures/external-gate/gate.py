"""One newly authored harmless gate; no imports, filesystem or child processes."""
def check(raw, parsed, json, time):
    value = json.loads(raw)
    if (type(value) is not dict or set(value) != {"values", "expected", "block_seconds"}
            or type(value["values"]) is not list or not 1 <= len(value["values"]) <= 8
            or any(type(n) is not int or not 0 <= n <= 9 for n in value["values"])
            or type(value["expected"]) is not int or not 0 <= value["expected"] <= 100
            or type(value["block_seconds"]) is not int or value["block_seconds"] not in (0, 10)):
        raise ValueError("invalid-invented-input")
    parsed()
    if value["block_seconds"]:
        time.sleep(value["block_seconds"])
    total = sum(value["values"])
    return (0 if total == value["expected"] else 7), ["parse", "sum", "compare"]
