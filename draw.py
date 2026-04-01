import json
import random
import argparse
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
ITEMS_FILE = DATA_DIR / "items.json"
HISTORY_FILE = DATA_DIR / "history.json"


def load_items():
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def filter_items(items, include_tags, exclude_tags):
    result = []
    for item in items:
        tags = item.get("tags", [])

        if include_tags and not any(tag in tags for tag in include_tags):
            continue

        if exclude_tags and any(tag in tags for tag in exclude_tags):
            continue

        result.append(item)

    return result


def weighted_draw(items):
    weights = [item["weight"] for item in items]
    return random.choices(items, weights=weights, k=1)[0]


def ask_status():
    print("\nどうする？")
    print("[a] 採用 / [h] 保留 / [s] スキップ / [n] 記録しない")

    while True:
        choice = input("> ").strip().lower()
        if choice in ["a", "h", "s", "n"]:
            return choice
        print("無効な入力。a/h/s/n のどれかを入力してね")


def main():
    parser = argparse.ArgumentParser(description="Walkerpedia 抽選CLI")
    parser.add_argument("--tag", nargs="*", help="含めるタグ")
    parser.add_argument("--exclude", nargs="*", help="除外タグ")
    parser.add_argument("--reroll", action="store_true")

    args = parser.parse_args()

    items = load_items()
    history = load_history()

    filtered = filter_items(items, args.tag, args.exclude)

    # reroll
    if args.reroll and history:
        last = history[-1]["result"]
        filtered = [item for item in filtered if item["name"] != last]

    if not filtered:
        print("候補がありません")
        return

    result_item = weighted_draw(filtered)

    # 演出
    print("抽選中...")
    print("・・・\n")
    print(f"🎯 {result_item['name']}")
    print(f"タグ: {', '.join(result_item.get('tags', []))}")

    # 選択
    choice = ask_status()

    status_map = {
        "a": "accepted",
        "h": "hold",
        "s": "skipped"
    }

    # n（記録しない）は保存しない
    if choice == "n":
        print("記録しませんでした")
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "result": result_item["name"],
        "tags": result_item.get("tags", []),
        "status": status_map[choice]
    }

    history.append(entry)
    save_history(history)

    print(f"記録しました: {entry['status']}")


if __name__ == "__main__":
    main()