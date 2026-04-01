# CLIで動くルーレット

Pythonで動くシンプルな抽選CLIツールです。
キャラや場所などをランダムに選び、創作のネタ出しや挿絵決めに使えます。

---

## 🧩 特徴

* Python標準ライブラリのみで動作（追加インストール不要）
* タグ・重み付き抽選に対応
* 抽選結果を履歴として保存
* 採用 / 保留 / スキップなどのステータス管理が可能

---

## 🚀 使い方

```bash
python draw.py
```

オプション例：

```bash
python draw.py --tag character
python draw.py --exclude historical
python draw.py --reroll
```

---

## ⚙️ データ構成

### `data/items.json`

抽選対象のデータを記述します。

```json
[
  {
    "name": "エミリー・ウォーカー",
    "tags": ["character", "main"],
    "weight": 5
  }
]
```

---

### `data/history.json`

抽選履歴が保存されます。

```json
[
  {
    "timestamp": "2026-04-01T12:00:00",
    "result": "エミリー・ウォーカー",
    "tags": ["character", "main"],
    "status": "accepted"
  }
]
```

ステータス：

* `accepted`：採用
* `hold`：保留
* `skipped`：スキップ

※「記録しない」を選んだ場合は保存されません

---

## 📝 JSON生成ツール

### `json_convert.py`

`input.txt` を `items.json` に変換します。

#### フォーマット：

```
name|tag1,tag2|weight
```

#### 例：

```
エミリー・ウォーカー|character,main|5
シカゴ|location,city|3
リンカーン|historical|0.5
```

#### 実行：

```bash
python json_convert.py
```

* フォーマットが間違っているとエラーになります
* `input.txt` は同じフォルダに配置してください
* 出力も同じパスに生成されます

---

## 📁 ディレクトリ構成

```
.
├── draw.py
├── json_convert.py
├── input.txt
└── data/
    ├── items.json
    └── history.json
```

---

## ⚠️ 注意

* `items.json` と `history.json` は `.gitignore` 推奨です
  （各自の環境で管理してください）
* `data` フォルダは事前に作成するか、自動生成されます

---

## 💡 補足

このツールは「全部入りガチャ」的な使い方もできますが、
タグや重みを調整するとより快適に使えます。

---

## 🎲 コンセプト

> 何が出るかわからない。
> 出たものから創作する。

そんな「霧の中から引き当てる」感覚を楽しむためのツールです。
