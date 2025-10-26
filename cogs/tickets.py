import discord
from discord.ext import commands
from datetime import datetime
import json
import os
import asyncio

class Tickets(commands.Cog):
    """Système de tickets complet et optimisé"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "tickets_config.json"
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
                "category_id": None,
                "panel_channel_id": None,
                "panel_message_id": None,
                "log_channel_id": None,
                "support_role_id": None,
                "ticket_count": 0,
                "open_tickets": {},
                "types": {
                    "support": {"emoji": "💬", "name": "Support Général", "enabled": True},
                    "report": {"emoji": "⚠️", "name": "Signalement", "enabled": True},
                    "partnership": {"emoji": "🤝", "name": "Partenariat", "enabled": True},
                    "other": {"emoji": "📝", "name": "Autre", "enabled": True}
                }
            }
            self.save_config()
        return self.config[guild_id]
    
    def create_embed(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Ticket System")
        return embed
    
    async def log_action(self, guild, action, user, ticket_channel=None, reason=None):
        """Log les actions des tickets"""
        config = self.get_config(guild.id)
        log_channel_id = config.get("log_channel_id")
        
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(int(log_channel_id))
        if not log_channel:
            return
        
        colors = {
            "created": discord.Color.from_rgb(40, 167, 69),
            "closed": discord.Color.from_rgb(220, 53, 69),
            "claimed": discord.Color.from_rgb(0, 123, 255),
            "added": discord.Color.from_rgb(40, 167, 69),
            "removed": discord.Color.from_rgb(255, 193, 7)
        }
        
        embed = self.create_embed(
            f"🎫 Ticket {action.title()}",
            f"**Utilisateur :** {user.mention}\n"
            f"**Ticket :** {ticket_channel.mention if ticket_channel else 'N/A'}\n"
            f"{'**Raison :** ' + reason if reason else ''}",
            colors.get(action, discord.Color.blue())
        )
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.command(name="ticketsetup")
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx):
        """Configure automatiquement le système de tickets"""
        
        await ctx.send("🔄 **Configuration du système de tickets...**")
        
        config = self.get_config(ctx.guild.id)
        
        # 1. Créer la catégorie
        category = None
        if config["category_id"]:
            category = ctx.guild.get_channel(int(config["category_id"]))
        
        if not category:
            try:
                category = await ctx.guild.create_category(
                    name="🎫 TICKETS",
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(
                            read_messages=False,
                            send_messages=False
                        ),
                        ctx.guild.me: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            manage_channels=True,
                            manage_messages=True
                        )
                    }
                )
                config["category_id"] = category.id
            except Exception as e:
                return await ctx.send(f"❌ Erreur lors de la création de la catégorie : {e}")
        
        # 2. Créer le salon des logs
        log_channel = None
        if config["log_channel_id"]:
            log_channel = ctx.guild.get_channel(int(config["log_channel_id"]))
        
        if not log_channel:
            try:
                log_channel = await ctx.guild.create_text_channel(
                    name="📋・logs-tickets",
                    category=category,
                    topic="Logs du système de tickets"
                )
                config["log_channel_id"] = log_channel.id
            except:
                pass
        
        # 3. Créer le salon du panel
        panel_channel = None
        if config["panel_channel_id"]:
            panel_channel = ctx.guild.get_channel(int(config["panel_channel_id"]))
        
        if not panel_channel:
            try:
                panel_channel = await ctx.guild.create_text_channel(
                    name="🎫・créer-ticket",
                    category=category,
                    topic="Cliquez sur un bouton pour créer un ticket",
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=False
                        ),
                        ctx.guild.me: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True
                        )
                    }
                )
                config["panel_channel_id"] = panel_channel.id
            except Exception as e:
                return await ctx.send(f"❌ Erreur lors de la création du salon panel : {e}")
        
        # 4. Créer le message du panel
        panel_embed = discord.Embed(
            title="🎫 Système de Tickets",
            description=(
                "Bienvenue dans notre système de support !\n\n"
                "**Comment créer un ticket ?**\n"
                "Cliquez sur un des boutons ci-dessous selon votre besoin.\n\n"
                "**Types de tickets disponibles :**\n"
                "💬 **Support Général** - Besoin d'aide générale\n"
                "⚠️ **Signalement** - Signaler un problème\n"
                "🤝 **Partenariat** - Proposition de partenariat\n"
                "📝 **Autre** - Autre demande\n\n"
                "⏱️ Temps de réponse moyen : **< 24h**\n"
                "✅ Un membre du staff vous répondra rapidement"
            ),
            color=discord.Color.from_rgb(0, 123, 255)
        )
        panel_embed.set_footer(text=f"{ctx.guild.name} • Ticket System", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        panel_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        # Créer les boutons
        view = TicketButtonsView(self)
        
        try:
            # Supprimer l'ancien message si existe
            if config["panel_message_id"]:
                try:
                    old_message = await panel_channel.fetch_message(int(config["panel_message_id"]))
                    await old_message.delete()
                except:
                    pass
            
            panel_message = await panel_channel.send(embed=panel_embed, view=view)
            config["panel_message_id"] = panel_message.id
        except Exception as e:
            return await ctx.send(f"❌ Erreur lors de la création du panel : {e}")
        
        self.save_config()
        
        # Message de confirmation
        embed = discord.Embed(
            title="✅ Configuration Terminée !",
            description=(
                f"**Catégorie :** {category.mention}\n"
                f"**Panel :** {panel_channel.mention}\n"
                f"**Logs :** {log_channel.mention if log_channel else 'Non configuré'}\n\n"
                f"**Prochaine étape :**\n"
                f"Utilisez `ticket setrole @role` pour définir le rôle support"
            ),
            color=discord.Color.from_rgb(40, 167, 69)
        )
        
        await ctx.send(embed=embed)
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crée un ticket"""
        config = self.get_config(interaction.guild.id)
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        open_tickets = config.get("open_tickets", {})
        user_id = str(interaction.user.id)
        
        if user_id in open_tickets:
            existing_channel = interaction.guild.get_channel(int(open_tickets[user_id]))
            if existing_channel:
                return await interaction.response.send_message(
                    f"❌ Vous avez déjà un ticket ouvert : {existing_channel.mention}",
                    ephemeral=True
                )
        
        # Incrémenter le compteur
        config["ticket_count"] += 1
        ticket_number = config["ticket_count"]
        
        # Récupérer la catégorie
        category_id = config.get("category_id")
        if not category_id:
            return await interaction.response.send_message(
                "❌ Le système de tickets n'est pas configuré !",
                ephemeral=True
            )
        
        category = interaction.guild.get_channel(int(category_id))
        if not category:
            return await interaction.response.send_message(
                "❌ La catégorie des tickets est introuvable !",
                ephemeral=True
            )
        
        # Récupérer le rôle support
        support_role = None
        if config.get("support_role_id"):
            support_role = interaction.guild.get_role(int(config["support_role_id"]))
        
        # Permissions du ticket
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            )
        
        # Créer le salon
        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=f"ticket-{ticket_number:04d}",
                category=category,
                topic=f"Ticket de {interaction.user} • Type: {ticket_type}",
                overwrites=overwrites
            )
        except Exception as e:
            return await interaction.response.send_message(
                f"❌ Erreur lors de la création du ticket : {e}",
                ephemeral=True
            )
        
        # Sauvegarder le ticket
        config["open_tickets"][user_id] = ticket_channel.id
        self.save_config()
        
        # Message de bienvenue dans le ticket
        ticket_info = config["types"].get(ticket_type, {})
        emoji = ticket_info.get("emoji", "🎫")
        name = ticket_info.get("name", ticket_type.title())
        
        welcome_embed = discord.Embed(
            title=f"{emoji} Ticket #{ticket_number:04d}",
            description=(
                f"Bienvenue {interaction.user.mention} !\n\n"
                f"**Type :** {name}\n"
                f"**Statut :** 🟢 Ouvert\n\n"
                f"Merci d'avoir créé un ticket. Un membre du staff vous répondra très bientôt.\n"
                f"En attendant, décrivez votre demande de manière détaillée."
            ),
            color=discord.Color.from_rgb(40, 167, 69)
        )
        welcome_embed.set_footer(text=f"Créé le {datetime.utcnow().strftime('%d/%m/%Y à %H:%M')}")
        
        # Boutons du ticket
        view = TicketControlView(self)
        
        await ticket_channel.send(
            content=f"{interaction.user.mention} {support_role.mention if support_role else ''}",
            embed=welcome_embed,
            view=view
        )
        
        # Log de création
        await self.log_action(interaction.guild, "created", interaction.user, ticket_channel)
        
        await interaction.response.send_message(
            f"✅ Votre ticket a été créé : {ticket_channel.mention}",
            ephemeral=True
        )
    
    async def close_ticket(self, interaction: discord.Interaction, reason: str = None):
        """Ferme un ticket"""
        config = self.get_config(interaction.guild.id)
        channel = interaction.channel
        
        # Vérifier si c'est un ticket
        if not channel.category or channel.category.id != config.get("category_id"):
            return await interaction.response.send_message(
                "❌ Cette commande ne peut être utilisée que dans un ticket !",
                ephemeral=True
            )
        
        # Trouver le propriétaire du ticket
        ticket_owner = None
        for user_id, ticket_channel_id in config["open_tickets"].items():
            if ticket_channel_id == channel.id:
                ticket_owner = interaction.guild.get_member(int(user_id))
                del config["open_tickets"][user_id]
                break
        
        self.save_config()
        
        # Message de fermeture
        close_embed = discord.Embed(
            title="🔒 Ticket Fermé",
            description=(
                f"Ce ticket a été fermé par {interaction.user.mention}\n"
                f"{'**Raison :** ' + reason if reason else ''}\n\n"
                f"Le salon sera supprimé dans 5 secondes..."
            ),
            color=discord.Color.from_rgb(220, 53, 69)
        )
        
        await interaction.response.send_message(embed=close_embed)
        
        # Log de fermeture
        await self.log_action(
            interaction.guild,
            "closed",
            interaction.user,
            channel,
            reason
        )
        
        # Supprimer le salon après 5 secondes
        await asyncio.sleep(5)
        try:
            await channel.delete()
        except:
            pass
    
    async def claim_ticket(self, interaction: discord.Interaction):
        """Claim un ticket"""
        config = self.get_config(interaction.guild.id)
        
        # Vérifier le rôle support
        support_role_id = config.get("support_role_id")
        if support_role_id:
            support_role = interaction.guild.get_role(int(support_role_id))
            if support_role and support_role not in interaction.user.roles:
                return await interaction.response.send_message(
                    "❌ Vous devez avoir le rôle support pour claim un ticket !",
                    ephemeral=True
                )
        
        # Message de claim
        claim_embed = discord.Embed(
            title="✋ Ticket Pris en Charge",
            description=f"**{interaction.user.mention}** prend en charge ce ticket",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        await interaction.response.send_message(embed=claim_embed)
        
        # Log de claim
        await self.log_action(interaction.guild, "claimed", interaction.user, interaction.channel)
    
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        """Ajoute un utilisateur au ticket"""
        try:
            await interaction.channel.set_permissions(
                user,
                read_messages=True,
                send_messages=True
            )
            
            embed = discord.Embed(
                title="➕ Utilisateur Ajouté",
                description=f"{user.mention} a été ajouté au ticket par {interaction.user.mention}",
                color=discord.Color.from_rgb(40, 167, 69)
            )
            
            await interaction.response.send_message(embed=embed)
            await self.log_action(interaction.guild, "added", user, interaction.channel)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)
    
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        """Retire un utilisateur du ticket"""
        try:
            await interaction.channel.set_permissions(user, overwrite=None)
            
            embed = discord.Embed(
                title="➖ Utilisateur Retiré",
                description=f"{user.mention} a été retiré du ticket par {interaction.user.mention}",
                color=discord.Color.from_rgb(255, 193, 7)
            )
            
            await interaction.response.send_message(embed=embed)
            await self.log_action(interaction.guild, "removed", user, interaction.channel)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)
    
    # ==================== COMMANDES ====================
    
    @commands.group(name="ticket", invoke_without_command=True)
    async def ticket(self, ctx):
        """Système de tickets"""
        embed = discord.Embed(
            title="🎫 Système de Tickets",
            description="Système de support complet pour votre serveur",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        embed.add_field(
            name="⚙️ Configuration (Admin)",
            value=(
                "`ticketsetup` • Configuration automatique\n"
                "`ticket setrole @role` • Définir le rôle support\n"
                "`ticket panel` • Recréer le panel\n"
                "`ticket stats` • Statistiques"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎫 Gestion des Tickets",
            value=(
                "`ticket close [raison]` • Fermer le ticket\n"
                "`ticket claim` • Prendre en charge\n"
                "`ticket add @user` • Ajouter un utilisateur\n"
                "`ticket remove @user` • Retirer un utilisateur"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @ticket.command(name="setrole")
    @commands.has_permissions(administrator=True)
    async def ticket_setrole(self, ctx, role: discord.Role):
        """Définit le rôle support"""
        config = self.get_config(ctx.guild.id)
        config["support_role_id"] = role.id
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Rôle Support Défini",
            description=f"Le rôle {role.mention} a accès à tous les tickets",
            color=discord.Color.from_rgb(40, 167, 69)
        )
        await ctx.send(embed=embed)
    
    @ticket.command(name="close")
    async def ticket_close_cmd(self, ctx, *, reason: str = None):
        """Ferme le ticket actuel"""
        
        class ConfirmView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=30)
                self.cog = cog
            
            @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.danger, emoji="🔒")
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.cog.close_ticket(interaction, reason)
            
            @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌")
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message("❌ Fermeture annulée", ephemeral=True)
                await interaction.message.delete()
        
        embed = discord.Embed(
            title="🔒 Fermer le Ticket ?",
            description="Êtes-vous sûr de vouloir fermer ce ticket ?\n" + (f"**Raison :** {reason}" if reason else ""),
            color=discord.Color.from_rgb(255, 193, 7)
        )
        
        await ctx.send(embed=embed, view=ConfirmView(self))
    
    @ticket.command(name="claim")
    async def ticket_claim_cmd(self, ctx):
        """Prend en charge le ticket"""
        await self.claim_ticket(ctx)
        
        embed = discord.Embed(
            title="✋ Ticket Pris en Charge",
            description=f"**{ctx.author.mention}** prend en charge ce ticket",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        await ctx.send(embed=embed)
    
    @ticket.command(name="add")
    async def ticket_add_cmd(self, ctx, user: discord.Member):
        """Ajoute un utilisateur au ticket"""
        try:
            await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
            
            embed = discord.Embed(
                title="➕ Utilisateur Ajouté",
                description=f"{user.mention} a été ajouté au ticket",
                color=discord.Color.from_rgb(40, 167, 69)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @ticket.command(name="remove")
    async def ticket_remove_cmd(self, ctx, user: discord.Member):
        """Retire un utilisateur du ticket"""
        try:
            await ctx.channel.set_permissions(user, overwrite=None)
            
            embed = discord.Embed(
                title="➖ Utilisateur Retiré",
                description=f"{user.mention} a été retiré du ticket",
                color=discord.Color.from_rgb(255, 193, 7)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @ticket.command(name="stats")
    @commands.has_permissions(administrator=True)
    async def ticket_stats(self, ctx):
        """Affiche les statistiques"""
        config = self.get_config(ctx.guild.id)
        
        open_count = len(config.get("open_tickets", {}))
        total_count = config.get("ticket_count", 0)
        
        embed = discord.Embed(
            title="📊 Statistiques des Tickets",
            description=f"Serveur : **{ctx.guild.name}**",
            color=discord.Color.from_rgb(0, 123, 255)
        )
        
        embed.add_field(name="🟢 Tickets Ouverts", value=f"`{open_count}`", inline=True)
        embed.add_field(name="📈 Total Créés", value=f"`{total_count}`", inline=True)
        embed.add_field(name="🔒 Total Fermés", value=f"`{total_count - open_count}`", inline=True)
        
        support_role_id = config.get("support_role_id")
        if support_role_id:
            support_role = ctx.guild.get_role(int(support_role_id))
            if support_role:
                embed.add_field(name="👥 Rôle Support", value=support_role.mention, inline=False)
        
        await ctx.send(embed=embed)


# ==================== VUES (BOUTONS) ====================

class TicketButtonsView(discord.ui.View):
    """Boutons du panel de tickets"""
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, emoji="💬", custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction, "support")
    
    @discord.ui.button(label="Signalement", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="ticket_report")
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction, "report")
    
    @discord.ui.button(label="Partenariat", style=discord.ButtonStyle.success, emoji="🤝", custom_id="ticket_partnership")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction, "partnership")
    
    @discord.ui.button(label="Autre", style=discord.ButtonStyle.secondary, emoji="📝", custom_id="ticket_other")
    async def other_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction, "other")


class TicketControlView(discord.ui.View):
    """Boutons de contrôle dans un ticket"""
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="Fermer", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.close_ticket(interaction)
    
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="✋", custom_id="ticket_claim_btn")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.claim_ticket(interaction)


async def setup(bot):
    cog = Tickets(bot)
    await bot.add_cog(cog)
    
    # Réenregistrer les vues persistantes
    bot.add_view(TicketButtonsView(cog))
    bot.add_view(TicketControlView(cog))
    
    print("✅ Système de tickets chargé avec succès !")