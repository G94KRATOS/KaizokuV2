# cogs/fun.py
import discord
from discord.ext import commands, tasks
import asyncio
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx, seconds: int, *, prize: str):
        """Lance un giveaway. Usage: !giveaway <secondes> <prix>"""
        embed = discord.Embed(
            title="🎁 Giveaway !",
            description=f"**Prix :** {prize}\nRéagissez avec 🎉 pour participer !\nDurée : {seconds} secondes",
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Lancé par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        await asyncio.sleep(seconds)

        # Récupérer le message mis à jour
        try:
            message = await ctx.channel.fetch_message(message.id)
            reaction = discord.utils.get(message.reactions, emoji="🎉")
            users = [user async for user in reaction.users() if not user.bot]
        except Exception:
            await ctx.send("❌ Impossible de récupérer les participants.")
            return

        if users:
            winner = random.choice(users)
            win_embed = discord.Embed(
                title="🏆 Giveaway terminé !",
                description=f"Félicitations {winner.mention} ! Vous avez gagné **{prize}** !",
                color=discord.Color.gold()
            )
            await ctx.send(embed=win_embed)
        else:
            await ctx.send("Aucun participant n'a réagi au giveaway 😢")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
