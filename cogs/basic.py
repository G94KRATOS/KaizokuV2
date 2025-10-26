from discord.ext import commands

class Basic(commands.Cog, name="Basic"):
    """Commandes de base du bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Dit bonjour au bot.")
    async def hello(self, ctx):
        await ctx.send(f"👋 Salut {ctx.author.mention} !")

    @commands.command(help="Teste si le bot est en ligne.")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong ! Latence : {round(self.bot.latency*1000)}ms")

async def setup(bot):
    await bot.add_cog(Basic(bot))
