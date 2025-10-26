import discord
from discord.ext import commands

class Utils(commands.Cog):
    """Commandes utilitaires."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", help="Affiche des infos sur un membre")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Infos sur {member}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Nom", value=member.name, inline=False)
        embed.add_field(name="Statut", value=member.status, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))
