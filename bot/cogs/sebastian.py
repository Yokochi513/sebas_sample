import discord
from discord import app_commands
from discord.ext import commands

from bot.gemini import gemini_generate_grounded
from bot.persona import sebastian_persona


class Sebastian(commands.Cog):
    """一般向け：セバスチャンのスラッシュコマンド（Gemini）。"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="セバスチャンに何でも尋ねます")
    @app_commands.describe(question="ご質問")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()

        embed = None

        # 通常の質問 → Google検索グラウンディングで時事・固有の事実にも対応
        prompt = (
            f"ご主人様からのご質問：{question}\n\n"
            "必要に応じて検索結果を踏まえ、事実は正確に、執事として簡潔にお答えしてください。"
        )
        reply, sources = await gemini_generate_grounded(
            prompt=prompt,
            system_instruction=sebastian_persona(),
        )
        if reply and sources:
            # 参考資料は埋め込みで表示する。
            # 長いグラウンディングURLはそのまま出さず、タイトルに埋め込むマスクリンクで簡潔に。
            lines = []
            for i, (title, uri) in enumerate(sources[:3], 1):
                label = title or uri
                lines.append(f"{i}. [{label}]({uri})")
            embed = discord.Embed(
                title="参考にした資料",
                description="\n".join(lines),
            )

        if reply is None:
            reply = "申し訳ございません、ただいま考えがまとまらないようでございます。"
        await interaction.followup.send(reply, embed=embed)


async def setup(bot):
    await bot.add_cog(Sebastian(bot))
