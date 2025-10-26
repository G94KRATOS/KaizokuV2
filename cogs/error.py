import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignorer les commandes inexistantes
        if isinstance(error, commands.CommandNotFound):
            return

        # Permissions manquantes
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        
        # Argument manquant
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Il manque un argument : `{error.param}`")
        
        # Mauvais argument
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide.")

        # Erreurs inattendues
        else:
            print(f"❌ Erreur commande {ctx.command}: {error}")
            await ctx.send(f"❌ Une erreur inattendue est survenue. Vérifie la console pour plus de détails.")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
