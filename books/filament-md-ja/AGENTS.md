# Filament.md 和訳 (Physically Based Rendering in Filament)

元ドキュメント: `F:\Downloads\filament\docs\Filament.md.html`
（Filament 公式の PBR 理論解説）

## 方針

- 原文を分かりやすい日本語に翻訳し、Zenn Book (`books/filament-md-ja`) として分割する
- 数式・変数名・関数名・パラメータ名・文献キー (`#Burley12` など) は英語のまま
- コードブロックの内容は翻訳しない（コメントは日本語化してよい）
- 章の並びは `config.yaml` の `chapters` で管理する

## 各章の形式

```markdown
---
title: "章タイトル"
---

本文...

---

原文: https://google.github.io/filament/Filament.html
```

## 画像

- 画像ファイル: `images/filament-md-ja/`
- 記事からの参照: `![](/images/filament-md-ja/foo.png)`
- 図キャプションは日本語化する（例: `図: ...`）

## 数式（Zenn / KaTeX）

- Filament 原文の `\newcommand{NoL}{...}` は **使わない**（KaTeX では `\newcommand{\NoL}{...}` が必要で、かつ `\newcommand` は数式ブロック内スコープのみ）
- カスタムマクロ（`\NoL`, `\fDiffuse`, `\aa` など）は展開済みの形で書く
  - 例: `\NoL` → `n \cdot l`、`\fNormal` → `f_{0}`、`\aa` → `\alpha^2`
- `\begin{equation}...\end{equation}` / `\label` / `\ref` は使わず、`$$ ... $$` にする
- 修正スクリプト: `_fix_katex.py`

## Markdeep → Zenn 変換メモ

- `!!! Note: title` → `:::message` ブロック
- `~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~` コードフェンス → ` ```glsl ` など
- `[Listing [id]: caption]` → `*リスト: caption*`
- `[Table [id]: caption]` → テーブル直後に `*表: caption*`
- 画像パス `images/xxx` → `/images/filament-md-ja/xxx`
- 章内リンクは `./chapter-slug` 形式
- KaTeX の `\newcommand` は数式を使う章の先頭に配置する
