import discord
from discord.ext import commands
import json
import os

class PermissionsSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.perms_file = "permissions.json"
        self.permissions = self.load_permissions()
        
        # Hiérarchie des niveaux (plus le niveau est haut, plus il a de permissions)
        self.hierarchy = {
            0: "Membre",
            1: "Support",
            2: "Modérateur",
            3: "GS (Gestion)",
            4: "Administrateur",
            5: "Owner Bot"
        }
        
        # Permissions requises par commande
        self.command_levels = {
            # Support (niveau 1) - Info uniquement
            "warn": 1,
            "warns": 1,
            "memberinfo": 1,
            "mi": 1,
            "whois": 1,
            
            # Modérateur (niveau 2) - Modération basique
            "kick": 2,
            "mute": 2,
            "unmute": 2,
            "timeout": 2,
            "untimeout": 2,
            "clear": 2,
            "purge": 2,
            "lock": 2,
            "unlock": 2,
            "slowmode": 2,
            
            # GS (niveau 3) - Gestion complète SAUF commandes admin
            "ban": 3,
            "unban": 3,
            "addrole": 3,
            "removerole": 3,
            "nick": 3,
            "clearwarns": 3,
            "removewarn": 3,
            
            # Administrateur (niveau 4) - Gestion des permissions
            "addmod": 4,
            "removemod": 4,
            "addsupport": 4,
            "removesupport": 4,
            "setrole": 4,
            "delrole": 4,
            
            # Owner Bot (niveau 5) - Contrôle total
            "addgs": 5,
            "removegs": 5,
            "addadmin": 5,
            "removeadmin": 5,
            "addowner": 5,
            "removeowner": 5,
        }
    
    def load_permissions(self):
        if os.path.exists(self.perms_file):
            with open(self.perms_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_permissions(self):
        with open(self.perms_file, 'w', encoding='utf-8') as f:
            json.dump(self.permissions, indent=4, fp=f, ensure_ascii=False)
    
    def get_guild_perms(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.permissions:
            self.permissions[guild_id] = {
                "owners": [],
                "admins": [],
                "gs_users": [],
                "moderators": [],
                "supports": [],
                "roles": {}
            }
            self.save_permissions()
        return self.permissions[guild_id]
    
    def get_user_level(self, member):
        """Détermine le niveau de permission d'un membre"""
        guild_perms = self.get_guild_perms(member.guild.id)
        
        # Owner Bot (niveau 5)
        if member.id in guild_perms.get("owners", []):
            return 5
        
        # Propriétaire du serveur = Owner Bot
        if member.id == member.guild.owner_id:
            return 5
        
        # Administrateur (niveau 4)
        if member.id in guild_perms.get("admins", []):
            return 4
        
        # Admin Discord = Admin bot
        if member.guild_permissions.administrator:
            return 4
        
        # GS (niveau 3) - Gestion complète SAUF admin
        if member.id in guild_perms.get("gs_users", []):
            return 3
        
        # Modérateur (niveau 2)
        if member.id in guild_perms.get("moderators", []):
            return 2
        
        # Support (niveau 1)
        if member.id in guild_perms.get("supports", []):
            return 1
        
        # Vérifie les rôles configurés
        max_level = 0
        for role in member.roles:
            role_id = str(role.id)
            if role_id in guild_perms.get("roles", {}):
                level = guild_perms["roles"][role_id]
                max_level = max(max_level, level)
        
        return max_level
    
    def can_use_command(self, member, command_name):
        """Vérifie si un membre peut utiliser une commande"""
        user_level = self.get_user_level(member)
        required_level = self.command_levels.get(command_name, 0)
        return user_level >= required_level
    
    def can_moderate_target(self, moderator: discord.Member, target: discord.Member):
        """Vérifie la hiérarchie pour les sanctions"""
        if target == moderator:
            return False, "Tu ne peux pas te sanctionner toi-même !"
        
        if target.guild.owner == target:
            return False, "Tu ne peux pas sanctionner le propriétaire du serveur !"
        
        mod_level = self.get_user_level(moderator)
        target_level = self.get_user_level(target)
        
        if target_level >= mod_level:
            return False, f"Tu ne peux pas sanctionner quelqu'un de niveau {self.hierarchy[target_level]} (tu es {self.hierarchy[mod_level]}) !"
        
        # Owner Bot peut tout faire
        if mod_level == 5:
            return True, None
        
        # Vérifie aussi la hiérarchie Discord
        if target.top_role >= moderator.top_role and mod_level < 5:
            return False, "Tu ne peux pas sanctionner quelqu'un avec un rôle Discord égal ou supérieur !"
        
        return True, None
    
    # ==================== COMMANDES OWNER BOT ====================
    
    @commands.command(name="addowner")
    @commands.is_owner()
    async def add_owner(self, ctx, user: discord.User):
        """Ajoute un Owner Bot (niveau 5)"""
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id in guild_perms["owners"]:
            return await ctx.send(f"❌ {user.mention} est déjà Owner Bot.")
        
        guild_perms["owners"].append(user.id)
        self.save_permissions()
        
        embed = discord.Embed(
            title="👑 Owner Bot ajouté",
            description=f"{user.mention} → **Owner Bot (Niveau 5)**",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="✅ Accès",
            value="• Contrôle total du bot\n• Toutes les commandes\n• Bypass des permissions Discord",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removeowner")
    @commands.is_owner()
    async def remove_owner(self, ctx, user: discord.User):
        """Retire un Owner Bot"""
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id not in guild_perms["owners"]:
            return await ctx.send(f"❌ {user.mention} n'est pas Owner Bot.")
        
        guild_perms["owners"].remove(user.id)
        self.save_permissions()
        await ctx.send(f"✅ {user.mention} n'est plus **Owner Bot**.")
    
    # ==================== COMMANDES ADMINISTRATEUR ====================
    
    @commands.command(name="addadmin")
    async def add_admin(self, ctx, user: discord.User):
        """Ajoute un Administrateur (niveau 4)"""
        if self.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Seuls les **Owner Bot** peuvent attribuer le niveau Administrateur.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id in guild_perms["admins"]:
            return await ctx.send(f"❌ {user.mention} est déjà Administrateur.")
        
        guild_perms["admins"].append(user.id)
        self.save_permissions()
        
        embed = discord.Embed(
            title="🔴 Administrateur ajouté",
            description=f"{user.mention} → **Administrateur (Niveau 4)**",
            color=discord.Color.red()
        )
        embed.add_field(
            name="✅ Accès",
            value="• Gestion des Mods/Supports\n• Configuration des rôles\n• Bypass des permissions Discord",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removeadmin")
    async def remove_admin(self, ctx, user: discord.User):
        """Retire le niveau Administrateur"""
        if self.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Seuls les **Owner Bot** peuvent retirer le niveau Administrateur.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id not in guild_perms["admins"]:
            return await ctx.send(f"❌ {user.mention} n'est pas Administrateur.")
        
        guild_perms["admins"].remove(user.id)
        self.save_permissions()
        await ctx.send(f"✅ {user.mention} n'est plus **Administrateur**.")
    
    # ==================== COMMANDES GS ====================
    
    @commands.command(name="addgs")
    async def add_gs(self, ctx, user: discord.User):
        """Ajoute un GS (niveau 3)"""
        if self.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Seuls les **Owner Bot** peuvent attribuer le niveau GS.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id in guild_perms["gs_users"]:
            return await ctx.send(f"❌ {user.mention} a déjà le niveau GS.")
        
        guild_perms["gs_users"].append(user.id)
        self.save_permissions()
        
        embed = discord.Embed(
            title="🔵 GS (Gestion) ajouté",
            description=f"{user.mention} → **GS - Gestion (Niveau 3)**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="✅ Accès",
            value="• Ban/Unban\n• Gestion rôles/salons\n• Tout SAUF commandes admin\n• Bypass des permissions Discord",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removegs")
    async def remove_gs(self, ctx, user: discord.User):
        """Retire le niveau GS"""
        if self.get_user_level(ctx.author) < 5:
            return await ctx.send("❌ Seuls les **Owner Bot** peuvent retirer le niveau GS.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id not in guild_perms["gs_users"]:
            return await ctx.send(f"❌ {user.mention} n'a pas le niveau GS.")
        
        guild_perms["gs_users"].remove(user.id)
        self.save_permissions()
        await ctx.send(f"✅ {user.mention} n'a plus le niveau **GS**.")
    
    # ==================== COMMANDES MODÉRATEUR ====================
    
    @commands.command(name="addmod")
    async def add_mod(self, ctx, user: discord.User):
        """Ajoute un Modérateur (niveau 2)"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent attribuer le niveau Modérateur.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id in guild_perms["moderators"]:
            return await ctx.send(f"❌ {user.mention} est déjà Modérateur.")
        
        guild_perms["moderators"].append(user.id)
        self.save_permissions()
        
        embed = discord.Embed(
            title="🟠 Modérateur ajouté",
            description=f"{user.mention} → **Modérateur (Niveau 2)**",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="✅ Accès",
            value="• Kick/Mute/Timeout\n• Clear/Lock/Slowmode\n• Bypass des permissions Discord",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removemod")
    async def remove_mod(self, ctx, user: discord.User):
        """Retire le niveau Modérateur"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent retirer le niveau Modérateur.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id not in guild_perms["moderators"]:
            return await ctx.send(f"❌ {user.mention} n'est pas Modérateur.")
        
        guild_perms["moderators"].remove(user.id)
        self.save_permissions()
        await ctx.send(f"✅ {user.mention} n'est plus **Modérateur**.")
    
    # ==================== COMMANDES SUPPORT ====================
    
    @commands.command(name="addsupport")
    async def add_support(self, ctx, user: discord.User):
        """Ajoute un Support (niveau 1)"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent attribuer le niveau Support.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id in guild_perms["supports"]:
            return await ctx.send(f"❌ {user.mention} est déjà Support.")
        
        guild_perms["supports"].append(user.id)
        self.save_permissions()
        
        embed = discord.Embed(
            title="🟢 Support ajouté",
            description=f"{user.mention} → **Support (Niveau 1)**",
            color=discord.Color.green()
        )
        embed.add_field(
            name="✅ Accès",
            value="• Warn/Warns\n• Memberinfo\n• Commandes d'information",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removesupport")
    async def remove_support(self, ctx, user: discord.User):
        """Retire le niveau Support"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent retirer le niveau Support.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        
        if user.id not in guild_perms["supports"]:
            return await ctx.send(f"❌ {user.mention} n'est pas Support.")
        
        guild_perms["supports"].remove(user.id)
        self.save_permissions()
        await ctx.send(f"✅ {user.mention} n'est plus **Support**.")
    
    # ==================== GESTION DES RÔLES ====================
    
    @commands.command(name="setrole")
    async def set_role(self, ctx, role: discord.Role, level: int):
        """Définit le niveau d'un rôle Discord (0-4)"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent configurer les rôles.")
        
        if level not in self.hierarchy or level >= 5:
            levels_text = "\n".join([f"**{lvl}** - {name}" for lvl, name in self.hierarchy.items() if lvl < 5])
            return await ctx.send(f"❌ Niveau invalide. Niveaux disponibles:\n{levels_text}")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        guild_perms["roles"][str(role.id)] = level
        self.save_permissions()
        
        embed = discord.Embed(
            title="✅ Rôle configuré",
            description=f"{role.mention} → **{self.hierarchy[level]}** (niveau {level})",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="delrole")
    async def remove_role_perm(self, ctx, role: discord.Role):
        """Retire un rôle de la configuration"""
        if self.get_user_level(ctx.author) < 4:
            return await ctx.send("❌ Seuls les **Administrateurs** peuvent configurer les rôles.")
        
        guild_perms = self.get_guild_perms(ctx.guild.id)
        role_id = str(role.id)
        
        if role_id not in guild_perms.get("roles", {}):
            return await ctx.send(f"❌ {role.mention} n'a pas de niveau configuré.")
        
        del guild_perms["roles"][role_id]
        self.save_permissions()
        await ctx.send(f"✅ {role.mention} n'a plus de niveau de permission.")
    
    # ==================== AFFICHAGE ====================
    
    @commands.command(name="permissions", aliases=["perms"])
    async def show_permissions(self, ctx, member: discord.Member = None):
        """Affiche les permissions d'un membre"""
        if member:
            level = self.get_user_level(member)
            
            embed = discord.Embed(
                title=f"🔐 Permissions de {member.display_name}",
                description=f"**{self.hierarchy[level]}** (niveau {level})",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            guild_perms = self.get_guild_perms(ctx.guild.id)
            
            if member.id in guild_perms.get("owners", []):
                embed.add_field(name="👑 Owner Bot", value="Contrôle total", inline=False)
            elif member.id in guild_perms.get("admins", []):
                embed.add_field(name="🔴 Administrateur", value="Gestion des permissions", inline=False)
            elif member.id in guild_perms.get("gs_users", []):
                embed.add_field(name="🔵 GS", value="Gestion complète sauf admin", inline=False)
            elif member.id in guild_perms.get("moderators", []):
                embed.add_field(name="🟠 Modérateur", value="Modération standard", inline=False)
            elif member.id in guild_perms.get("supports", []):
                embed.add_field(name="🟢 Support", value="Commandes de base", inline=False)
            
            embed.add_field(
                name="✅ Bypass Discord",
                value="Pas besoin de permissions Discord natives",
                inline=False
            )
        else:
            guild_perms = self.get_guild_perms(ctx.guild.id)
            
            embed = discord.Embed(
                title="🔐 Configuration des permissions",
                description=f"Serveur: **{ctx.guild.name}**",
                color=discord.Color.blue()
            )
            
            # Affichage des membres par niveau
            for key, emoji, name in [
                ("owners", "👑", "Owners (5)"),
                ("admins", "🔴", "Administrateurs (4)"),
                ("gs_users", "🔵", "GS (3)"),
                ("moderators", "🟠", "Modérateurs (2)"),
                ("supports", "🟢", "Supports (1)")
            ]:
                if guild_perms.get(key):
                    users = [f"<@{uid}>" for uid in guild_perms[key]]
                    embed.add_field(name=f"{emoji} {name}", value="\n".join(users), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="mylevel")
    async def my_level(self, ctx):
        """Affiche votre niveau de permission"""
        level = self.get_user_level(ctx.author)
        
        embed = discord.Embed(
            title="🔐 Votre niveau",
            description=f"**{self.hierarchy[level]}** (niveau {level})",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        available_cmds = [cmd for cmd, req_level in self.command_levels.items() if req_level <= level]
        embed.add_field(
            name="📊 Statistiques",
            value=f"**{len(available_cmds)}** commandes disponibles",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # ==================== CHECK AUTOMATIQUE ====================
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Vérifie les permissions avant chaque commande"""
        if ctx.command.cog == self:
            return
        
        if not self.can_use_command(ctx.author, ctx.command.name):
            user_level = self.get_user_level(ctx.author)
            required_level = self.command_levels.get(ctx.command.name, 0)
            
            embed = discord.Embed(
                title="❌ Permission refusée",
                description=f"Cette commande nécessite le niveau **{self.hierarchy[required_level]}** minimum.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Votre niveau actuel",
                value=f"**{self.hierarchy[user_level]}**"
            )
            await ctx.send(embed=embed, delete_after=10)
            raise commands.CommandError("Permission insuffisante")

async def setup(bot):
    await bot.add_cog(PermissionsSystem(bot))