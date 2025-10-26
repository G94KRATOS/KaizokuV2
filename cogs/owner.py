import discord
from discord.ext import commands
from datetime import datetime
import aiohttp
import asyncio
import io

class Owner(commands.Cog):
    """Commandes avancées pour les Owner Bot (niveau 5)"""
    
    def __init__(self, bot):
        self.bot = bot
        # ID de ton serveur support
        self.SUPPORT_SERVER_ID = 1431645461248475218  # ⚠️ REMPLACE PAR L'ID DE TON SERVEUR
        # ID du salon de logs dans ton serveur support
        self.LOG_CHANNEL_ID = 1431797410270810182  # ⚠️ REMPLACE PAR L'ID DU SALON DE LOGS
    
    def get_perms_cog(self):
        """Récupère le cog de permissions"""
        return self.bot.get_cog("PermissionsSystem")
    
    async def log_owner_action(self, ctx, action: str, details: dict = None, color: discord.Color = discord.Color.blue()):
        """Envoie un log dans le serveur support"""
        try:
            # Récupère le salon de logs
            log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
            if not log_channel:
                return
            
            # Création de l'embed
            embed = discord.Embed(
                title=f"🔔 {action}",
                color=color,
                timestamp=datetime.utcnow()
            )
            
            # Informations de l'utilisateur
            embed.add_field(
                name="👤 Exécuté par",
                value=f"{ctx.author.mention}\n`{ctx.author}` (`{ctx.author.id}`)",
                inline=True
            )
            
            # Serveur d'origine
            if ctx.guild:
                embed.add_field(
                    name="🌐 Serveur",
                    value=f"**{ctx.guild.name}**\n`{ctx.guild.id}`",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🌐 Serveur",
                    value="DM",
                    inline=True
                )
            
            # Commande utilisée
            embed.add_field(
                name="⚙️ Commande",
                value=f"`{ctx.message.content}`",
                inline=False
            )
            
            # Détails supplémentaires
            if details:
                for key, value in details.items():
                    embed.add_field(name=key, value=value, inline=True)
            
            embed.set_footer(text=f"User ID: {ctx.author.id}")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erreur lors du log: {e}")
    
    # ======================
    # GESTION DU STATUT
    # ======================
    
    @commands.command(name="botstatus", aliases=["changestatus"])
    async def set_status(self, ctx, activity_type: str, *, text: str):
        """Change le statut du bot - Nécessite Owner Bot (5)
        Types: playing, watching, listening, streaming, competing
        Exemple: +botstatus playing Minecraft
                 +botstatus watching YouTube
                 +botstatus listening Spotify"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        activity_type = activity_type.lower()
        
        try:
            if activity_type in ["playing", "play", "game"]:
                activity = discord.Game(name=text)
            elif activity_type in ["watching", "watch"]:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=text
                )
            elif activity_type in ["listening", "listen"]:
                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=text
                )
            elif activity_type in ["streaming", "stream"]:
                activity = discord.Streaming(
                    name=text,
                    url="https://twitch.tv/discord"
                )
            elif activity_type in ["competing", "compete"]:
                activity = discord.Activity(
                    type=discord.ActivityType.competing,
                    name=text
                )
            else:
                return await ctx.send(
                    "❌ Type invalide. Utilisez: `playing`, `watching`, `listening`, `streaming`, `competing`"
                )
            
            await self.bot.change_presence(activity=activity)
            
            embed = discord.Embed(
                title="✅ Statut modifié",
                description=f"**Type:** {activity_type.capitalize()}\n**Texte:** {text}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
            # Log l'action
            await self.log_owner_action(
                ctx,
                "Statut du Bot Modifié",
                {
                    "📝 Type": activity_type.capitalize(),
                    "💬 Texte": text
                },
                discord.Color.blue()
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="botstatustype", aliases=["setonline"])
    async def set_status_type(self, ctx, status_type: str):
        """Change le type de statut - Nécessite Owner Bot (5)
        Types: online, idle, dnd, invisible
        Exemple: +botstatustype online"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        status_type = status_type.lower()
        
        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        
        if status_type not in status_map:
            return await ctx.send("❌ Type invalide. Utilisez: `online`, `idle`, `dnd`, `invisible`")
        
        try:
            await self.bot.change_presence(status=status_map[status_type])
            
            embed = discord.Embed(
                title="✅ Type de statut modifié",
                description=f"Statut: **{status_type}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
            # Log l'action
            await self.log_owner_action(
                ctx,
                "Type de Statut Modifié",
                {
                    "🟢 Nouveau statut": status_type.upper()
                },
                discord.Color.green()
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ======================
    # GESTION DU PSEUDO/AVATAR
    # ======================
    
    @commands.command(name="botname", aliases=["changename"])
    async def set_bot_name(self, ctx, *, name: str):
        """Change le nom du bot - Nécessite Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        try:
            old_name = self.bot.user.name
            await self.bot.user.edit(username=name)
            
            embed = discord.Embed(
                title="✅ Nom du bot modifié",
                description=f"**{old_name}** → **{name}**",
                color=discord.Color.green()
            )
            embed.set_footer(text="Limite: 2 changements par heure")
            await ctx.send(embed=embed)
            
            # Log l'action
            await self.log_owner_action(
                ctx,
                "Nom du Bot Modifié",
                {
                    "📛 Ancien nom": old_name,
                    "✨ Nouveau nom": name
                },
                discord.Color.gold()
            )
            
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="botavatar", aliases=["changeavatar"])
    async def set_bot_avatar(self, ctx, url: str = None):
        """Change l'avatar du bot - Nécessite Owner Bot (5)
        Exemple: +botavatar [lien image]
        Ou envoyer une image avec la commande"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        # Récupère l'image depuis l'attachement ou l'URL
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        elif not url:
            return await ctx.send("❌ Veuillez fournir une URL d'image ou attacher une image.")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("❌ Impossible de télécharger l'image.")
                    
                    avatar_bytes = await resp.read()
                    await self.bot.user.edit(avatar=avatar_bytes)
            
            embed = discord.Embed(
                title="✅ Avatar du bot modifié",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            
            # Log l'action avec l'image
            await self.log_owner_action(
                ctx,
                "Avatar du Bot Modifié",
                {
                    "🖼️ Nouvel avatar": f"[Voir l'image]({self.bot.user.display_avatar.url})"
                },
                discord.Color.purple()
            )
            
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erreur : {e}")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du téléchargement : {e}")
  
    
    # ======================
    # GESTION DES BLACKLISTS
    # ======================
    
    @commands.command(name="blserver", aliases=["blserver"])
    async def blacklist_server(self, ctx, guild_id: int, *, reason: str = "Aucune raison"):
        """Blacklist un serveur et le quitte - Nécessite Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send(f"❌ Serveur `{guild_id}` introuvable.")
        
        guild_name = guild.name
        guild_members = guild.member_count
        
        try:
            await guild.leave()
            
            embed = discord.Embed(
                title="🚫 Serveur blacklisté",
                description=f"**{guild_name}** (`{guild_id}`) a été blacklisté et quitté.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
            
            # Log l'action
            await self.log_owner_action(
                ctx,
                "⛔ Serveur Blacklisté",
                {
                    "🏷️ Nom du serveur": guild_name,
                    "🆔 ID": str(guild_id),
                    "👥 Membres": str(guild_members),
                    "📋 Raison": reason
                },
                discord.Color.red()
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="bl", aliases=["bluser"])
    async def blacklist_user(self, ctx, user_id: int, *, reason: str = "Aucune raison"):
        """Blacklist un utilisateur (empêche d'utiliser le bot) - Nécessite Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        try:
            user = await self.bot.fetch_user(user_id)
            
            embed = discord.Embed(
                title="🚫 Utilisateur blacklisté",
                description=f"**{user}** (`{user_id}`) ne peut plus utiliser le bot.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.set_footer(text="Note: Fonctionnalité à implémenter dans le système de permissions")
            await ctx.send(embed=embed)
            
            # Log l'action
            await self.log_owner_action(
                ctx,
                "⛔ Utilisateur Blacklisté",
                {
                    "👤 Utilisateur": f"{user} (`{user.id}`)",
                    "📋 Raison": reason
                },
                discord.Color.red()
            )
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    
    # ======================
    # STATISTIQUES AVANCÉES
    # ======================
    
    @commands.command(name="ownerinfo", aliases=["botinfo"])
    async def owner_info(self, ctx):
        """Affiche les statistiques complètes du bot - Nécessite Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        # Statistiques Discord
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        total_text = sum(len(g.text_channels) for g in self.bot.guilds)
        total_voice = sum(len(g.voice_channels) for g in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Statistiques complètes du bot",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🌐 Serveurs",
            value=f"```yaml\nTotal: {len(self.bot.guilds)}\nMoyenne: {total_members // len(self.bot.guilds) if self.bot.guilds else 0} membres/serveur```",
            inline=True
        )
        
        embed.add_field(
            name="👥 Utilisateurs",
            value=f"```yaml\nTotal: {total_members:,}\nUniques: {len(self.bot.users):,}```",
            inline=True
        )
        
        embed.add_field(
            name="📝 Salons",
            value=f"```yaml\nTotal: {total_channels}\nTexte: {total_text}\nVocaux: {total_voice}```",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Commandes",
            value=f"```yaml\nTotal: {len(list(self.bot.walk_commands()))}\nCogs: {len(self.bot.cogs)}```",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Connexion",
            value=f"```yaml\nLatence: {round(self.bot.latency * 1000)}ms\nStatut: Connecté```",
            inline=True
        )
        
        # Uptime
        if hasattr(self.bot, 'uptime'):
            uptime_seconds = int((datetime.utcnow() - self.bot.uptime).total_seconds())
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            
            uptime_str = []
            if days > 0:
                uptime_str.append(f"{days}j")
            if hours > 0:
                uptime_str.append(f"{hours}h")
            if minutes > 0:
                uptime_str.append(f"{minutes}m")
            
            embed.add_field(
                name="⏱️ Uptime",
                value=f"```yaml\n{' '.join(uptime_str) if uptime_str else '< 1m'}```",
                inline=True
            )
        
        # Système (si psutil disponible)
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            embed.add_field(
                name="💻 Ressources",
                value=f"```yaml\nRAM: {memory_usage:.2f} MB\nCPU: {cpu_usage}%```",
                inline=False
            )
        except ImportError:
            pass
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
        
        await ctx.send(embed=embed)
        
        # Log l'action
        await self.log_owner_action(
            ctx,
            "📊 Statistiques Consultées",
            {
                "📈 Serveurs": str(len(self.bot.guilds)),
                "👥 Utilisateurs": f"{total_members:,}"
            },
            discord.Color.blue()
        )
    
    # ======================
    # MAINTENANCE
    # ======================
    
    @commands.command(name="maintenance")
    async def toggle_maintenance(self, ctx):
        """Active/désactive le mode maintenance - Nécessite Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Cette commande nécessite le niveau **Owner Bot** (5).")
        
        # Toggle maintenance mode
        if not hasattr(self.bot, 'maintenance_mode'):
            self.bot.maintenance_mode = False
        
        self.bot.maintenance_mode = not self.bot.maintenance_mode
        
        status = "activé" if self.bot.maintenance_mode else "désactivé"
        color = discord.Color.orange() if self.bot.maintenance_mode else discord.Color.green()
        
        embed = discord.Embed(
            title=f"🔧 Mode maintenance {status}",
            description="Le bot est maintenant en maintenance." if self.bot.maintenance_mode else "Le bot est de nouveau opérationnel.",
            color=color
        )
        await ctx.send(embed=embed)
        
        # Log l'action
        await self.log_owner_action(
            ctx,
            f"🔧 Mode Maintenance {'Activé' if self.bot.maintenance_mode else 'Désactivé'}",
            {
                "⚙️ Statut": "EN MAINTENANCE" if self.bot.maintenance_mode else "OPÉRATIONNEL"
            },
            discord.Color.orange() if self.bot.maintenance_mode else discord.Color.green()
        )

async def setup(bot):
    await bot.add_cog(Owner(bot))
    print("✅ Cog Owner chargé avec succès")