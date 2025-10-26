import discord
from discord.ext import commands
import sys
import os
import asyncio
import time
from datetime import datetime

class Admin(commands.Cog):
    """Commandes d'administration réservées au propriétaire du bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # ======================
    # GESTION DU BOT
    # ======================

    @commands.command(name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """Redémarre le bot"""
        embed = discord.Embed(
            title="🔄 Redémarrage du bot",
            description="Le bot redémarre... Il sera de retour dans quelques secondes.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        await self.bot.close()

    @commands.command(name="shutdown", aliases=["stop"])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Éteint complètement le bot"""
        embed = discord.Embed(
            title="⚠️ Arrêt du bot",
            description="Le bot s'éteint...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        await self.bot.close()
        sys.exit(0)

    @commands.command(name="load")
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        """Charge un cog
        Exemple: +load admin"""
        try:
            await self.bot.load_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                title="✅ Cog chargé",
                description=f"Le module `{cog}` a été chargé avec succès.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de charger `{cog}`\n```py\n{e}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        """Décharge un cog
        Exemple: +unload admin"""
        try:
            await self.bot.unload_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                title="✅ Cog déchargé",
                description=f"Le module `{cog}` a été déchargé avec succès.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de décharger `{cog}`\n```py\n{e}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Recharge un cog
        Exemple: +reload admin"""
        try:
            await self.bot.reload_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                title="✅ Cog rechargé",
                description=f"Le module `{cog}` a été rechargé avec succès.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de recharger `{cog}`\n```py\n{e}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="reloadall")
    @commands.is_owner()
    async def reload_all_cogs(self, ctx):
        """Recharge tous les cogs"""
        msg = await ctx.send("🔄 Rechargement de tous les cogs...")
        
        reloaded = []
        failed = []
        
        for extension in list(self.bot.extensions.keys()):
            try:
                await self.bot.reload_extension(extension)
                reloaded.append(extension.split('.')[-1])
            except Exception as e:
                failed.append(f"{extension.split('.')[-1]}: {str(e)[:50]}")
        
        embed = discord.Embed(
            title="🔄 Rechargement des cogs",
            color=discord.Color.blue()
        )
        
        if reloaded:
            embed.add_field(
                name="✅ Rechargés",
                value="\n".join([f"• {cog}" for cog in reloaded]) or "Aucun",
                inline=False
            )
        
        if failed:
            embed.add_field(
                name="❌ Échecs",
                value="\n".join([f"• {cog}" for cog in failed]) or "Aucun",
                inline=False
            )
        
        await msg.edit(content=None, embed=embed)

    @commands.command(name="listcogs")
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """Liste tous les cogs chargés"""
        cogs = [f"• `{cog}`" for cog in self.bot.cogs.keys()]
        
        embed = discord.Embed(
            title="📦 Cogs chargés",
            description="\n".join(cogs) if cogs else "Aucun cog chargé",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(cogs)} cog(s)")
        await ctx.send(embed=embed)

    # ======================
    # GESTION DES SERVEURS
    # ======================

    @commands.command(name="servers", aliases=["guilds"])
    @commands.is_owner()
    async def list_servers(self, ctx):
        """Liste tous les serveurs où le bot est présent"""
        guilds = []
        
        for guild in sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True):
            owner_name = str(guild.owner) if guild.owner else "Inconnu"
            guilds.append(
                f"**{guild.name}** (`{guild.id}`)\n"
                f"└ {guild.member_count} membres • Owner: {owner_name}"
            )
        
        # Pagination si trop de serveurs
        if len(guilds) > 10:
            guilds = guilds[:10]
            guilds.append(f"\n*... et {len(self.bot.guilds) - 10} autres serveurs*")
        
        embed = discord.Embed(
            title="🌐 Liste des serveurs",
            description="\n\n".join(guilds) if guilds else "Aucun serveur",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(self.bot.guilds)} serveur(s)")
        await ctx.send(embed=embed)

    @commands.command(name="serverlinks", aliases=["invites"])
    @commands.is_owner()
    async def server_links(self, ctx):
        """Génère des liens d'invitation pour tous les serveurs où le bot est présent"""
        msg = await ctx.send("🔗 Génération des liens d'invitation...")
        
        links = []
        no_permission = []
        
        for guild in sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True):
            try:
                # Vérifie si le bot a la permission de créer des invitations
                if not guild.me.guild_permissions.create_instant_invite:
                    no_permission.append(f"• **{guild.name}** (`{guild.id}`) - Pas de permission")
                    continue
                
                # Cherche un salon où créer l'invitation
                invite_channel = None
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).create_instant_invite:
                        invite_channel = channel
                        break
                
                if not invite_channel:
                    no_permission.append(f"• **{guild.name}** (`{guild.id}`) - Aucun salon disponible")
                    continue
                
                # Crée une invitation permanente
                invite = await invite_channel.create_invite(
                    max_age=0,  # Jamais expire
                    max_uses=0,  # Utilisations illimitées
                    reason="Demande du propriétaire du bot"
                )
                
                links.append(
                    f"**{guild.name}**\n"
                    f"└ {guild.member_count} membres • {invite.url}"
                )
                
            except Exception as e:
                no_permission.append(f"• **{guild.name}** (`{guild.id}`) - Erreur: {str(e)[:50]}")
        
        # Prépare l'embed
        embed = discord.Embed(
            title="🔗 Liens des serveurs",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if links:
            # Pagination si trop de serveurs
            if len(links) > 10:
                description = "\n\n".join(links[:10])
                description += f"\n\n*... et {len(links) - 10} autres serveurs (voir DM)*"
                
                # Envoie tous les liens en DM
                try:
                    dm_content = "\n\n".join(links)
                    chunks = [dm_content[i:i+1900] for i in range(0, len(dm_content), 1900)]
                    
                    for i, chunk in enumerate(chunks):
                        dm_embed = discord.Embed(
                            title=f"🔗 Liens des serveurs ({i+1}/{len(chunks)})",
                            description=chunk,
                            color=discord.Color.blue()
                        )
                        await ctx.author.send(embed=dm_embed)
                    
                    embed.set_footer(text="Liste complète envoyée en DM")
                except:
                    embed.set_footer(text="Impossible d'envoyer en DM")
            else:
                description = "\n\n".join(links)
            
            embed.description = description if len(links) <= 10 else description
        else:
            embed.description = "Aucun lien généré"
        
        if no_permission:
            # Limite l'affichage des erreurs
            error_list = "\n".join(no_permission[:5])
            if len(no_permission) > 5:
                error_list += f"\n*... et {len(no_permission) - 5} autres*"
            
            embed.add_field(
                name="⚠️ Impossible de générer",
                value=error_list,
                inline=False
            )
        
        embed.add_field(
            name="📊 Résumé",
            value=f"✅ Liens générés: **{len(links)}**\n❌ Échecs: **{len(no_permission)}**",
            inline=False
        )
        
        await msg.edit(content=None, embed=embed)

    @commands.command(name="leaveserver")
    @commands.is_owner()
    async def leave_server(self, ctx, guild_id: int):
        """Fait quitter le bot d'un serveur
        Exemple: +leaveserver 123456789"""
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send(f"❌ Serveur `{guild_id}` introuvable.")
        
        guild_name = guild.name
        
        try:
            await guild.leave()
            embed = discord.Embed(
                title="✅ Serveur quitté",
                description=f"Le bot a quitté **{guild_name}** (`{guild_id}`)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

    @commands.command(name="serverinfo")
    @commands.is_owner()
    async def server_info(self, ctx, guild_id: int = None):
        """Affiche les informations détaillées d'un serveur
        Exemple: +serverinfo 123456789
        Sans ID, affiche les infos du serveur actuel"""
        
        if guild_id is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send(f"❌ Serveur `{guild_id}` introuvable.")
        
        # Statistiques des membres
        total = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total - bots
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(
            name="🆔 ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        embed.add_field(
            name="👑 Propriétaire",
            value=f"{guild.owner.mention if guild.owner else 'Inconnu'}\n`{guild.owner.id if guild.owner else 'N/A'}`",
            inline=True
        )
        
        embed.add_field(
            name="📅 Créé le",
            value=f"<t:{int(guild.created_at.timestamp())}:F>",
            inline=False
        )
        
        embed.add_field(
            name="👥 Membres",
            value=f"```yaml\nTotal: {total}\nHumains: {humans}\nBots: {bots}```",
            inline=True
        )
        
        embed.add_field(
            name="📝 Salons",
            value=f"```yaml\nTexte: {len(guild.text_channels)}\nVocaux: {len(guild.voice_channels)}\nCatégories: {len(guild.categories)}```",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Rôles",
            value=f"`{len(guild.roles)}` rôles",
            inline=True
        )
        
        await ctx.send(embed=embed)

    # ======================
    # STATISTIQUES & DEBUG
    # ======================

    @commands.command(name="botstats", aliases=["stats"])
    @commands.is_owner()
    async def botstats(self, ctx):
        """Affiche les statistiques détaillées du bot"""
        # Uptime
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = f"<t:{int(self.start_time)}:R>"
        
        # Statistiques Discord
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Statistiques du bot",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🤖 Discord",
            value=f"```yaml\nServeurs: {len(self.bot.guilds)}\nUtilisateurs: {total_members}\nSalons: {total_channels}\nCommandes: {len(list(self.bot.walk_commands()))}```",
            inline=True
        )
        
        # Statistiques système (si psutil disponible)
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            embed.add_field(
                name="💻 Système",
                value=f"```yaml\nRAM: {memory_usage:.2f} MB\nCPU: {cpu_usage}%\nLatence: {round(self.bot.latency * 1000)}ms```",
                inline=True
            )
        except ImportError:
            embed.add_field(
                name="💻 Système",
                value=f"```yaml\nLatence: {round(self.bot.latency * 1000)}ms\nRAM/CPU: Non disponible\n(pip install psutil)```",
                inline=True
            )
        
        embed.add_field(
            name="⏱️ Uptime",
            value=f"Démarré {uptime_str}",
            inline=False
        )
        
        embed.add_field(
            name="🐍 Version",
            value=f"```\nPython: {sys.version.split()[0]}\nDiscord.py: {discord.__version__}```",
            inline=False
        )
        
        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
        await ctx.send(embed=embed)

    @commands.command(name="uptime")
    @commands.is_owner()
    async def uptime(self, ctx):
        """Affiche le temps de fonctionnement du bot"""
        uptime_seconds = int(time.time() - self.start_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_str = []
        if days > 0:
            uptime_str.append(f"{days}j")
        if hours > 0:
            uptime_str.append(f"{hours}h")
        if minutes > 0:
            uptime_str.append(f"{minutes}m")
        uptime_str.append(f"{seconds}s")
        
        embed = discord.Embed(
            title="⏱️ Uptime",
            description=f"Le bot fonctionne depuis **{' '.join(uptime_str)}**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Démarré le",
            value=f"<t:{int(self.start_time)}:F>",
            inline=False
        )
        await ctx.send(embed=embed)

    # ======================
    # COMMANDES SYSTÈME
    # ======================

    @commands.command(name="eval")
    @commands.is_owner()
    async def eval_code(self, ctx, *, code: str):
        """Évalue du code Python (DANGER - Owner uniquement)
        Exemple: +eval 1+1"""
        try:
            # Retire les backticks si présents
            if code.startswith('```py') or code.startswith('```python'):
                code = code.split('```')[1].strip('python').strip('py').strip()
            elif code.startswith('```'):
                code = code.strip('```').strip()
            
            # Évalue le code
            result = eval(code)
            
            embed = discord.Embed(
                title="✅ Évaluation réussie",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📥 Entrée",
                value=f"```py\n{code[:1000]}```",
                inline=False
            )
            embed.add_field(
                name="📤 Sortie",
                value=f"```py\n{str(result)[:1000]}```",
                inline=False
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"```py\n{str(e)[:2000]}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Synchronise les commandes slash (si utilisées)"""
        msg = await ctx.send("🔄 Synchronisation des commandes...")
        
        try:
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                title="✅ Commandes synchronisées",
                description=f"**{len(synced)}** commande(s) slash synchronisée(s).",
                color=discord.Color.green()
            )
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur de synchronisation",
                description=f"```py\n{str(e)[:1000]}```",
                color=discord.Color.red()
            )
            await msg.edit(content=None, embed=embed)

    @commands.command(name="dm")
    @commands.is_owner()
    async def dm_user(self, ctx, user_id: int, *, message: str):
        """Envoie un message privé à un utilisateur
        Exemple: +dm 123456789 Bonjour!"""
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            
            embed = discord.Embed(
                title="✅ Message envoyé",
                description=f"Message envoyé à **{user}** (`{user_id}`)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Impossible d'envoyer un message à cet utilisateur (DM fermés).")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

    @commands.command(name="announce")
    @commands.is_owner()
    async def announce_to_servers(self, ctx, *, message: str):
        """Envoie une annonce dans tous les serveurs (premier salon disponible)"""
        sent = 0
        failed = 0
        
        msg = await ctx.send("📢 Envoi de l'annonce...")
        
        for guild in self.bot.guilds:
            try:
                # Trouve le premier salon où le bot peut écrire
                channel = None
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                
                if channel:
                    embed = discord.Embed(
                        title="📢 Annonce",
                        description=message,
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_footer(text=f"Envoyé depuis {self.bot.user.name}")
                    await channel.send(embed=embed)
                    sent += 1
                else:
                    failed += 1
            except:
                failed += 1
            
            # Pause pour éviter le rate limit
            await asyncio.sleep(1)
        
        embed = discord.Embed(
            title="✅ Annonce envoyée",
            description=f"Envoyé dans **{sent}** serveur(s)\nÉchec: **{failed}** serveur(s)",
            color=discord.Color.green()
        )
        await msg.edit(content=None, embed=embed)

    # ======================
    # GESTION DES ERREURS
    # ======================

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Gestion des erreurs pour les commandes du cog"""
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="❌ Accès refusé",
                description="Cette commande est réservée au propriétaire du bot.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=5)

# Setup
async def setup(bot):
    await bot.add_cog(Admin(bot))
    print("✅ Cog Admin chargé avec succès")