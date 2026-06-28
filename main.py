import discord
from discord.ext import commands

from bot import config

# 読み込むCog（拡張）一覧
INITIAL_EXTENSIONS = [
    "bot.cogs.sebastian",
]


class SebastianBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Cogをロード
        for ext in INITIAL_EXTENSIONS:
            await self.load_extension(ext)

        # スラッシュコマンドをこのギルドへ即時同期
        try:
            guild_obj = discord.Object(id=config.GUILD_ID)
            self.tree.copy_global_to(guild=guild_obj)
            synced = await self.tree.sync(guild=guild_obj)
            print(f"スラッシュコマンド同期: {len(synced)}件")
        except Exception as e:
            print(f"スラッシュコマンド同期エラー: {e}")

    async def on_ready(self):
        print(f"ログインしました: {self.user}")


def main():
    bot = SebastianBot()
    bot.run(config.TOKEN)


if __name__ == "__main__":
    main()
