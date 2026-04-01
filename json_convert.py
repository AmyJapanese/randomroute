import json
from pathlib import Path

INPUT_FILE = Path("input.txt")
OUTPUT_FILE = Path("items.json")


def parse_line(line, line_num):
    parts = line.strip().split("|")

    if len(parts) != 3:
        raise ValueError(f"{line_num}行目: フォーマットが不正")

    name = parts[0].strip()

    tags = [t.strip() for t in parts[1].split(",") if t.strip()]

    try:
        weight = float(parts[2])
    except ValueError:
        raise ValueError(f"{line_num}行目: weightは数字で指定してね")

    return {
        "name": name,
        "tags": tags,
        "weight": weight
    }


def main():
    if not INPUT_FILE.exists():
        print("input.txtが見つからない")
        return

    items = []
    errors = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if not line.strip():
                continue  # 空行スキップ

            try:
                item = parse_line(line, i)
                items.append(item)
            except ValueError as e:
                errors.append(str(e))

    if errors:
        print("⚠ エラーがありました:")
        for e in errors:
            print("-", e)
        print("\n修正してからもう一度実行してね")
        return

    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(items)}件を items.json に書き出しました")


if __name__ == "__main__":
    main()