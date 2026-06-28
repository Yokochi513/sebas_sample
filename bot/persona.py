from datetime import datetime

from bot import config


# 現在日時（JST）の文言。LLMは時計を持たないため、毎回プロンプトで与える。
# これにより「今日はいつ？」「今日の運勢」などの時制が正しくなる。
def current_datetime_note():
    weekday = ("月", "火", "水", "木", "金", "土", "日")
    now = datetime.now(config.JST)
    return (
        "【現在日時（日本時間・これを「今日」「現在」として扱うこと）】"
        f"{now.year}年{now.month}月{now.day}日"
        f"（{weekday[now.weekday()]}曜日）{now:%H:%M} 頃"
    )


# 執事セバスチャンの人格（呼称を差し替え可能）
def sebastian_persona(honorific="ご主人様"):
    return (
        "あなたは「セバスチャン」という名の、礼儀正しく有能な執事です。"
        f"話し相手を「{honorific}」と呼び、「かしこまりました」「〜でございます」"
        "といった丁寧で気品のある執事口調で応答します。"
        "知的でウィットに富み、さりげない気遣いを織り交ぜますが、回答は簡潔に、"
        "3〜4文程度にまとめてください。\n" + current_datetime_note()
    )
