import discord
from discord.ext import commands
from datetime import datetime
import aiohttp
import asyncio

class Owner(commands.Cog):
    """Commandes avancées pour les Owner Bot (niveau 5)"""
    
    def __init__(self, bot):
        self.bot = bot
        # ID de ton serveur support
        self.SUPPORT_SERVER_ID = 1431645461248475218
        # ID du salon de logs dans ton serveur support
        self.LOG_CHANNEL_ID = 1431797410270810182
    
    def get_perms_cog(self):
        """Récupère le cog de permissions"""
        return self.bot.get_cog("PermissionsSystem")
    
    async def log_owner_action(self, ctx, action: str, details: dict = None, color: discord.Color = discord.Color.blue()):
        """Envoie un log dans le serveur support"""
        try:
            log_channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
            if not log_channel:
                return
            
            embed = discord.Embed(
                title=f"🔔 {action}",
                color=color,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="👤 Exécuté par",
                value=f"{ctx.author.mention}\n`{ctx.author}` (`{ctx.author.id}`)",
                inline=True
            )
            
            if ctx.guild:
                embed.add_field(
                    name="🌐 Serveur",
                    value=f"**{ctx.guild.name}**\n`{ctx.guild.id}`",
                    inline=True
                )
            else:
                embed.add_field(name="🌐 Serveur", value="DM", inline=True)
            
            embed.add_field(
                name="⚙️ Commande",
                value=f"`{ctx.message.content}`",
                inline=False
            )
            
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
    
    @commands.command(name="botstatus", aliases=["changestatus", "setstatus"])
    async def set_status(self, ctx, activity_type: str, *, text: str):
        """Change le statut du bot - Owner Bot (5)
        Types: playing, watching, listening, streaming, competing"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        activity_type = activity_type.lower()
        
        try:
            if activity_type in ["playing", "play", "game"]:
                activity = discord.Game(name=text)
            elif activity_type in ["watching", "watch"]:
                activity = discord.Activity(type=discord.ActivityType.watching, name=text)
            elif activity_type in ["listening", "listen"]:
                activity = discord.Activity(type=discord.ActivityType.listening, name=text)
            elif activity_type in ["streaming", "stream"]:
                activity = discord.Streaming(name=text, url="https://twitch.tv/discord")
            elif activity_type in ["competing", "compete"]:
                activity = discord.Activity(type=discord.ActivityType.competing, name=text)
            else:
                return await ctx.send("❌ Type invalide: `playing`, `watching`, `listening`, `streaming`, `competing`")
            
            await self.bot.change_presence(activity=activity)
            
            embed = discord.Embed(
                title="✅ Statut modifié",
                description=f"**Type:** {activity_type.capitalize()}\n**Texte:** {text}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            await self.log_owner_action(ctx, "Statut Modifié", {"📝 Type": activity_type, "💬 Texte": text}, discord.Color.blue())
            
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="botstatustype", aliases=["setonline"])
    async def set_status_type(self, ctx, status_type: str):
        """Change le type de statut - Owner Bot (5)
        Types: online, idle, dnd, invisible"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        
        if status_type.lower() not in status_map:
            return await ctx.send("❌ Type invalide: `online`, `idle`, `dnd`, `invisible`")
        
        try:
            await self.bot.change_presence(status=status_map[status_type.lower()])
            await ctx.send(f"✅ Statut changé: **{status_type}**")
            await self.log_owner_action(ctx, "Type Statut Modifié", {"🟢 Statut": status_type.upper()}, discord.Color.green())
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ======================
    # GESTION PSEUDO/AVATAR
    # ======================
    
    @commands.command(name="botname", aliases=["changename"])
    async def set_bot_name(self, ctx, *, name: str):
        """Change le nom du bot - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        try:
            old_name = self.bot.user.name
            await self.bot.user.edit(username=name)
            
            embed = discord.Embed(
                title="✅ Nom modifié",
                description=f"**{old_name}** → **{name}**",
                color=discord.Color.green()
            )
            embed.set_footer(text="Limite: 2 changements/heure")
            await ctx.send(embed=embed)
            await self.log_owner_action(ctx, "Nom Bot Modifié", {"📛 Ancien": old_name, "✨ Nouveau": name}, discord.Color.gold())
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="botavatar", aliases=["changeavatar"])
    async def set_bot_avatar(self, ctx, url: str = None):
        """Change l'avatar du bot - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        elif not url:
            return await ctx.send("❌ Fournissez une URL ou attachez une image.")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("❌ Impossible de télécharger l'image.")
                    avatar_bytes = await resp.read()
                    await self.bot.user.edit(avatar=avatar_bytes)
            
            embed = discord.Embed(title="✅ Avatar modifié", color=discord.Color.green())
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            await self.log_owner_action(ctx, "Avatar Bot Modifié", {}, discord.Color.purple())
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ======================
    # BLACKLISTS
    # ======================
    
    @commands.command(name="bls", aliases=["blserv", "blserver"])
    async def blacklist_server(self, ctx, guild_id: int, *, reason: str = "Aucune raison"):
        """Blacklist un serveur - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send(f"❌ Serveur `{guild_id}` introuvable.")
        
        guild_name = guild.name
        guild_members = guild.member_count
        
        if not hasattr(self.bot, 'blacklisted_servers'):
            self.bot.blacklisted_servers = []
        
        if guild_id not in self.bot.blacklisted_servers:
            self.bot.blacklisted_servers.append(guild_id)
        
        try:
            await guild.leave()
            embed = discord.Embed(
                title="🚫 Serveur blacklisté",
                description=f"**{guild_name}** (`{guild_id}`) quitté.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
            await self.log_owner_action(ctx, "⛔ Serveur Blacklisté", 
                {"🏷️ Nom": guild_name, "🆔 ID": str(guild_id), "👥 Membres": str(guild_members), "📋 Raison": reason},
                discord.Color.red())
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="unbls", aliases=["unblserv"])
    async def unblacklist_server(self, ctx, guild_id: int):
        """Retire un serveur de la blacklist - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        if not hasattr(self.bot, 'blacklisted_servers'):
            self.bot.blacklisted_servers = []
        
        if guild_id not in self.bot.blacklisted_servers:
            return await ctx.send(f"❌ Serveur `{guild_id}` non blacklisté.")
        
        self.bot.blacklisted_servers.remove(guild_id)
        await ctx.send(f"✅ Serveur `{guild_id}` retiré de la blacklist.")
        await self.log_owner_action(ctx, "✅ Serveur Déblacklisté", {"🆔 ID": str(guild_id)}, discord.Color.green())
    
    @commands.command(name="bl", aliases=["bluser", "blu"])
    async def blacklist_user(self, ctx, user_id: int, *, reason: str = "Aucune raison"):
        """Blacklist un utilisateur - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        if not hasattr(self.bot, 'blacklisted_users'):
            self.bot.blacklisted_users = []
        
        if user_id in self.bot.blacklisted_users:
            return await ctx.send(f"❌ Utilisateur `{user_id}` déjà blacklisté.")
        
        self.bot.blacklisted_users.append(user_id)
        
        try:
            user = await self.bot.fetch_user(user_id)
            embed = discord.Embed(
                title="🚫 Utilisateur blacklisté",
                description=f"**{user}** (`{user_id}`) ne peut plus utiliser le bot.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
            await self.log_owner_action(ctx, "⛔ Utilisateur Blacklisté", {"👤 User": f"{user} (`{user.id}`)", "📋 Raison": reason}, discord.Color.red())
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="unbl", aliases=["unbluser"])
    async def unblacklist_user(self, ctx, user_id: int):
        """Retire un utilisateur de la blacklist - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        if not hasattr(self.bot, 'blacklisted_users'):
            self.bot.blacklisted_users = []
        
        if user_id not in self.bot.blacklisted_users:
            return await ctx.send(f"❌ Utilisateur `{user_id}` non blacklisté.")
        
        self.bot.blacklisted_users.remove(user_id)
        
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.send(f"✅ **{user}** peut à nouveau utiliser le bot.")
            await self.log_owner_action(ctx, "✅ Utilisateur Déblacklisté", {"👤 User": f"{user} (`{user.id}`)"}, discord.Color.green())
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="blacklist", aliases=["blacklists"])
    async def show_blacklist(self, ctx):
        """Affiche les blacklists - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        if not hasattr(self.bot, 'blacklisted_servers'):
            self.bot.blacklisted_servers = []
        if not hasattr(self.bot, 'blacklisted_users'):
            self.bot.blacklisted_users = []
        
        embed = discord.Embed(title="🚫 Blacklists", color=discord.Color.red())
        
        if self.bot.blacklisted_servers:
            servers = "\n".join([f"`{sid}`" for sid in self.bot.blacklisted_servers])
            embed.add_field(name=f"🌐 Serveurs ({len(self.bot.blacklisted_servers)})", value=servers, inline=False)
        else:
            embed.add_field(name="🌐 Serveurs", value="Aucun", inline=False)
        
        if self.bot.blacklisted_users:
            users_list = []
            for uid in self.bot.blacklisted_users[:10]:
                try:
                    user = await self.bot.fetch_user(uid)
                    users_list.append(f"**{user}** (`{uid}`)")
                except:
                    users_list.append(f"`{uid}`")
            embed.add_field(name=f"👤 Utilisateurs ({len(self.bot.blacklisted_users)})", value="\n".join(users_list), inline=False)
            if len(self.bot.blacklisted_users) > 10:
                embed.set_footer(text=f"Limité à 10/{len(self.bot.blacklisted_users)}")
        else:
            embed.add_field(name="👤 Utilisateurs", value="Aucun", inline=False)
        
        await ctx.send(embed=embed)
    
    # ======================
    # STATISTIQUES
    # ======================
    
    @commands.command(name="ownerinfo", aliases=["botinfo", "stats"])
    async def owner_info(self, ctx):
        """Stats complètes du bot - Owner Bot (5)"""
        
        perms_cog = self.get_perms_cog()
        if not perms_cog or perms_cog.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Nécessite le niveau **Owner Bot** (5).")
        
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        embed = discord.Embed(title="📊 Statistiques Bot", color=discord.Color.gold())
        embed.add_field(name="🌐 Serveurs", value=f"```yaml\n{len(self.bot.guilds)}```", inline=True)
        embed.add_field(name="👥 Utilisateurs", value=f"```yaml\n{total_members:,}```", inline=True)
        embed.add_field(name="📝 Salons", value=f"```yaml\n{total_channels}```", inline=True)
        embed.add_field(name="⚙️ Commandes", value=f"```yaml\n{len(list(self.bot.walk_commands()))}```", inline=True)
        embed.add_field(name="🔗 Latence", value=f"```yaml\n{round(self.bot.latency * 1000)}ms```", inline=True)
        embed.add_field(name="📦 Cogs", value=f"```yaml\n{len(self.bot.cogs)}```", inline=True)
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))

async def teardown(bot):
    """Appelé lors du déchargement du cog"""
    pass
