import discord
from discord.ext import commands
from datetime import datetime
import asyncio

class ServerLogger(commands.Cog):
    """Log ultra-détaillé des serveurs rejoints et quittés"""
    
    def __init__(self, bot):
        self.bot = bot
        # ⚠️ IMPORTANT : Remplace ces IDs par les IDs de tes salons de logs
        self.log_channel_id = 1431718741007142952  # Logs serveurs rejoints/quittés
        self.mod_log_channel_id = 1431785521163800739  # Logs actions de modération (à configurer)

    async def get_server_info(self, guild):
        """Récupère toutes les infos détaillées du serveur"""
        info = {
            "name": guild.name,
            "id": guild.id,
            "owner": guild.owner,
            "owner_id": guild.owner_id,
            "created_at": guild.created_at,
            "member_count": guild.member_count,
            "icon": guild.icon.url if guild.icon else None,
            "banner": guild.banner.url if guild.banner else None,
            "description": guild.description or "Aucune description",
            "verification_level": str(guild.verification_level).replace("_", " ").title(),
            "boost_level": guild.premium_tier,
            "boost_count": guild.premium_subscription_count or 0,
            "features": guild.features,
            "text_channels": len(guild.text_channels),
            "voice_channels": len(guild.voice_channels),
            "categories": len(guild.categories),
            "roles_count": len(guild.roles),
            "emojis_count": len(guild.emojis),
            "stickers_count": len(guild.stickers),
        }
        
        # Compte les membres
        try:
            bots = sum(1 for m in guild.members if m.bot)
            humans = info["member_count"] - bots
            info["bots"] = bots
            info["humans"] = humans
            
            # Statuts des membres
            online = sum(1 for m in guild.members if m.status == discord.Status.online)
            idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
            dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
            offline = sum(1 for m in guild.members if m.status == discord.Status.offline)
            
            info["online"] = online
            info["idle"] = idle
            info["dnd"] = dnd
            info["offline"] = offline
        except:
            info["bots"] = 0
            info["humans"] = info["member_count"]
            info["online"] = 0
            info["idle"] = 0
            info["dnd"] = 0
            info["offline"] = 0
        
        # Invitations
        try:
            invites = await guild.invites()
            info["invite_count"] = len(invites)
        except:
            info["invite_count"] = 0
        
        # Webhooks
        try:
            webhooks = await guild.webhooks()
            info["webhook_count"] = len(webhooks)
        except:
            info["webhook_count"] = 0
        
        # Bannissements
        try:
            bans = [ban async for ban in guild.bans()]
            info["ban_count"] = len(bans)
        except:
            info["ban_count"] = 0
        
        return info

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Quand le bot rejoint un serveur"""
        log_channel = self.bot.get_channel(self.log_channel_id)
        
        if not log_channel:
            print(f"⚠️ Salon de log introuvable (ID: {self.log_channel_id})")
            return
        
        # Récupère toutes les infos
        info = await self.get_server_info(guild)
        
        # Création de l'embed principal
        embed = discord.Embed(
            title="✅ Nouveau Serveur Rejoint !",
            description=f"**{info['name']}** vient d'ajouter le bot",
            color=discord.Color.from_rgb(40, 167, 69),
            timestamp=datetime.utcnow()
        )
        
        if info["icon"]:
            embed.set_thumbnail(url=info["icon"])
        
        if info["banner"]:
            embed.set_image(url=info["banner"])
        
        # Informations générales
        embed.add_field(
            name="🏷️ Informations Générales",
            value=(
                f"**Nom :** `{info['name']}`\n"
                f"**ID :** `{info['id']}`\n"
                f"**Description :** *{info['description'][:100]}*\n"
                f"**Région :** Automatique"
            ),
            inline=False
        )
        
        # Propriétaire
        embed.add_field(
            name="👑 Propriétaire",
            value=(
                f"**Nom :** {info['owner'].mention if info['owner'] else 'Inconnu'}\n"
                f"**Tag :** `{info['owner']}`\n"
                f"**ID :** `{info['owner_id']}`\n"
                f"**Compte créé :** <t:{int(info['owner'].created_at.timestamp()) if info['owner'] else 0}:R>"
            ),
            inline=True
        )
        
        # Statistiques membres
        embed.add_field(
            name="👥 Membres",
            value=(
                f"**Total :** `{info['member_count']}`\n"
                f"👤 Humains : `{info['humans']}`\n"
                f"🤖 Bots : `{info['bots']}`\n"
                f"📊 Ratio : `{round(info['humans']/info['member_count']*100) if info['member_count'] > 0 else 0}%`"
            ),
            inline=True
        )
        
        # Statuts en ligne
        embed.add_field(
            name="🟢 Statuts",
            value=(
                f"🟢 En ligne : `{info['online']}`\n"
                f"🟡 Absent : `{info['idle']}`\n"
                f"🔴 Occupé : `{info['dnd']}`\n"
                f"⚫ Hors ligne : `{info['offline']}`"
            ),
            inline=True
        )
        
        # Salons
        embed.add_field(
            name="📝 Salons",
            value=(
                f"💬 Texte : `{info['text_channels']}`\n"
                f"🔊 Vocal : `{info['voice_channels']}`\n"
                f"📁 Catégories : `{info['categories']}`\n"
                f"📊 Total : `{info['text_channels'] + info['voice_channels']}`"
            ),
            inline=True
        )
        
        # Contenu
        embed.add_field(
            name="🎨 Contenu",
            value=(
                f"🎭 Rôles : `{info['roles_count']}`\n"
                f"😀 Emojis : `{info['emojis_count']}`\n"
                f"🎯 Stickers : `{info['stickers_count']}`\n"
                f"🔗 Invitations : `{info['invite_count']}`"
            ),
            inline=True
        )
        
        # Sécurité & Modération
        embed.add_field(
            name="🛡️ Sécurité & Modération",
            value=(
                f"**Vérification :** `{info['verification_level']}`\n"
                f"🔨 Bannissements : `{info['ban_count']}`\n"
                f"🔗 Webhooks : `{info['webhook_count']}`\n"
                f"💎 Boosts : `Niveau {info['boost_level']}` (`{info['boost_count']}` boosts)"
            ),
            inline=False
        )
        
        # Date de création du serveur
        embed.add_field(
            name="📅 Serveur Créé",
            value=(
                f"**Date :** <t:{int(info['created_at'].timestamp())}:F>\n"
                f"**Il y a :** <t:{int(info['created_at'].timestamp())}:R>\n"
                f"**Âge :** `{(datetime.utcnow() - info['created_at']).days}` jours"
            ),
            inline=True
        )
        
        # Date d'ajout du bot
        embed.add_field(
            name="🤖 Bot Ajouté",
            value=(
                f"**Date :** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                f"**Heure :** <t:{int(datetime.utcnow().timestamp())}:T>"
            ),
            inline=True
        )
        
        # Fonctionnalités spéciales
        if info["features"]:
            features_text = []
            feature_emojis = {
                "VERIFIED": "✅ Vérifié",
                "PARTNERED": "🤝 Partenaire",
                "COMMUNITY": "🌐 Communauté",
                "DISCOVERABLE": "🔍 Découvrable",
                "VANITY_URL": "🔗 URL Personnalisée",
                "ANIMATED_ICON": "🎬 Icône Animée",
                "BANNER": "🖼️ Bannière",
                "WELCOME_SCREEN_ENABLED": "👋 Écran Bienvenue",
                "MEMBER_VERIFICATION_GATE_ENABLED": "🚪 Gate Vérification",
                "PREVIEW_ENABLED": "👁️ Prévisualisation",
                "MONETIZATION_ENABLED": "💰 Monétisation",
                "PRIVATE_THREADS": "🧵 Threads Privés",
                "ROLE_ICONS": "🎭 Icônes Rôles",
                "NEWS": "📰 Actualités"
            }
            
            for feature in info["features"][:10]:  # Limite à 10
                features_text.append(feature_emojis.get(feature, f"• {feature}"))
            
            embed.add_field(
                name="⭐ Fonctionnalités Spéciales",
                value="\n".join(features_text) if features_text else "Aucune",
                inline=False
            )
        
        # Footer avec statistiques globales
        embed.set_footer(
            text=f"Total serveurs : {len(self.bot.guilds)} • Total utilisateurs : {sum(g.member_count for g in self.bot.guilds)}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        try:
            await log_channel.send(embed=embed)
            
            # Message supplémentaire si serveur suspect
            if info["member_count"] < 10 or (info["humans"] / info["member_count"] < 0.3 if info["member_count"] > 0 else False):
                alert_embed = discord.Embed(
                    title="⚠️ Serveur Potentiellement Suspect",
                    description=(
                        f"Le serveur **{info['name']}** présente des caractéristiques inhabituelles :\n"
                        f"• Peu de membres ({info['member_count']})\n"
                        f"• Ratio bots/humains élevé ({round(info['bots']/info['member_count']*100) if info['member_count'] > 0 else 0}%)"
                    ),
                    color=discord.Color.from_rgb(255, 193, 7)
                )
                await log_channel.send(embed=alert_embed)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du log: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Quand le bot quitte un serveur"""
        log_channel = self.bot.get_channel(self.log_channel_id)
        
        if not log_channel:
            print(f"⚠️ Salon de log introuvable (ID: {self.log_channel_id})")
            return
        
        # Récupère les infos (limitées car le bot n'est plus dans le serveur)
        embed = discord.Embed(
            title="❌ Serveur Quitté",
            description=f"Le bot a quitté **{guild.name}**",
            color=discord.Color.from_rgb(220, 53, 69),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informations de base
        embed.add_field(
            name="🏷️ Informations",
            value=(
                f"**Nom :** `{guild.name}`\n"
                f"**ID :** `{guild.id}`\n"
                f"**Propriétaire :** {guild.owner.mention if guild.owner else 'Inconnu'}\n"
                f"**ID Propriétaire :** `{guild.owner_id}`"
            ),
            inline=False
        )
        
        # Statistiques
        embed.add_field(
            name="📊 Statistiques",
            value=(
                f"👥 Membres : `{guild.member_count}`\n"
                f"💬 Salons texte : `{len(guild.text_channels)}`\n"
                f"🔊 Salons vocaux : `{len(guild.voice_channels)}`\n"
                f"🎭 Rôles : `{len(guild.roles)}`"
            ),
            inline=True
        )
        
        # Dates
        embed.add_field(
            name="📅 Dates",
            value=(
                f"**Serveur créé :** <t:{int(guild.created_at.timestamp())}:R>\n"
                f"**Quitté le :** <t:{int(datetime.utcnow().timestamp())}:F>"
            ),
            inline=True
        )
        
        # Raison possible
        embed.add_field(
            name="❓ Raison Possible",
            value=(
                "• Bot expulsé/banni\n"
                "• Serveur supprimé\n"
                "• Bot retiré manuellement"
            ),
            inline=False
        )
        
        embed.set_footer(
            text=f"Total serveurs : {len(self.bot.guilds)} • Total utilisateurs : {sum(g.member_count for g in self.bot.guilds)}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du log: {e}")

    # ======================
    # LOGS ACTIONS MODÉRATION
    # ======================

    async def log_mod_action(self, guild, action_type, embed):
        """Envoie un log d'action de modération"""
        if not self.mod_log_channel_id:
            return
        
        mod_log_channel = self.bot.get_channel(self.mod_log_channel_id)
        if not mod_log_channel:
            return
        
        try:
            await mod_log_channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Erreur log modération: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log quand un membre est banni"""
        await asyncio.sleep(1)
        
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    moderator = entry.user
                    reason = entry.reason or "Aucune raison fournie"
                    
                    embed = discord.Embed(
                        title="🔨 Membre Banni",
                        description=f"**{user}** a été banni du serveur **{guild.name}**",
                        color=discord.Color.from_rgb(220, 53, 69),
                        timestamp=datetime.utcnow()
                    )
                    
                    if user.avatar:
                        embed.set_thumbnail(url=user.display_avatar.url)
                    
                    embed.add_field(
                        name="👤 Utilisateur Banni",
                        value=(
                            f"**Nom :** `{user}`\n"
                            f"**ID :** `{user.id}`\n"
                            f"**Mention :** {user.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👮 Modérateur",
                        value=(
                            f"**Nom :** `{moderator}`\n"
                            f"**ID :** `{moderator.id}`\n"
                            f"**Mention :** {moderator.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🏛️ Serveur",
                        value=(
                            f"**Nom :** `{guild.name}`\n"
                            f"**ID :** `{guild.id}`\n"
                            f"**Propriétaire :** {guild.owner.mention if guild.owner else 'Inconnu'}"
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📋 Raison",
                        value=f"```{reason[:1000]}```",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📅 Date & Heure",
                        value=(
                            f"**Date complète :** <t:{int(entry.created_at.timestamp())}:F>\n"
                            f"**Heure :** <t:{int(entry.created_at.timestamp())}:T>\n"
                            f"**Il y a :** <t:{int(entry.created_at.timestamp())}:R>"
                        ),
                        inline=False
                    )
                    
                    embed.set_footer(
                        text=f"Action ID: {entry.id} • Serveur: {guild.name}",
                        icon_url=guild.icon.url if guild.icon else None
                    )
                    
                    await self.log_mod_action(guild, "ban", embed)
                    break
        except Exception as e:
            print(f"❌ Erreur log ban: {e}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Log quand un membre est débanni"""
        await asyncio.sleep(1)
        
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    moderator = entry.user
                    
                    embed = discord.Embed(
                        title="✅ Membre Débanni",
                        description=f"**{user}** a été débanni du serveur **{guild.name}**",
                        color=discord.Color.from_rgb(40, 167, 69),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="👤 Utilisateur Débanni",
                        value=(
                            f"**Nom :** `{user}`\n"
                            f"**ID :** `{user.id}`\n"
                            f"**Mention :** {user.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👮 Modérateur",
                        value=(
                            f"**Nom :** `{moderator}`\n"
                            f"**ID :** `{moderator.id}`\n"
                            f"**Mention :** {moderator.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🏛️ Serveur",
                        value=(
                            f"**Nom :** `{guild.name}`\n"
                            f"**ID :** `{guild.id}`"
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📅 Date & Heure",
                        value=(
                            f"**Date :** <t:{int(entry.created_at.timestamp())}:F>\n"
                            f"**Il y a :** <t:{int(entry.created_at.timestamp())}:R>"
                        ),
                        inline=False
                    )
                    
                    embed.set_footer(text=f"Serveur: {guild.name}")
                    
                    await self.log_mod_action(guild, "unban", embed)
                    break
        except Exception as e:
            print(f"❌ Erreur log unban: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log quand un membre est kick (différent du départ normal)"""
        await asyncio.sleep(1)
        
        try:
            async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id and (datetime.utcnow() - entry.created_at).seconds < 5:
                    moderator = entry.user
                    reason = entry.reason or "Aucune raison fournie"
                    
                    embed = discord.Embed(
                        title="👢 Membre Expulsé (Kick)",
                        description=f"**{member}** a été expulsé du serveur **{member.guild.name}**",
                        color=discord.Color.from_rgb(255, 193, 7),
                        timestamp=datetime.utcnow()
                    )
                    
                    if member.avatar:
                        embed.set_thumbnail(url=member.display_avatar.url)
                    
                    embed.add_field(
                        name="👤 Utilisateur Expulsé",
                        value=(
                            f"**Nom :** `{member}`\n"
                            f"**ID :** `{member.id}`\n"
                            f"**Mention :** {member.mention}\n"
                            f"**A rejoint le :** <t:{int(member.joined_at.timestamp()) if member.joined_at else 0}:R>"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👮 Modérateur",
                        value=(
                            f"**Nom :** `{moderator}`\n"
                            f"**ID :** `{moderator.id}`\n"
                            f"**Mention :** {moderator.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🏛️ Serveur",
                        value=(
                            f"**Nom :** `{member.guild.name}`\n"
                            f"**ID :** `{member.guild.id}`\n"
                            f"**Propriétaire :** {member.guild.owner.mention if member.guild.owner else 'Inconnu'}"
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📋 Raison",
                        value=f"```{reason[:1000]}```",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📅 Date & Heure",
                        value=(
                            f"**Date :** <t:{int(entry.created_at.timestamp())}:F>\n"
                            f"**Il y a :** <t:{int(entry.created_at.timestamp())}:R>"
                        ),
                        inline=False
                    )
                    
                    # Rôles du membre
                    if len(member.roles) > 1:
                        roles = ", ".join([r.mention for r in member.roles[1:][:10]])
                        embed.add_field(
                            name="🎭 Rôles du Membre",
                            value=roles,
                            inline=False
                        )
                    
                    embed.set_footer(text=f"Serveur: {member.guild.name}")
                    
                    await self.log_mod_action(member.guild, "kick", embed)
                    return
        except Exception as e:
            print(f"❌ Erreur log kick: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log les timeouts (mises en sourdine)"""
        # Détecte les timeouts
        if before.timed_out_until != after.timed_out_until:
            await asyncio.sleep(1)
            
            try:
                async for entry in after.guild.audit_logs(limit=3, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        moderator = entry.user
                        
                        # Timeout ajouté
                        if after.timed_out_until and not before.timed_out_until:
                            embed = discord.Embed(
                                title="⏱️ Membre Mis en Timeout",
                                description=f"**{after}** a été mis en timeout dans **{after.guild.name}**",
                                color=discord.Color.from_rgb(255, 193, 7),
                                timestamp=datetime.utcnow()
                            )
                            
                            embed.add_field(
                                name="👤 Utilisateur",
                                value=(
                                    f"**Nom :** `{after}`\n"
                                    f"**ID :** `{after.id}`\n"
                                    f"**Mention :** {after.mention}"
                                ),
                                inline=True
                            )
                            
                            embed.add_field(
                                name="👮 Modérateur",
                                value=(
                                    f"**Nom :** `{moderator}`\n"
                                    f"**ID :** `{moderator.id}`\n"
                                    f"**Mention :** {moderator.mention}"
                                ),
                                inline=True
                            )
                            
                            embed.add_field(
                                name="🏛️ Serveur",
                                value=f"**Nom :** `{after.guild.name}`\n**ID :** `{after.guild.id}`",
                                inline=False
                            )
                            
                            embed.add_field(
                                name="⏰ Durée du Timeout",
                                value=(
                                    f"**Jusqu'au :** <t:{int(after.timed_out_until.timestamp())}:F>\n"
                                    f"**Expire :** <t:{int(after.timed_out_until.timestamp())}:R>"
                                ),
                                inline=False
                            )
                            
                            if entry.reason:
                                embed.add_field(
                                    name="📋 Raison",
                                    value=f"```{entry.reason[:1000]}```",
                                    inline=False
                                )
                            
                            embed.set_footer(text=f"Serveur: {after.guild.name}")
                            await self.log_mod_action(after.guild, "timeout", embed)
                        
                        # Timeout retiré
                        elif before.timed_out_until and not after.timed_out_until:
                            embed = discord.Embed(
                                title="✅ Timeout Retiré",
                                description=f"Le timeout de **{after}** a été retiré dans **{after.guild.name}**",
                                color=discord.Color.from_rgb(40, 167, 69),
                                timestamp=datetime.utcnow()
                            )
                            
                            embed.add_field(
                                name="👤 Utilisateur",
                                value=f"**Nom :** `{after}`\n**ID :** `{after.id}`",
                                inline=True
                            )
                            
                            embed.add_field(
                                name="👮 Modérateur",
                                value=f"**Nom :** `{moderator}`\n**ID :** `{moderator.id}`",
                                inline=True
                            )
                            
                            embed.set_footer(text=f"Serveur: {after.guild.name}")
                            await self.log_mod_action(after.guild, "timeout_remove", embed)
                        
                        break
            except Exception as e:
                print(f"❌ Erreur log timeout: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log suppression de salons"""
        await asyncio.sleep(1)
        
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    moderator = entry.user
                    
                    embed = discord.Embed(
                        title="🗑️ Salon Supprimé",
                        description=f"Un salon a été supprimé dans **{channel.guild.name}**",
                        color=discord.Color.from_rgb(220, 53, 69),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="📝 Salon",
                        value=(
                            f"**Nom :** `{channel.name}`\n"
                            f"**Type :** `{channel.type}`\n"
                            f"**ID :** `{channel.id}`"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👮 Modérateur",
                        value=(
                            f"**Nom :** `{moderator}`\n"
                            f"**ID :** `{moderator.id}`\n"
                            f"**Mention :** {moderator.mention}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🏛️ Serveur",
                        value=f"**Nom :** `{channel.guild.name}`\n**ID :** `{channel.guild.id}`",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📅 Date",
                        value=f"<t:{int(entry.created_at.timestamp())}:F>",
                        inline=False
                    )
                    
                    embed.set_footer(text=f"Serveur: {channel.guild.name}")
                    await self.log_mod_action(channel.guild, "channel_delete", embed)
                    break
        except Exception as e:
            print(f"❌ Erreur log suppression salon: {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log suppression de rôles"""
        await asyncio.sleep(1)
        
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    moderator = entry.user
                    
                    embed = discord.Embed(
                        title="🎭 Rôle Supprimé",
                        description=f"Un rôle a été supprimé dans **{role.guild.name}**",
                        color=discord.Color.from_rgb(220, 53, 69),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="🎭 Rôle",
                        value=(
                            f"**Nom :** `{role.name}`\n"
                            f"**ID :** `{role.id}`\n"
                            f"**Couleur :** `{role.color}`"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👮 Modérateur",
                        value=(
                            f"**Nom :** `{moderator}`\n"
                            f"**ID :** `{moderator.id}`"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📅 Date",
                        value=f"<t:{int(entry.created_at.timestamp())}:F>",
                        inline=False
                    )
                    
                    embed.set_footer(text=f"Serveur: {role.guild.name}")
                    await self.log_mod_action(role.guild, "role_delete", embed)
                    break
        except Exception as e:
            print(f"❌ Erreur log suppression rôle: {e}")

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        """Log suppression en masse de messages"""
        if not messages:
            return
        
        guild = messages[0].guild
        channel = messages[0].channel
        
        await asyncio.sleep(1)
        
        try:
            async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.message_bulk_delete):
                moderator = entry.user
                
                embed = discord.Embed(
                    title="🗑️ Suppression en Masse",
                    description=f"Des messages ont été supprimés en masse dans **{guild.name}**",
                    color=discord.Color.from_rgb(220, 53, 69),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="📊 Statistiques",
                    value=(
                        f"**Messages supprimés :** `{len(messages)}`\n"
                        f"**Salon :** {channel.mention}\n"
                        f"**Auteurs concernés :** `{len(set(m.author for m in messages))}`"
                    ),
                    inline=False
                )
                
                embed.add_field(
                    name="👮 Modérateur",
                    value=(
                        f"**Nom :** `{moderator}`\n"
                        f"**ID :** `{moderator.id}`\n"
                        f"**Mention :** {moderator.mention}"
                    ),
                    inline=True
                )
                
                embed.add_field(
                    name="📅 Date",
                    value=f"<t:{int(entry.created_at.timestamp())}:F>",
                    inline=False
                )
                
                embed.set_footer(text=f"Serveur: {guild.name}")
                await self.log_mod_action(guild, "bulk_delete", embed)
                break
        except Exception as e:
            print(f"❌ Erreur log bulk delete: {e}")

    # ======================
    # COMMANDES ADMIN
    # ======================

    @commands.command(name="setmodlogs")
    @commands.is_owner()
    async def set_mod_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Définit le salon pour les logs de modération"""
        
        if channel is None:
            channel = ctx.channel
        
        self.mod_log_channel_id = channel.id
        
        embed = discord.Embed(
            title="✅ Salon de Logs Modération Configuré",
            description=f"Les actions de modération seront loggées dans {channel.mention}",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        
        embed.add_field(
            name="📋 Actions Loggées",
            value=(
                "• 🔨 Bannissements\n"
                "• ✅ Débannissements\n"
                "• 👢 Kicks/Expulsions\n"
                "• ⏱️ Timeouts\n"
                "• 🗑️ Suppressions de salons\n"
                "• 🎭 Suppressions de rôles\n"
                "• 🗑️ Suppressions en masse de messages"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Note",
            value=(
                "Configuration temporaire. Pour la rendre permanente :\n"
                f"```python\nself.mod_log_channel_id = {channel.id}\n```"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Message de test
        test_embed = discord.Embed(
            title="🧪 Logs de Modération Activés",
            description=(
                "✅ Ce salon recevra toutes les actions de modération effectuées sur les serveurs où le bot est présent.\n\n"
                "Chaque log contiendra :\n"
                "• L'action effectuée\n"
                "• Le modérateur responsable\n"
                "• L'utilisateur/élément ciblé\n"
                "• Le serveur concerné\n"
                "• La date et l'heure exactes\n"
                "• La raison (si fournie)"
            ),
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=test_embed)

    @commands.command(name="testmodlog")
    @commands.is_owner()
    async def test_mod_log(self, ctx):
        """Teste les logs de modération"""
        if not self.mod_log_channel_id:
            return await ctx.send("❌ Le salon de logs modération n'est pas configuré ! Utilisez `setmodlogs`")
        
        mod_log_channel = self.bot.get_channel(self.mod_log_channel_id)
        if not mod_log_channel:
            return await ctx.send(f"❌ Salon introuvable (ID: {self.mod_log_channel_id})")
        
        # Embed de test
        embed = discord.Embed(
            title="🧪 Test - Action de Modération",
            description=f"Ceci est un test du système de logs de modération pour **{ctx.guild.name}**",
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👮 Modérateur (Test)",
            value=(
                f"**Nom :** `{ctx.author}`\n"
                f"**ID :** `{ctx.author.id}`\n"
                f"**Mention :** {ctx.author.mention}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏛️ Serveur",
            value=(
                f"**Nom :** `{ctx.guild.name}`\n"
                f"**ID :** `{ctx.guild.id}`\n"
                f"**Propriétaire :** {ctx.guild.owner.mention if ctx.guild.owner else 'Inconnu'}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📅 Date & Heure",
            value=(
                f"**Date :** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                f"**Il y a :** <t:{int(datetime.utcnow().timestamp())}:R>"
            ),
            inline=False
        )
        
        embed.set_footer(text="🧪 CECI EST UN TEST")
        
        await mod_log_channel.send(embed=embed)
        await ctx.send(f"✅ Message de test envoyé dans {mod_log_channel.mention}")

    @commands.command(name="logstatus")
    @commands.is_owner()
    async def logs_status(self, ctx):
        """Affiche le statut de configuration des logs"""
        
        embed = discord.Embed(
            title="📊 Statut des Logs",
            description="Configuration actuelle du système de logs",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        # Logs serveurs
        server_log = self.bot.get_channel(self.log_channel_id)
        if server_log:
            embed.add_field(
                name="🌐 Logs Serveurs",
                value=f"✅ Configuré : {server_log.mention}",
                inline=False
            )
        else:
            embed.add_field(
                name="🌐 Logs Serveurs",
                value=f"❌ Non configuré ou salon introuvable\nID: `{self.log_channel_id}`",
                inline=False
            )
        
        # Logs modération
        if self.mod_log_channel_id:
            mod_log = self.bot.get_channel(self.mod_log_channel_id)
            if mod_log:
                embed.add_field(
                    name="🔨 Logs Modération",
                    value=f"✅ Configuré : {mod_log.mention}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🔨 Logs Modération",
                    value=f"❌ Salon introuvable\nID: `{self.mod_log_channel_id}`",
                    inline=False
                )
        else:
            embed.add_field(
                name="🔨 Logs Modération",
                value="⚠️ Non configuré\nUtilisez `setmodlogs #salon`",
                inline=False
            )
        
        embed.add_field(
            name="📋 Commandes Disponibles",
            value=(
                "`setlogchannel` - Logs serveurs\n"
                "`setmodlogs` - Logs modération\n"
                "`testserverjoin` - Test logs serveurs\n"
                "`testmodlog` - Test logs modération\n"
                "`logstatus` - Ce message"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    @commands.is_owner()
    async def set_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Définit le salon pour les logs de serveurs"""
        
        if channel is None:
            channel = ctx.channel
        
        self.log_channel_id = channel.id
        
        embed = discord.Embed(
            title="✅ Salon de Logs Configuré",
            description=f"Les logs des serveurs seront envoyés dans {channel.mention}",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        embed.add_field(
            name="💡 Note Importante",
            value=(
                "Cette configuration est **temporaire** et sera perdue au redémarrage.\n\n"
                "Pour une configuration permanente, modifie `log_channel_id` dans le code :\n"
                f"```python\nself.log_channel_id = {channel.id}\n```"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Message de test
        test_embed = discord.Embed(
            title="🧪 Test de Logs",
            description=(
                "✅ Ce salon recevra les notifications détaillées quand :\n"
                "• Le bot rejoint un nouveau serveur\n"
                "• Le bot quitte un serveur\n\n"
                "Les logs incluent toutes les informations importantes du serveur."
            ),
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=test_embed)

    @commands.command(name="testserverjoin")
    @commands.is_owner()
    async def test_join_log(self, ctx):
        """Teste le message de log avec le serveur actuel"""
        log_channel = self.bot.get_channel(self.log_channel_id)
        
        if not log_channel:
            return await ctx.send(f"❌ Salon de log introuvable (ID: {self.log_channel_id})")
        
        await ctx.send("🔄 Génération du log de test...")
        
        # Simule un join avec le serveur actuel
        guild = ctx.guild
        info = await self.get_server_info(guild)
        
        # Même embed que on_guild_join mais avec mention TEST
        embed = discord.Embed(
            title="✅ Nouveau Serveur Rejoint ! (TEST)",
            description=f"**{info['name']}** vient d'ajouter le bot",
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        
        if info["icon"]:
            embed.set_thumbnail(url=info["icon"])
        
        embed.add_field(
            name="🏷️ Informations Générales",
            value=(
                f"**Nom :** `{info['name']}`\n"
                f"**ID :** `{info['id']}`\n"
                f"**Description :** *{info['description'][:100]}*"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👑 Propriétaire",
            value=(
                f"**Nom :** {info['owner'].mention}\n"
                f"**Tag :** `{info['owner']}`\n"
                f"**ID :** `{info['owner_id']}`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="👥 Membres",
            value=(
                f"**Total :** `{info['member_count']}`\n"
                f"👤 Humains : `{info['humans']}`\n"
                f"🤖 Bots : `{info['bots']}`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🟢 Statuts",
            value=(
                f"🟢 En ligne : `{info['online']}`\n"
                f"🟡 Absent : `{info['idle']}`\n"
                f"🔴 Occupé : `{info['dnd']}`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📝 Salons",
            value=(
                f"💬 Texte : `{info['text_channels']}`\n"
                f"🔊 Vocal : `{info['voice_channels']}`\n"
                f"📁 Catégories : `{info['categories']}`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Contenu",
            value=(
                f"🎭 Rôles : `{info['roles_count']}`\n"
                f"😀 Emojis : `{info['emojis_count']}`\n"
                f"🎯 Stickers : `{info['stickers_count']}`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Sécurité",
            value=(
                f"**Vérification :** `{info['verification_level']}`\n"
                f"🔨 Bannissements : `{info['ban_count']}`\n"
                f"💎 Boosts : Niveau `{info['boost_level']}`"
            ),
            inline=True
        )
        
        embed.set_footer(
            text=f"🧪 CECI EST UN TEST • Total serveurs : {len(self.bot.guilds)}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await log_channel.send(embed=embed)
        await ctx.send(f"✅ Message de test envoyé dans {log_channel.mention}")

    @commands.command(name="serverstats")
    @commands.is_owner()
    async def server_stats(self, ctx):
        """Affiche les statistiques globales de tous les serveurs"""
        
        total_guilds = len(self.bot.guilds)
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Statistiques Globales",
            description="Vue d'ensemble de tous les serveurs",
            color=discord.Color.from_rgb(0, 123, 255),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🌐 Serveurs",
            value=f"**Total :** `{total_guilds}`",
            inline=True
        )
        
        embed.add_field(
            name="👥 Utilisateurs",
            value=f"**Total :** `{total_members}`",
            inline=True
        )
        
        embed.add_field(
            name="📝 Salons",
            value=f"**Total :** `{total_channels}`",
            inline=True
        )
        
        # Top 5 serveurs
        top_guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)[:5]
        top_text = "\n".join([f"`{i+1}.` **{g.name}** - `{g.member_count}` membres" for i, g in enumerate(top_guilds)])
        
        embed.add_field(
            name="🏆 Top 5 Serveurs",
            value=top_text,
            inline=False
        )
        
        await ctx.send(embed=embed)

# Setup
async def setup(bot):
    await bot.add_cog(ServerLogger(bot))
    print("✅ ServerLogger ultra-détaillé chargé avec succès !")