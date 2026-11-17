# muse-widgets

[Muse](https://muse.ai) のチャット内ウィジェットのための、部品カタログ、HTML雛形、判断を担うエージェント Skill、契約の検査ツールをまとめたリポジトリです。

**デモ: [hyd3-14.github.io/muse-widgets](https://hyd3-14.github.io/muse-widgets/)** — 全15部品をブラウザでそのまま触れます。

English: [README.md](README.md)

> 非公式のプロジェクトです。Muse は Meta の製品です。ここに書いたウィジェットの契約は、公開された SDK ではなく、実際に観測できる挙動に基づくため、変わる可能性があります。

## なぜ作ったか

Muse はチャットの中で、スライダーやチェックリストや計算機のような対話できる HTML ウィジェットを表示できます。うまく使えば文章より伝わります。数量を動かして合計が追随する、チェックした残り項目をエージェントが読み戻せる、条件を変えると推奨が動く比較表、といった形です。

ただし、公開されたカタログがありません。エージェントは毎回その場で組み立て、状態の扱いは会話ごとに再発見され、同じ失敗（状態をブラウザの保存領域に入れる、明るい画面前提の配色、form 要素の使用）が繰り返されます。このリポジトリは、汎用の生成 UI ではなく Muse に特化した、そのカタログです。

## 中身

| 部分 | パス | 役割 |
| --- | --- | --- |
| エージェント Skill | `skills/chat-intelligent-ui/` | ウィジェットを出すかどうか、どの部品を使うか、作るときの規則を判断する |
| 部品カタログ | `catalog/` | 15部品の仕様と状態の形、デザイントークン（`tokens.css`） |
| 雛形 | `templates/` | 部品ごとに1ファイル、そのまま使える HTML 断片 |
| 完成例 | `examples/` | 雛形から作った完成品 |
| 検査ツール | `tools/validate-widget.py and tools/layout_check.py` | 断片が契約に合うか検査する（Python 標準ライブラリのみ） |
| 状態ブリッジの文書 | `docs/state-bridge.md` | `window.hatchWidget` の状態、テーマ、対話の仕組み |
| デモ | `docs/index.html` | `tools/build-demo.py` が雛形から生成する |

## 契約の要点

- ウィジェットは完全な文書ではなく HTML の断片で、上限は 1 MB です。
- 状態は `window.hatchWidget` だけに置きます。`getState(defaults)` で初期化し、変更のたびに `setState(nextState)` で丸ごと差し替え、`hatch-widget-state` イベントで再描画します。
- `localStorage` と `<form>` は使いません。配色は `--hatch-widget-*` のテーマ変数で決め、明暗どちらのテーマでも読めるようにします。

全文は [docs/state-bridge.md](docs/state-bridge.md) にあります。

## ライセンス

MIT
