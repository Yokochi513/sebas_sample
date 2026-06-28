# セバスチャン（/ask 抽出版）

`C:\workspace\git\sebastian` の Discord ボット「セバスチャン」から、スラッシュコマンド `/ask` の機能だけを抜き出した最小構成です。伝言（取り次ぎ）機能、定時投稿、占い・献立・学習問題などのコマンドは含みません。

## /ask の挙動

- 通常の質問 → Google 検索グラウンディング付きで Gemini が回答し、参考資料を埋め込みで添える。
- 質問に台風系キーワード（`台風` / `たいふう` / `暴風`）が含まれる → 先に気象庁の一次情報を取得し、それだけを根拠に整形させる（数値を創作させない）。
- 送信者のユーザーIDに応じて呼称（二人称）を `setting.json` で切り替える。

## セットアップ

```bash
pip install -r requirements.txt
python main.py
```

## 設定

リポジトリ直下に `.env` を作成してください（git 管理外）。

```
TOKEN=Discordボットのトークン
GUILD_ID=スラッシュコマンドを同期するギルドID
GEMINI_API_KEY=GeminiのAPIキー
GEMINI_MODEL=gemini-3.1-flash-lite   # 任意
STUDY_GRADE=                          # 任意。呼称判定にのみ使用
```

呼称（二人称）の対応は `setting.json` で指定します。表に無いIDには `default` が使われます。

## 構成

```
main.py                  起点。Cogを読み込み、スラッシュコマンドをギルドへ同期
bot/config.py            .env / setting.json の読み込みと定数
bot/gemini.py            Gemini REST 呼び出し（通常 / 検索グラウンディング）
bot/persona.py           執事ペルソナ・呼称・防災時の安全ルール
bot/cogs/sebastian.py    /ask スラッシュコマンド
bot/services/typhoon.py  気象庁の台風一次情報の取得
```
