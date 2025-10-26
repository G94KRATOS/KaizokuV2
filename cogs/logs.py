import discord
from discord.ext import commands
from datetime import datetime
import json
import os
import asyncio

class Logger(commands.Cog):
    """Système de logs complet et automatique"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "logs_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_config(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.config:
            self.config[guild_id] = {
                "moderation": None,
                "messages": None,
                "members": None,
                "voice": None,
                "server": None,
                "roles": None,
                "invites": None,
                "giveaways": None,
                "boosts": None,
                "reactions": None
            }
            self.save_config()
        return self.config[guild_id]
    
    async def log(self, guild, log_type, embed):
        config = self.get_config(guild.id)
        channel_id = config.get(log_type)
        
        if channel_id:
            channel = guild.get_channel(int(channel_id))
            if channel:
                try:
                    await channel.send(embed=embed)
                except:
                    pass
    
    def create_embed(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Logger System")
        return embed
    
    # ==================== MODÉRATION ====================
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await asyncio.sleep(1)
        try:
            async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    embed = self.create_embed(
                        "🔨 Membre Banni",
                        f"**Utilisateur :** {user.mention} `{user}`\n"
                        f"**ID :** `{user.id}`\n"
                        f"**Modérateur :** {entry.user.mention}\n"
                        f"**Raison :** ```{entry.reason or 'Aucune raison'}```",
                        discord.Color.from_rgb(220, 53, 69)
                    )
                    if user.avatar:
                        embed.set_thumbnail(url=user.display_avatar.url)
                    await self.log(guild, "moderation", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await asyncio.sleep(1)
        try:
            async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    embed = self.create_embed(
                        "✅ Membre Débanni",
                        f"**Utilisateur :** {user.mention} `{user}`\n"
                        f"**Modérateur :** {entry.user.mention}",
                        discord.Color.from_rgb(40, 167, 69)
                    )
                    await self.log(guild, "moderation", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(1)
        
        # Vérifie si kick
        try:
            async for entry in member.guild.audit_logs(limit=3, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id and (datetime.utcnow() - entry.created_at).seconds < 5:
                    embed = self.create_embed(
                        "👢 Membre Expulsé",
                        f"**Utilisateur :** {member.mention} `{member}`\n"
                        f"**ID :** `{member.id}`\n"
                        f"**Modérateur :** {entry.user.mention}\n"
                        f"**Raison :** ```{entry.reason or 'Aucune raison'}```",
                        discord.Color.from_rgb(255, 193, 7)
                    )
                    await self.log(member.guild, "moderation", embed)
                    return
        except:
            pass
        
        # Départ normal
        roles = ", ".join([r.mention for r in member.roles[1:][:10]]) if len(member.roles) > 1 else "Aucun"
        
        embed = self.create_embed(
            "👋 Membre Parti",
            f"**Membre :** {member.mention} `{member}`\n"
            f"**ID :** `{member.id}`\n"
            f"**Rejoint le :** <t:{int(member.joined_at.timestamp())}:R>\n"
            f"**Rôles :** {roles}\n"
            f"**Membres restants :** `{member.guild.member_count}`",
            discord.Color.from_rgb(108, 117, 125)
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        await self.log(member.guild, "members", embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        account_age = datetime.utcnow() - member.created_at
        is_new = account_age.days < 7
        is_suspect = account_age.days < 1
        
        desc = (
            f"**Membre :** {member.mention} `{member}`\n"
            f"**ID :** `{member.id}`\n"
            f"**Compte créé :** <t:{int(member.created_at.timestamp())}:R> ({account_age.days}j)\n"
            f"**Total membres :** `{member.guild.member_count}`"
        )
        
        if is_suspect:
            desc += f"\n🚨 **ALERTE : Compte très récent !**"
        elif is_new:
            desc += f"\n⚠️ **Attention : Compte récent**"
        
        color = discord.Color.from_rgb(220, 53, 69) if is_suspect else (
            discord.Color.from_rgb(255, 193, 7) if is_new else discord.Color.from_rgb(40, 167, 69)
        )
        
        embed = self.create_embed("👋 Nouveau Membre", desc, color)
        
        if member.avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        await self.log(member.guild, "members", embed)
    
    # ==================== MESSAGES ====================
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        
        content = message.content[:800] if message.content else "*[Vide ou média]*"
        
        desc = (
            f"**Auteur :** {message.author.mention} `{message.author}`\n"
            f"**Salon :** {message.channel.mention}\n"
            f"**ID Message :** `{message.id}`\n"
            f"**Contenu :** ```{content}```"
        )
        
        if message.attachments:
            files = ", ".join([a.filename for a in message.attachments[:5]])
            desc += f"\n**📎 Fichiers :** `{files}`"
        
        if message.embeds:
            desc += f"\n**📊 Embeds :** `{len(message.embeds)}`"
        
        embed = self.create_embed("🗑️ Message Supprimé", desc, discord.Color.from_rgb(220, 53, 69))
        
        await self.log(message.guild, "messages", embed)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages or not messages[0].guild:
            return
        
        guild = messages[0].guild
        channel = messages[0].channel
        
        embed = self.create_embed(
            "🗑️ Suppression en Masse",
            f"**Salon :** {channel.mention}\n"
            f"**Messages supprimés :** `{len(messages)}`\n"
            f"**Auteurs concernés :** `{len(set(m.author for m in messages))}`",
            discord.Color.from_rgb(220, 53, 69)
        )
        
        await self.log(guild, "messages", embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        
        embed = self.create_embed(
            "✏️ Message Modifié",
            f"**Auteur :** {before.author.mention}\n"
            f"**Salon :** {before.channel.mention}\n\n"
            f"**Avant :** ```{before.content[:300]}```\n"
            f"**Après :** ```{after.content[:300]}```\n"
            f"[Aller au message]({after.jump_url})",
            discord.Color.from_rgb(255, 193, 7)
        )
        
        await self.log(before.guild, "messages", embed)
    
    # ==================== RÔLES ====================
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return
        
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)
        
        if added:
            roles_list = ", ".join([r.mention for r in added])
            embed = self.create_embed(
                "➕ Rôle(s) Ajouté(s)",
                f"**Membre :** {after.mention}\n"
                f"**Rôle(s) :** {roles_list}\n"
                f"**Total rôles :** `{len(after.roles) - 1}`",
                discord.Color.from_rgb(40, 167, 69)
            )
            await self.log(after.guild, "roles", embed)
        
        if removed:
            roles_list = ", ".join([r.mention for r in removed])
            embed = self.create_embed(
                "➖ Rôle(s) Retiré(s)",
                f"**Membre :** {after.mention}\n"
                f"**Rôle(s) :** {roles_list}\n"
                f"**Total rôles :** `{len(after.roles) - 1}`",
                discord.Color.from_rgb(220, 53, 69)
            )
            await self.log(after.guild, "roles", embed)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await asyncio.sleep(1)
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    embed = self.create_embed(
                        "🎭 Rôle Créé",
                        f"**Rôle :** {role.mention}\n"
                        f"**Nom :** `{role.name}`\n"
                        f"**Couleur :** `{role.color}`\n"
                        f"**Créé par :** {entry.user.mention}",
                        discord.Color.from_rgb(40, 167, 69)
                    )
                    await self.log(role.guild, "roles", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await asyncio.sleep(1)
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    embed = self.create_embed(
                        "🎭 Rôle Supprimé",
                        f"**Nom :** `{role.name}`\n"
                        f"**Supprimé par :** {entry.user.mention}",
                        discord.Color.from_rgb(220, 53, 69)
                    )
                    await self.log(role.guild, "roles", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.name == after.name and before.color == after.color and before.permissions == after.permissions:
            return
        
        changes = []
        if before.name != after.name:
            changes.append(f"**Nom :** `{before.name}` → `{after.name}`")
        if before.color != after.color:
            changes.append(f"**Couleur :** `{before.color}` → `{after.color}`")
        if before.permissions != after.permissions:
            changes.append(f"**Permissions modifiées**")
        
        if changes:
            embed = self.create_embed(
                "🎭 Rôle Modifié",
                f"**Rôle :** {after.mention}\n" + "\n".join(changes),
                discord.Color.from_rgb(255, 193, 7)
            )
            await self.log(after.guild, "roles", embed)
    
    # ==================== VOCAL ====================
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Connexion
        if before.channel is None and after.channel:
            embed = self.create_embed(
                "🔊 Connexion Vocale",
                f"**Membre :** {member.mention}\n"
                f"**Salon :** {after.channel.mention}\n"
                f"**Membres dans le salon :** `{len(after.channel.members)}`",
                discord.Color.from_rgb(40, 167, 69)
            )
            await self.log(member.guild, "voice", embed)
        
        # Déconnexion
        elif before.channel and after.channel is None:
            embed = self.create_embed(
                "🔇 Déconnexion Vocale",
                f"**Membre :** {member.mention}\n"
                f"**Salon :** {before.channel.mention}",
                discord.Color.from_rgb(220, 53, 69)
            )
            await self.log(member.guild, "voice", embed)
        
        # Déplacement
        elif before.channel != after.channel and before.channel and after.channel:
            embed = self.create_embed(
                "↔️ Déplacement Vocal",
                f"**Membre :** {member.mention}\n"
                f"{before.channel.mention} → {after.channel.mention}",
                discord.Color.from_rgb(0, 123, 255)
            )
            await self.log(member.guild, "voice", embed)
    
    # ==================== SERVEUR ====================
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await asyncio.sleep(1)
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    embed = self.create_embed(
                        "➕ Salon Créé",
                        f"**Nom :** {channel.mention}\n"
                        f"**Type :** `{channel.type}`\n"
                        f"**Créé par :** {entry.user.mention}",
                        discord.Color.from_rgb(40, 167, 69)
                    )
                    await self.log(channel.guild, "server", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await asyncio.sleep(1)
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    embed = self.create_embed(
                        "➖ Salon Supprimé",
                        f"**Nom :** `{channel.name}`\n"
                        f"**Type :** `{channel.type}`\n"
                        f"**Supprimé par :** {entry.user.mention}",
                        discord.Color.from_rgb(220, 53, 69)
                    )
                    await self.log(channel.guild, "server", embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        changes = []
        
        if before.name != after.name:
            changes.append(f"**Nom :** `{before.name}` → `{after.name}`")
        if before.icon != after.icon:
            changes.append(f"**Icône modifiée**")
        if before.banner != after.banner:
            changes.append(f"**Bannière modifiée**")
        if before.verification_level != after.verification_level:
            changes.append(f"**Niveau de vérification :** `{before.verification_level}` → `{after.verification_level}`")
        
        if changes:
            embed = self.create_embed(
                "⚙️ Serveur Modifié",
                "\n".join(changes),
                discord.Color.from_rgb(0, 123, 255)
            )
            await self.log(after, "server", embed)
    
    # ==================== BOOSTS ====================
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Détecte les boosts
        if before.premium_since is None and after.premium_since is not None:
            embed = self.create_embed(
                "💎 Nouveau Boost !",
                f"**Membre :** {after.mention}\n"
                f"**Niveau serveur :** `Niveau {after.guild.premium_tier}`\n"
                f"**Boosts totaux :** `{after.guild.premium_subscription_count}`",
                discord.Color.from_rgb(255, 115, 250)
            )
            await self.log(after.guild, "boosts", embed)
        
        # Perte de boost
        elif before.premium_since is not None and after.premium_since is None:
            embed = self.create_embed(
                "💔 Boost Retiré",
                f"**Membre :** {after.mention}\n"
                f"**Niveau serveur :** `Niveau {after.guild.premium_tier}`\n"
                f"**Boosts restants :** `{after.guild.premium_subscription_count}`",
                discord.Color.from_rgb(108, 117, 125)
            )
            await self.log(after.guild, "boosts", embed)
    
    # ==================== RÉACTIONS ====================
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member and payload.member.bot:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
            member = payload.member
            
            embed = self.create_embed(
                "➕ Réaction Ajoutée",
                f"**Membre :** {member.mention}\n"
                f"**Salon :** {channel.mention}\n"
                f"**Emoji :** {payload.emoji}\n"
                f"[Aller au message]({message.jump_url})",
                discord.Color.from_rgb(40, 167, 69)
            )
            await self.log(guild, "reactions", embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        channel = guild.get_channel(payload.channel_id)
        member = guild.get_member(payload.user_id)
        
        if not channel or not member or member.bot:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
            
            embed = self.create_embed(
                "➖ Réaction Retirée",
                f"**Membre :** {member.mention}\n"
                f"**Salon :** {channel.mention}\n"
                f"**Emoji :** {payload.emoji}\n"
                f"[Aller au message]({message.jump_url})",
                discord.Color.from_rgb(220, 53, 69)
            )
            await self.log(guild, "reactions", embed)
        except:
            pass
    
    # ==================== INVITATIONS ====================
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        embed = self.create_embed(
            "📨 Invitation Créée",
            f"**Code :** `{invite.code}`\n"
            f"**Créateur :** {invite.inviter.mention}\n"
            f"**Salon :** {invite.channel.mention}\n"
            f"**Expiration :** {f'<t:{int((datetime.utcnow().timestamp() + invite.max_age))}:R>' if invite.max_age else 'Jamais'}\n"
            f"**Utilisations max :** `{invite.max_uses or 'Illimité'}`",
            discord.Color.from_rgb(40, 167, 69)
        )
        await self.log(invite.guild, "invites", embed)
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        embed = self.create_embed(
            "🗑️ Invitation Supprimée",
            f"**Code :** `{invite.code}`\n"
            f"**Salon :** {invite.channel.mention if invite.channel else 'Inconnu'}",
            discord.Color.from_rgb(220, 53, 69)
        )
        await self.log(invite.guild, "invites", embed)
    
    # ==================== COMMANDES ====================
    
    @commands.command(name="logsetup")
    @commands.has_permissions(administrator=True)
    async def logsetup(self, ctx):
        """Crée automatiquement la catégorie et tous les salons de logs"""
        
        await ctx.send("🔄 **Création de la structure de logs...**")
        
        # Cherche si la catégorie existe déjà
        category = discord.utils.get(ctx.guild.categories, name="📊 LOGS")
        
        if not category:
            try:
                category = await ctx.guild.create_category(
                    name="📊 LOGS",
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    }
                )
            except Exception as e:
                return await ctx.send(f"❌ Erreur lors de la création de la catégorie : {e}")
        
        # Définition des salons à créer
        channels_to_create = {
            "moderation": "🔨・modération",
            "messages": "💬・messages",
            "members": "👥・membres",
            "voice": "🔊・vocal",
            "server": "⚙️・serveur",
            "roles": "🎭・rôles",
            "invites": "📨・invitations",
            "giveaways": "🎉・giveaways",
            "boosts": "💎・boosts",
            "reactions": "⭐・réactions"
        }
        
        config = self.get_config(ctx.guild.id)
        created = 0
        updated = 0
        
        for log_type, channel_name in channels_to_create.items():
            # Vérifie si le salon existe déjà
            existing_channel = discord.utils.get(category.channels, name=channel_name)
            
            if existing_channel:
                config[log_type] = existing_channel.id
                updated += 1
            else:
                try:
                    new_channel = await ctx.guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        topic=f"Logs de type {log_type}"
                    )
                    config[log_type] = new_channel.id
                    created += 1
                except:
                    pass
        
        self.save_config()
        
        # Embed de confirmation
        embed = discord.Embed(
            title="✅ Configuration Terminée !",
            description=f"**Catégorie :** {category.mention}\n\n"
                       f"✨ **{created}** salon(s) créé(s)\n"
                       f"🔄 **{updated}** salon(s) déjà existant(s)\n"
                       f"📊 **{created + updated}** salon(s) configuré(s)",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        
        # Liste des salons configurés
        channels_list = []
        for log_type, channel_id in config.items():
            if channel_id:
                channel = ctx.guild.get_channel(int(channel_id))
                if channel:
                    channels_list.append(f"✅ {channel.mention}")
        
        if channels_list:
            embed.add_field(
                name="📋 Salons Configurés",
                value="\n".join(channels_list[:10]),
                inline=False
            )
        
        embed.set_footer(text="Utilisez 'logs view' pour voir la configuration")
        
        await ctx.send(embed=embed)
    
    @commands.group(name="logs", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx):
        """Menu principal des logs"""
        embed = discord.Embed(
            title="📊 Système de Logs Complet",
            description="Système de logs automatique et complet pour votre serveur",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        embed.add_field(
            name="⚙️ Commandes",
            value=(
                "`logsetup` • Créer automatiquement tous les salons\n"
                "`logs set <type> <#salon>` • Définir un salon\n"
                "`logs remove <type>` • Retirer un type\n"
                "`logs view` • Voir la configuration\n"
                "`logs test` • Tester les logs\n"
                "`logs clear` • Tout réinitialiser"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Types de Logs",
            value=(
                "`moderation` • Bans, kicks, sanctions\n"
                "`messages` • Messages supprimés/modifiés\n"
                "`members` • Arrivées/départs\n"
                "`voice` • Activité vocale\n"
                "`server` • Modifications serveur\n"
                "`roles` • Gestion des rôles\n"
                "`invites` • Invitations\n"
                "`giveaways` • Giveaways\n"
                "`boosts` • Boosts serveur\n"
                "`reactions` • Réactions"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Serveur : {ctx.guild.name}")
        await ctx.send(embed=embed)
    
    @logs.command(name="set")
    @commands.has_permissions(administrator=True)
    async def logs_set(self, ctx, log_type: str, channel: discord.TextChannel):
        """Configure un type de log"""
        config = self.get_config(ctx.guild.id)
        
        if log_type not in config:
            types = "`, `".join(config.keys())
            return await ctx.send(f"❌ Type invalide ! Types : `{types}`")
        
        config[log_type] = channel.id
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Configuration Enregistrée",
            description=f"**Type :** `{log_type}`\n**Salon :** {channel.mention}",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        await ctx.send(embed=embed)
    
    @logs.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def logs_remove(self, ctx, log_type: str):
        """Retire un type de log"""
        config = self.get_config(ctx.guild.id)
        
        if log_type not in config:
            return await ctx.send("❌ Type invalide !")
        
        config[log_type] = None
        self.save_config()
        
        embed = discord.Embed(
            title="🗑️ Configuration Supprimée",
            description=f"Les logs **{log_type}** ont été désactivés",
            color=discord.Color.from_rgb(220, 53, 69)
        )
        await ctx.send(embed=embed)
    
    @logs.command(name="view")
    @commands.has_permissions(administrator=True)
    async def logs_view(self, ctx):
        """Affiche la configuration actuelle"""
        config = self.get_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="📋 Configuration Actuelle",
            description=f"Serveur : **{ctx.guild.name}**",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        emojis = {
            "moderation": "🔨",
            "messages": "💬",
            "members": "👥",
            "voice": "🔊",
            "server": "⚙️",
            "roles": "🎭",
            "invites": "📨",
            "giveaways": "🎉",
            "boosts": "💎",
            "reactions": "⭐"
        }
        
        configured = 0
        for log_type, channel_id in config.items():
            emoji = emojis.get(log_type, "📌")
            
            if channel_id:
                channel = ctx.guild.get_channel(int(channel_id))
                if channel:
                    value = f"✅ {channel.mention}"
                    configured += 1
                else:
                    value = "❌ Salon introuvable"
            else:
                value = "⚪ Non configuré"
            
            embed.add_field(
                name=f"{emoji} {log_type.title()}",
                value=value,
                inline=True
            )
        
        embed.description += f"\n\n**Configurés :** `{configured}/{len(config)}`"
        
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
    
    @logs.command(name="test")
    @commands.has_permissions(administrator=True)
    async def logs_test(self, ctx):
        """Envoie un message test dans tous les salons configurés"""
        config = self.get_config(ctx.guild.id)
        
        test_embed = discord.Embed(
            title="🧪 Message Test",
            description="Si vous voyez ce message, les logs fonctionnent correctement !",
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        test_embed.set_footer(text=f"Demandé par {ctx.author}")
        
        sent = 0
        failed = []
        
        for log_type, channel_id in config.items():
            if channel_id:
                channel = ctx.guild.get_channel(int(channel_id))
                if channel:
                    try:
                        await channel.send(embed=test_embed)
                        sent += 1
                    except:
                        failed.append(log_type)
        
        embed = discord.Embed(
            title="✅ Test Terminé",
            description=f"**Envoyés :** `{sent}` salon(s)\n"
                       f"**Échecs :** `{len(failed)}` salon(s)",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        
        if failed:
            embed.add_field(
                name="❌ Échecs",
                value=", ".join([f"`{f}`" for f in failed]),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @logs.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def logs_clear(self, ctx):
        """Réinitialise toute la configuration"""
        config = self.get_config(ctx.guild.id)
        
        for key in config:
            config[key] = None
        
        self.save_config()
        
        embed = discord.Embed(
            title="🗑️ Configuration Réinitialisée",
            description="Tous les logs ont été désactivés",
            color=discord.Color.from_rgb(220, 53, 69)
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logger(bot))
    print("✅ Logger complet chargé avec succès !")