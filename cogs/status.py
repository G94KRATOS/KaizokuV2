import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio

class Status(commands.Cog):
    """Affiche et met à jour automatiquement le statut du bot dans un salon"""
    
    def __init__(self, bot):
        self.bot = bot
        self.status_channel_id = None  # ID du salon où afficher le statut
        self.status_message_id = None  # ID du message de statut
        self.update_status.start()  # Démarre la boucle de mise à jour
    
    def cog_unload(self):
        """Arrête la boucle quand le cog est déchargé"""
        self.update_status.cancel()
    
    # ======================
    # CONFIGURATION
    # ======================
    
    @commands.command(name="setstatus")
    @commands.has_permissions(administrator=True)
    async def set_status_channel(self, ctx):
        """Configure le salon actuel pour afficher le statut du bot"""
        self.status_channel_id = ctx.channel.id
        
        # Crée le premier message de statut
        embed = await self.create_status_embed()
        message = await ctx.send(embed=embed)
        self.status_message_id = message.id
        
        success_embed = discord.Embed(
            title="✅ Statut configuré",
            description=f"Le statut du bot sera mis à jour automatiquement dans ce salon toutes les 5 minutes.",
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed, delete_after=10)
        await ctx.message.delete(delay=10)
    
    @commands.command(name="removestatus")
    @commands.has_permissions(administrator=True)
    async def remove_status(self, ctx):
        """Retire le statut automatique du bot"""
        if self.status_channel_id:
            self.status_channel_id = None
            self.status_message_id = None
            
            embed = discord.Embed(
                title="✅ Statut retiré",
                description="Le statut automatique a été désactivé.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            await ctx.send("❌ Aucun statut n'est configuré.", delete_after=5)
    
    # ======================
    # CRÉATION DE L'EMBED
    # ======================
    
    async def create_status_embed(self):
        """Crée l'embed du statut du bot"""
        # Calcul de l'uptime
        uptime_seconds = int(discord.utils.utcnow().timestamp() - self.bot.uptime.timestamp()) if hasattr(self.bot, 'uptime') else 0
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
        if not uptime_str:
            uptime_str.append("< 1m")
        
        # Statistiques
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        # Crée l'embed
        embed = discord.Embed(
            title="📊 Statut du Bot",
            description="Informations en temps réel sur le bot",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        # Statut en ligne
        embed.add_field(
            name="🟢 Statut",
            value="**En ligne**",
            inline=True
        )
        
        # Latence
        latency = round(self.bot.latency * 1000)
        latency_emoji = "🟢" if latency < 100 else "🟡" if latency < 200 else "🔴"
        embed.add_field(
            name=f"{latency_emoji} Latence",
            value=f"**{latency}ms**",
            inline=True
        )
        
        # Uptime
        embed.add_field(
            name="⏱️ Uptime",
            value=f"**{' '.join(uptime_str)}**",
            inline=True
        )
        
        # Serveurs
        embed.add_field(
            name="🌐 Serveurs",
            value=f"**{len(self.bot.guilds)}** serveur(s)",
            inline=True
        )
        
        # Utilisateurs
        embed.add_field(
            name="👥 Utilisateurs",
            value=f"**{total_members:,}** utilisateur(s)",
            inline=True
        )
        
        # Salons
        embed.add_field(
            name="📝 Salons",
            value=f"**{total_channels}** salon(s)",
            inline=True
        )
        
        # Commandes disponibles
        embed.add_field(
            name="⚙️ Commandes",
            value=f"**{len(list(self.bot.walk_commands()))}** commande(s)",
            inline=True
        )
        
        # Version Discord.py
        embed.add_field(
            name="🐍 Discord.py",
            value=f"**v{discord.__version__}**",
            inline=True
        )
        
        # CPU & RAM (si psutil disponible)
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            embed.add_field(
                name="💻 Ressources",
                value=f"**CPU:** {cpu_usage}%\n**RAM:** {memory_usage:.1f} MB",
                inline=True
            )
        except ImportError:
            pass
        
        embed.set_footer(text=f"Dernière mise à jour")
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        return embed
    
    # ======================
    # BOUCLE DE MISE À JOUR
    # ======================
    
    @tasks.loop(hours=1)
    async def update_status(self):
        """Met à jour le message de statut toutes les 5 minutes"""
        if not self.status_channel_id or not self.status_message_id:
            return
        
        try:
            channel = self.bot.get_channel(self.status_channel_id)
            if not channel:
                return
            
            # Récupère et met à jour le message
            try:
                message = await channel.fetch_message(self.status_message_id)
                embed = await self.create_status_embed()
                await message.edit(embed=embed)
            except discord.NotFound:
                # Le message a été supprimé, on en crée un nouveau
                embed = await self.create_status_embed()
                message = await channel.send(embed=embed)
                self.status_message_id = message.id
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du statut: {e}")
    
    @update_status.before_loop
    async def before_update_status(self):
        """Attend que le bot soit prêt avant de démarrer la boucle"""
        await self.bot.wait_until_ready()
    
    # ======================
    # COMMANDE MANUELLE
    # ======================
    
    @commands.command(name="updatestatus")
    @commands.has_permissions(administrator=True)
    async def force_update_status(self, ctx):
        """Force la mise à jour immédiate du statut"""
        if not self.status_channel_id or not self.status_message_id:
            return await ctx.send("❌ Aucun statut n'est configuré. Utilisez `+setstatus` d'abord.", delete_after=5)
        
        try:
            channel = self.bot.get_channel(self.status_channel_id)
            message = await channel.fetch_message(self.status_message_id)
            embed = await self.create_status_embed()
            await message.edit(embed=embed)
            
            await ctx.send("✅ Statut mis à jour!", delete_after=5)
            await ctx.message.delete(delay=5)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}", delete_after=10)
    
# Setup
async def setup(bot):
    await bot.add_cog(Status(bot))
    print("✅ Cog Status chargé avec succès")