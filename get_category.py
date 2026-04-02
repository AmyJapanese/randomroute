import os
import time
import traceback
from typing import List, Dict, Any

import requests

API_URL = "https://waukeepedia.miraheze.org/w/api.php"
OUTPUT_FILE = "input.txt"

HEADERS = {
    "User-Agent": "RandomRouteCategoryFetcher/1.0 (User:SeijoAmi on waukeepedia.miraheze.org)",
    "Accept": "application/json",
}

SLEEP_SECONDS = 2.0
FORBIDDEN_SLEEP_SECONDS = 30
MAX_RETRIES = 3
WRITE_FSYNC_EVERY = 10
APLIMIT = 10
CLLIMIT = "max"

EXCLUDED_CATEGORY_PREFIXES = (
    "Pages with",
    "Articles with",
)

EXCLUDED_CATEGORY_NAMES = {
    "設定所属識別済み",
    "七本柱識別済み",
    "3000バイト超えの記事",
    "曖昧さ回避",
    "メタ",
    "Walkerpediaのメタ"
}


def debug(msg: str) -> None:
    print(msg, flush=True)


def strip_category_prefix(category_title: str) -> str:
    if category_title.startswith("Category:"):
        return category_title[len("Category:"):]
    return category_title


def should_skip_category(category_name: str) -> bool:
    if category_name in EXCLUDED_CATEGORY_NAMES:
        return True
    return any(category_name.startswith(prefix) for prefix in EXCLUDED_CATEGORY_PREFIXES)


def calc_weight(categories: List[str]) -> int:
    """
    重み = カテゴリ文字列のUTF-8バイト長
    カテゴリなしなら1
    """
    if not categories:
        return 1
    category_text = ",".join(categories)
    return max(1, len(category_text.encode("utf-8")))

def normalize_category(category_title: str) -> str:
    return category_title.removeprefix("カテゴリ:").strip()

def get_with_retry(session: requests.Session, params: Dict[str, Any]) -> Dict[str, Any]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            debug(f"[API] attempt={attempt} params={params}")
            response = session.get(API_URL, params=params, timeout=(10, 30))
            debug(f"[API] status={response.status_code}")

            if response.status_code == 403:
                debug("[API] 403 Forbidden -> 待機して再試行")
                time.sleep(FORBIDDEN_SLEEP_SECONDS)
                continue

            response.raise_for_status()
            return response.json()

        except Exception as e:
            debug(f"[API] 例外: {e!r}")
            debug(traceback.format_exc())
            time.sleep(3)

    raise RuntimeError("APIリトライ回数を超えました")


def iter_all_page_titles(session: requests.Session):
    """
    通常記事（名前空間0）かつ非リダイレクトのタイトルを順に返す
    """
    debug("[iter_all_page_titles] 開始")

    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apnamespace": "0",
        "aplimit": str(APLIMIT),
        "apfilterredir": "nonredirects",
    }

    page_count = 0

    while True:
        page_count += 1
        debug(f"[iter_all_page_titles] APIページ {page_count}")

        data = get_with_retry(session, params)
        allpages = data.get("query", {}).get("allpages", [])

        debug(f"[iter_all_page_titles] 今回取得件数={len(allpages)}")

        for page in allpages:
            title = page.get("title", "").strip()
            if title:
                debug(f"[iter_all_page_titles] title={title}")
                yield title

        cont = data.get("continue")
        if not cont:
            debug("[iter_all_page_titles] 全件取得完了")
            break

        params.update(cont)
        time.sleep(SLEEP_SECONDS)


def fetch_categories_for_title(session: requests.Session, title: str) -> List[str]:
    """
    1ページ分のカテゴリ取得
    """
    debug(f"[fetch_categories_for_title] 開始 title={title}")

    params = {
        "action": "query",
        "format": "json",
        "prop": "categories",
        "titles": title,
        "cllimit": CLLIMIT,
    }

    categories: List[str] = []

    while True:
        data = get_with_retry(session, params)
        pages = data.get("query", {}).get("pages", {})

        debug(f"[fetch_categories_for_title] pages keys={list(pages.keys())}")

        for page in pages.values():
            returned_title = page.get("title", "").strip()
            debug(f"[fetch_categories_for_title] returned_title={returned_title}")

            raw_categories = page.get("categories", [])
            debug(f"[fetch_categories_for_title] raw_categories={raw_categories}")

            for cat in raw_categories:
                cat_title = cat.get("title", "")
                cat_name = normalize_category(cat_title)
                if not cat_name:
                    continue
                if should_skip_category(cat_name):
                    continue
                categories.append(cat_name)

        cont = data.get("continue")
        if not cont:
            break

        params.update(cont)
        time.sleep(SLEEP_SECONDS)

    debug(f"[fetch_categories_for_title] categories={categories}")
    return categories


def main() -> None:
    debug("[main] 開始")

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        written_count = 0

        with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
            for title in iter_all_page_titles(session):
                try:
                    categories = fetch_categories_for_title(session, title)
                    if not categories:
                        debug(f"[main] カテゴリなしなのでスキップ: {title}")
                        continue
                    category_text = ",".join(categories)
                    weight = calc_weight(categories)

                    line = f"{title}|{category_text}|{weight}"
                    f.write(line + "\n")
                    f.flush()

                    written_count += 1
                    if written_count % WRITE_FSYNC_EVERY == 0:
                        os.fsync(f.fileno())

                    debug(f"[main] 書き込み済み ({written_count}): {line}")

                except Exception as e:
                    debug(f"[main] ページ処理失敗 title={title} error={e!r}")
                    debug(traceback.format_exc())

                time.sleep(SLEEP_SECONDS)

            f.flush()
            os.fsync(f.fileno())

        debug("[main] 正常終了")

    except Exception as e:
        debug("[main] 例外で停止")
        debug(repr(e))
        debug(traceback.format_exc())


if __name__ == "__main__":
    main()