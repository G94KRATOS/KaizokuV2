import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    """Commandes amusantes."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dice", help="Lance un dé à 6 faces")
    async def dice(self, ctx):
        await ctx.send(f"🎲 Résultat : {random.randint(1, 6)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
