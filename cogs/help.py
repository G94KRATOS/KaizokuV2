import discord
from discord.ext import commands
from discord.ui import Select, View, Button
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 🎨 CONFIGURATION VISUELLE
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "primary": discord.Color.from_rgb(88, 101, 242),      # Discord Blurple
    "success": discord.Color.from_rgb(87, 242, 135),      # Vert
    "info": discord.Color.from_rgb(52, 152, 219),         # Bleu
    "warning": discord.Color.from_rgb(254, 231, 92),      # Jaune
    "danger": discord.Color.from_rgb(237, 66, 69),        # Rouge
    "gold": discord.Color.from_rgb(255, 215, 0),          # Or
    "purple": discord.Color.from_rgb(155, 89, 182),       # Violet
}

EMOJI_MAP = {
    "Basic": "⚡",
    "Moderation": "🛡️",
    "Fun": "🎮",
    "Utils": "🛠️",
    "Admin": "🔑",
    "Logger": "📋",
    "Economy": "💰",
    "Giveaway": "🎁",
    "Gestion": "⚙️",
    "PermissionsSystem": "🔐",
    "Tickets": "🎫",
    "Status": "📊",
    "Owner": "👑",
    "ServerLogger": "📝"
}

CATEGORY_INFO = {
    "Basic": {
        "desc": "Commandes essentielles pour tous les utilisateurs",
        "color": COLORS["info"]
    },
    "Moderation": {
        "desc": "Outils puissants pour modérer votre serveur",
        "color": COLORS["danger"]
    },
    "Fun": {
        "desc": "Commandes amusantes pour divertir la communauté",
        "color": COLORS["warning"]
    },
    "Utils": {
        "desc": "Utilitaires pratiques du quotidien",
        "color": COLORS["primary"]
    },
    "Admin": {
        "desc": "Administration avancée du serveur",
        "color": COLORS["gold"]
    },
    "Logger": {
        "desc": "Système de journalisation des événements",
        "color": COLORS["purple"]
    },
    "Economy": {
        "desc": "Système d'économie virtuelle complet",
        "color": COLORS["success"]
    },
    "Giveaway": {
        "desc": "Organisation de concours et giveaways",
        "color": COLORS["warning"]
    },
    "Gestion": {
        "desc": "Gestion complète du serveur",
        "color": COLORS["info"]
    },
    "PermissionsSystem": {
        "desc": "Configuration des permissions du bot",
        "color": COLORS["danger"]
    },
    "Tickets": {
        "desc": "Système de tickets de support",
        "color": COLORS["primary"]
    },
    "Status": {
        "desc": "Statistiques et statut du bot",
        "color": COLORS["purple"]
    },
    "Owner": {
        "desc": "Commandes réservées aux propriétaires",
        "color": COLORS["gold"]
    }
}

# ═══════════════════════════════════════════════════════════════
# 🎯 BOUTONS INTERACTIFS
# ═══════════════════════════════════════════════════════════════

class HomeButton(Button):
    """Bouton pour retourner au menu principal"""
    def __init__(self, bot):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Accueil",
            emoji="🏠",
            row=1
        )
        self.bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            embed = create_main_embed(self.bot, interaction.user)
            view = MainHelpView(self.bot)
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            print(f"❌ Erreur HomeButton: {e}")

class InfoButton(Button):
    """Bouton d'informations détaillées"""
    def __init__(self, bot):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="Infos",
            emoji="ℹ️",
            row=1
        )
        self.bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Statistiques
            total_commands = len([cmd for cmd in self.bot.walk_commands() if not cmd.hidden])
            total_guilds = len(self.bot.guilds)
            total_users = sum(guild.member_count for guild in self.bot.guilds)
            
            # Uptime
            uptime_text = "Inconnu"
            if hasattr(self.bot, 'uptime'):
                delta = datetime.utcnow() - self.bot.uptime
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)
                
                parts = []
                if days > 0:
                    parts.append(f"{days}j")
                if hours > 0:
                    parts.append(f"{hours}h")
                if minutes > 0:
                    parts.append(f"{minutes}m")
                uptime_text = " ".join(parts) if parts else "< 1m"
            
            embed = discord.Embed(
                title="ℹ️ Informations Détaillées",
                description=f"**{self.bot.user.name}** - Bot Discord Multifonctions",
                color=COLORS["info"],
                timestamp=datetime.utcnow()
            )
            
            # Stats principales
            embed.add_field(
                name="📊 Statistiques Globales",
                value=(
                    f"```yml\n"
                    f"Serveurs      : {total_guilds:,}\n"
                    f"Utilisateurs  : {total_users:,}\n"
                    f"Commandes     : {total_commands}\n"
                    f"Catégories    : {len([c for c in self.bot.cogs if c not in ['Help', 'ErrorHandler']])}\n"
                    f"```"
                ),
                inline=False
            )
            
            # Performance
            embed.add_field(
                name="⚡ Performance",
                value=(
                    f"```yml\n"
                    f"Latence       : {round(self.bot.latency * 1000)}ms\n"
                    f"Uptime        : {uptime_text}\n"
                    f"```"
                ),
                inline=False
            )
            
            # Liens utiles
            embed.add_field(
                name="🔗 Liens Utiles",
                value=(
                    f"• [Inviter le Bot](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)\n"
                    f"• [Serveur Support](https://discord.gg/k2MEdE5aGj)\n"
                ),
                inline=False
            )
            
            # Développeur
            embed.add_field(
                name="👨‍💻 Développeur",
                value="**zenox_94** • Créateur du bot",
                inline=False
            )
            
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(
                text=f"Demandé par {interaction.user.name} • Développé par zenox_94",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            print(f"❌ Erreur InfoButton: {e}")

class InviteButton(Button):
    """Bouton d'invitation"""
    def __init__(self, bot):
        super().__init__(
            style=discord.ButtonStyle.link,
            label="Inviter",
            emoji="➕",
            url=f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands",
            row=1
        )

class SupportButton(Button):
    """Bouton de support"""
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.link,
            label="Support",
            emoji="💬",
            url="https://discord.gg/k2MEdE5aGj",
            row=1
        )

# ═══════════════════════════════════════════════════════════════
# 📋 MENU DÉROULANT DES CATÉGORIES
# ═══════════════════════════════════════════════════════════════

class CategorySelect(Select):
    """Menu de sélection des catégories"""
    def __init__(self, bot):
        self.bot = bot
        
        # Cogs à masquer
        hidden = ["Help", "HelpCog", "ErrorHandler", "Errors"]
        
        options = []
        for cog_name in sorted(bot.cogs.keys()):
            if cog_name not in hidden:
                cog = bot.get_cog(cog_name)
                if cog:
                    cmds = [cmd for cmd in cog.get_commands() if not cmd.hidden]
                    if cmds:
                        options.append(
                            discord.SelectOption(
                                label=cog_name,
                                description=f"{len(cmds)} commandes • {CATEGORY_INFO.get(cog_name, {}).get('desc', 'Catégorie')[:50]}",
                                emoji=EMOJI_MAP.get(cog_name, "📁")
                            )
                        )
        
        super().__init__(
            placeholder="🔍 Sélectionne une catégorie pour voir ses commandes...",
            options=options[:25],  # Discord limite à 25 options
            row=0
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            cog_name = self.values[0]
            cog = self.bot.get_cog(cog_name)
            
            if not cog:
                return await interaction.followup.send("❌ Catégorie introuvable", ephemeral=True)
            
            # Récupère les commandes
            cmds = sorted([cmd for cmd in cog.get_commands() if not cmd.hidden], key=lambda x: x.name)
            
            # Couleur personnalisée
            color = CATEGORY_INFO.get(cog_name, {}).get("color", COLORS["primary"])
            
            embed = discord.Embed(
                title=f"{EMOJI_MAP.get(cog_name, '📁')} Catégorie : {cog_name}",
                description=f"*{CATEGORY_INFO.get(cog_name, {}).get('desc', 'Commandes disponibles')}*\n\n",
                color=color,
                timestamp=datetime.utcnow()
            )
            
            if cmds:
                # Grouper par 8 commandes par field pour éviter l'embed trop long
                for i in range(0, len(cmds), 8):
                    chunk = cmds[i:i+8]
                    
                    text = []
                    for cmd in chunk:
                        # Description courte
                        desc = (cmd.help or "Pas de description").split('\n')[0][:40]
                        
                        # Affichage avec emoji
                        text.append(f"**`+{cmd.name}`**\n└ {desc}")
                    
                    field_name = "📝 Commandes" if i == 0 else "\u200b"
                    embed.add_field(
                        name=field_name,
                        value="\n\n".join(text),
                        inline=False
                    )
                
                # Note d'utilisation
                embed.add_field(
                    name="💡 Astuce",
                    value=f"Utilise `+cmdinfo <commande>` pour plus de détails",
                    inline=False
                )
            else:
                embed.description += "⚠️ Aucune commande disponible dans cette catégorie."
            
            # Footer avec compteur
            embed.set_footer(
                text=f"{len(cmds)} commande(s) • Demandé par {interaction.user.name} • Dev: zenox_94",
                icon_url=interaction.user.display_avatar.url
            )
            
            view = CategoryView(self.bot)
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            print(f"❌ Erreur CategorySelect: {e}")
            await interaction.followup.send(f"❌ Une erreur est survenue", ephemeral=True)

# ═══════════════════════════════════════════════════════════════
# 🎨 VUES (VIEWS)
# ═══════════════════════════════════════════════════════════════

class MainHelpView(View):
    """Vue principale du menu d'aide"""
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(CategorySelect(bot))
        self.add_item(InfoButton(bot))
        self.add_item(InviteButton(bot))
        self.add_item(SupportButton())

class CategoryView(View):
    """Vue pour les catégories"""
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(CategorySelect(bot))
        self.add_item(HomeButton(bot))
        self.add_item(InfoButton(bot))
        self.add_item(InviteButton(bot))

# ═══════════════════════════════════════════════════════════════
# 🎨 CRÉATION DE L'EMBED PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def create_main_embed(bot, user):
    """Crée l'embed du menu principal"""
    
    # Statistiques
    hidden = ["Help", "HelpCog", "ErrorHandler", "Errors"]
    visible_cogs = [c for c in bot.cogs.keys() if c not in hidden]
    total_commands = len([cmd for cmd in bot.walk_commands() if not cmd.hidden])
    
    embed = discord.Embed(
        title="📚 Centre d'Aide Interactif",
        description=(
            f"### Bienvenue {user.mention} ! 👋\n\n"
            f"Explore toutes mes fonctionnalités grâce au menu ci-dessous.\n"
            f"Utilise le **menu déroulant** pour découvrir les différentes catégories."
        ),
        color=COLORS["primary"],
        timestamp=datetime.utcnow()
    )
    
    # Aperçu rapide
    embed.add_field(
        name="📊 Aperçu Rapide",
        value=(
            f"```yaml\n"
            f"Préfixe       : +\n"
            f"Catégories    : {len(visible_cogs)}\n"
            f"Commandes     : {total_commands}\n"
            f"Serveurs      : {len(bot.guilds)}\n"
            f"```"
        ),
        inline=False
    )
    
    # Liste des catégories avec emojis
    cat_list = []
    for cog_name in sorted(visible_cogs):
        cog = bot.get_cog(cog_name)
        if cog:
            cmd_count = len([cmd for cmd in cog.get_commands() if not cmd.hidden])
            if cmd_count > 0:
                emoji = EMOJI_MAP.get(cog_name, "📁")
                cat_list.append(f"{emoji} **{cog_name}** • `{cmd_count}` cmd")
    
    # Diviser en 2 colonnes
    mid = len(cat_list) // 2 + len(cat_list) % 2
    col1 = cat_list[:mid]
    col2 = cat_list[mid:]
    
    if col1:
        embed.add_field(
            name="🗂️ Catégories (Partie 1)",
            value="\n".join(col1),
            inline=True
        )
    
    if col2:
        embed.add_field(
            name="🗂️ Catégories (Partie 2)",
            value="\n".join(col2),
            inline=True
        )
    
    # Guide d'utilisation
    embed.add_field(
        name="🎯 Comment utiliser ce menu ?",
        value=(
            "**1️⃣** Utilise le menu déroulant pour choisir une catégorie\n"
            "**2️⃣** Consulte les commandes disponibles\n"
            "**3️⃣** Utilise `+cmdinfo <commande>` pour plus de détails\n"
        ),
        inline=False
    )
    
    # Info développeur
    embed.add_field(
        name="👨‍💻 Développeur",
        value="**zenox_94** • Créateur du bot",
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(
        text=f"Demandé par {user.name} • Développé par zenox_94",
        icon_url=user.display_avatar.url
    )
    
    return embed

# ═══════════════════════════════════════════════════════════════
# 🤖 COG PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class Help(commands.Cog):
    """Système d'aide interactif et moderne"""
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')  # Retire la commande help par défaut
    
    @commands.command(name="help", aliases=["h", "aide", "commands"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help_command(self, ctx):
        """📚 Affiche le menu d'aide interactif"""
        
        # Supprime le message de l'utilisateur pour plus de propreté
        try:
            await ctx.message.delete()
        except:
            pass
        
        embed = create_main_embed(self.bot, ctx.author)
        view = MainHelpView(self.bot)
        
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="cmdinfo", aliases=["commandinfo", "ci"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def command_info(self, ctx, *, command_name: str):
        """🔍 Affiche les détails d'une commande spécifique
        
        Exemple: +cmdinfo ban"""
        
        cmd = self.bot.get_command(command_name.lower())
        
        if not cmd or cmd.hidden:
            embed = discord.Embed(
                title="❌ Commande introuvable",
                description=f"La commande `{command_name}` n'existe pas ou est privée.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed, delete_after=8)
        
        # Couleur selon la catégorie
        color = COLORS["primary"]
        if cmd.cog_name:
            color = CATEGORY_INFO.get(cmd.cog_name, {}).get("color", COLORS["primary"])
        
        embed = discord.Embed(
            title=f"📖 Commande : {cmd.name}",
            description=cmd.help or "*Aucune description disponible*",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Usage
        usage = f"+{cmd.name}"
        if cmd.signature:
            usage += f" {cmd.signature}"
        
        embed.add_field(
            name="💻 Utilisation",
            value=f"```\n{usage}\n```",
            inline=False
        )
        
        # Alias
        if cmd.aliases:
            embed.add_field(
                name="🔄 Alias",
                value=", ".join([f"`{alias}`" for alias in cmd.aliases]),
                inline=True
            )
        
        # Catégorie
        if cmd.cog_name:
            emoji = EMOJI_MAP.get(cmd.cog_name, "📁")
            embed.add_field(
                name="📂 Catégorie",
                value=f"{emoji} {cmd.cog_name}",
                inline=True
            )
        
        # Cooldown
        if cmd._buckets and cmd._buckets._cooldown:
            cooldown = cmd._buckets._cooldown
            embed.add_field(
                name="⏱️ Cooldown",
                value=f"{cooldown.rate}x / {cooldown.per}s",
                inline=True
            )
        
        embed.set_footer(
            text=f"Demandé par {ctx.author.name} • Développé par zenox_94",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="categories", aliases=["cats", "cogs"])
    async def list_categories(self, ctx):
        """📋 Liste toutes les catégories disponibles"""
        
        hidden = ["Help", "HelpCog", "ErrorHandler", "Errors"]
        
        embed = discord.Embed(
            title="📋 Liste des Catégories",
            description="Voici toutes les catégories de commandes disponibles :\n",
            color=COLORS["primary"],
            timestamp=datetime.utcnow()
        )
        
        for cog_name in sorted(self.bot.cogs.keys()):
            if cog_name not in hidden:
                cog = self.bot.get_cog(cog_name)
                if cog:
                    cmds = [cmd for cmd in cog.get_commands() if not cmd.hidden]
                    if cmds:
                        emoji = EMOJI_MAP.get(cog_name, "📁")
                        desc = CATEGORY_INFO.get(cog_name, {}).get("desc", "Catégorie de commandes")
                        
                        embed.add_field(
                            name=f"{emoji} {cog_name}",
                            value=f"{desc}\n`{len(cmds)}` commandes",
                            inline=True
                        )
        
        embed.set_footer(
            text=f"Utilise +help pour le menu interactif • Dev: zenox_94",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════════════
# 🚀 SETUP
# ═══════════════════════════════════════════════════════════════

async def setup(bot):
    await bot.add_cog(Help(bot))
    print("✅ Cog Help chargé avec succès")