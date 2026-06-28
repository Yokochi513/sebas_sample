# セバスチャン（/ask 抽出版）

Discord ボット「セバスチャン」から、スラッシュコマンド `/ask` の機能だけを抜き出した最小構成です。伝言（取り次ぎ）機能、定時投稿、占い・献立・学習問題などのコマンドは含みません。

## /ask の挙動

- 質問を Google 検索グラウンディング付きで Gemini に渡し、執事口調で回答する。
- 回答の根拠になった参考資料があれば、埋め込み（Embed）で最大3件添える。

## 構成

```
main.py                  起点。Cogを読み込み、スラッシュコマンドをギルドへ同期
bot/config.py            .env の読み込みと定数
bot/gemini.py            Gemini REST 呼び出し（通常 / 検索グラウンディング）
bot/persona.py           執事ペルソナと現在日時の注入
bot/cogs/sebastian.py    /ask スラッシュコマンド
```

## 設定（.env）

リポジトリ直下に `.env` を作成してください（git 管理外）。

```
TOKEN=Discordボットのトークン
GUILD_ID=スラッシュコマンドを同期するギルドID
GEMINI_API_KEY=GeminiのAPIキー
GEMINI_MODEL=gemini-3.1-flash-lite   # 任意（未指定ならこの値）
```

## ローカルでの起動

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

# Raspberry Pi での運用（systemd / systemctl）

Raspberry Pi 上で常駐させ、`systemctl` で起動・停止・自動起動を管理する手順です。
以下は実行ユーザーを `pi`、配置先を `/home/pi/sebas_sample` とした例です。
環境に合わせて読み替えてください（`whoami` でユーザー名を確認できます）。

## 1. 事前準備

```bash
sudo apt update
sudo apt install -y python3 python3-venv git
```

## 2. 配置と依存のインストール

```bash
# 任意の場所へ配置（git clone でも、ファイルをコピーでも可）
cd /home/pi
git clone <このリポジトリのURL> sebas_sample
cd sebas_sample

# 仮想環境を作って依存を入れる
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

## 3. .env の作成

```bash
nano /home/pi/sebas_sample/.env
```

```
TOKEN=Discordボットのトークン
GUILD_ID=スラッシュコマンドを同期するギルドID
GEMINI_API_KEY=GeminiのAPIキー
GEMINI_MODEL=gemini-3.1-flash-lite
```

トークンを含む秘密情報なので、パーミッションを絞っておくと安全です。

```bash
chmod 600 /home/pi/sebas_sample/.env
```

## 4. 動作確認（手動起動）

サービス登録の前に、手動で起動できることを確認します。

```bash
cd /home/pi/sebas_sample
.venv/bin/python main.py
# 「ログインしました: ...」「スラッシュコマンド同期: N件」が出ればOK。Ctrl+C で停止。
```

## 5. systemd ユニットの設置

リポジトリ同梱の `sebastian.service` をコピーして使います。ユーザー名・パスが
上記と異なる場合は、コピー後にファイルを編集してください。

```bash
sudo cp /home/pi/sebas_sample/sebastian.service /etc/systemd/system/sebastian.service
sudo nano /etc/systemd/system/sebastian.service   # User / WorkingDirectory / パスを環境に合わせる
```

ユニットの内容（`sebastian.service`）:

```ini
[Unit]
Description=Sebastian Discord Bot (/ask)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/sebas_sample
ExecStart=/home/pi/sebas_sample/.venv/bin/python /home/pi/sebas_sample/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

ポイント:
- `After/Wants=network-online.target` … 起動時にネットワーク確立を待つ。
- `Restart=always` / `RestartSec=10` … クラッシュや通信断で落ちても10秒後に自動再起動。
- `.env` は `WorkingDirectory` 直下に置けば自動で読み込まれます（コード側で `load_dotenv()`）。

## 6. 有効化と起動

```bash
sudo systemctl daemon-reload          # ユニット定義を読み込み
sudo systemctl enable sebastian       # 電源投入時の自動起動を有効化
sudo systemctl start sebastian        # 今すぐ起動
sudo systemctl status sebastian       # 稼働状態を確認（Ctrl+C で抜ける）
```

`enable` と `start` は `sudo systemctl enable --now sebastian` でまとめて実行できます。

## 7. 日常運用コマンド

```bash
sudo systemctl status sebastian       # 状態確認
sudo systemctl restart sebastian      # 再起動（コード/.env を更新したとき）
sudo systemctl stop sebastian         # 停止
sudo systemctl disable sebastian      # 自動起動を無効化
```

## 8. ログの確認

標準出力（`print`）は journald に記録されます。

```bash
journalctl -u sebastian -f            # リアルタイムで追う
journalctl -u sebastian -n 100        # 直近100行
journalctl -u sebastian --since "1 hour ago"
```

## 9. 更新の反映

コードや `.env` を更新したら、再起動で反映します。依存（`requirements.txt`）を
変更したときは先に再インストールしてください。

```bash
cd /home/pi/sebas_sample
git pull                                       # 更新を取得（git運用の場合）
.venv/bin/pip install -r requirements.txt      # 依存が変わったときのみ
sudo systemctl restart sebastian
```

## トラブルシューティング

- **起動直後に落ちて再起動を繰り返す**: `journalctl -u sebastian -n 50` でエラーを確認。
  多くは `.env` の不足・誤り（`TOKEN` / `GUILD_ID` / `GEMINI_API_KEY`）か、依存未インストール。
- **`status` が `active (running)` なのにコマンドが出てこない**: `GUILD_ID` が対象サーバーと一致しているか確認。スラッシュコマンドは指定ギルドへ同期されます。
- **`ModuleNotFoundError`**: `ExecStart` が venv の Python（`.venv/bin/python`）を指しているか、依存を入れた venv と一致しているか確認。
```
