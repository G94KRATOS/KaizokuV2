import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_perms_cog(self):
        """Récupère le cog de permissions"""
        return self.bot.get_cog("PermissionsSystem")
    
    async def find_member(self, ctx, user_input: str):
        """Trouve un membre par mention, ID, pseudo ou nom"""
        # Par mention
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = user_input.strip('<@!>')
            try:
                return await ctx.guild.fetch_member(int(user_id))
            except:
                return None
        
        # Par ID
        if user_input.isdigit():
            try:
                return await ctx.guild.fetch_member(int(user_input))
            except:
                return None
        
        # Par pseudo ou nom (insensible à la casse)
        user_input_lower = user_input.lower()
        for member in ctx.guild.members:
            if (member.name.lower() == user_input_lower or 
                member.display_name.lower() == user_input_lower or
                user_input_lower in member.name.lower() or
                user_input_lower in member.display_name.lower()):
                return member
        
        return None
    
    # ==================== BAN/UNBAN (GS - Niveau 3) ====================
    
    @commands.command(name="ban", aliases=["b"])
    async def ban_member(self, ctx, user: str, *, reason: str = "Aucune raison fournie"):
        """Ban un membre - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        # Trouve le membre
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        # Vérifie la hiérarchie
        can_moderate, error_msg = perms_cog.can_moderate_target(ctx.author, member)
        if not can_moderate:
            return await ctx.send(f"❌ {error_msg}")
        
        try:
            await member.ban(reason=f"[{ctx.author}] {reason}")
            
            embed = discord.Embed(
                title="🔨 Membre banni",
                description=f"{member.mention} a été banni du serveur.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de bannir ce membre (vérifiez la hiérarchie des rôles).")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="unban", aliases=["ub"])
    async def unban_member(self, ctx, user_id: str, *, reason: str = "Aucune raison"):
        """Unban un membre - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        try:
            user_id_int = int(user_id.strip('<@!>'))
            user = await self.bot.fetch_user(user_id_int)
            
            await ctx.guild.unban(user, reason=f"[{ctx.author}] {reason}")
            
            embed = discord.Embed(
                title="✅ Membre débanni",
                description=f"{user.mention} a été débanni.",
                color=discord.Color.green()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ ID utilisateur invalide.")
        except discord.NotFound:
            await ctx.send("❌ Cet utilisateur n'est pas banni.")
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de débannir.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="banlist", aliases=["bans"])
    async def ban_list(self, ctx):
        """Liste des membres bannis - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        try:
            bans = [entry async for entry in ctx.guild.bans(limit=100)]
            
            if not bans:
                return await ctx.send("✅ Aucun membre banni.")
            
            embed = discord.Embed(
                title=f"🔨 Liste des bannis ({len(bans)})",
                color=discord.Color.red()
            )
            
            ban_list = []
            for ban_entry in bans[:20]:  # Limite à 20 pour éviter le spam
                user = ban_entry.user
                reason = ban_entry.reason or "Aucune raison"
                ban_list.append(f"**{user}** (`{user.id}`)\n└ *{reason}*")
            
            embed.description = "\n\n".join(ban_list)
            if len(bans) > 20:
                embed.set_footer(text=f"Affichage limité à 20/{len(bans)} bannis")
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de voir les bannis.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== KICK (Modérateur - Niveau 2) ====================
    
    @commands.command(name="kick", aliases=["k"])
    async def kick_member(self, ctx, user: str, *, reason: str = "Aucune raison fournie"):
        """Kick un membre - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        can_moderate, error_msg = perms_cog.can_moderate_target(ctx.author, member)
        if not can_moderate:
            return await ctx.send(f"❌ {error_msg}")
        
        try:
            await member.kick(reason=f"[{ctx.author}] {reason}")
            
            embed = discord.Embed(
                title="👢 Membre expulsé",
                description=f"{member.mention} a été expulsé du serveur.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de kick ce membre.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== MUTE/TIMEOUT (Modérateur - Niveau 2) ====================
    
    @commands.command(name="mute", aliases=["m"])
    async def mute_member(self, ctx, user: str, duration: int = 10, *, reason: str = "Aucune raison"):
        """Mute un membre - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        can_moderate, error_msg = perms_cog.can_moderate_target(ctx.author, member)
        if not can_moderate:
            return await ctx.send(f"❌ {error_msg}")
        
        if duration < 1 or duration > 40320:  # Max 28 jours
            return await ctx.send("❌ Durée invalide (1 minute à 40320 minutes / 28 jours).")
        
        try:
            await member.timeout(timedelta(minutes=duration), reason=f"[{ctx.author}] {reason}")
            
            embed = discord.Embed(
                title="🔇 Membre mute",
                description=f"{member.mention} a été mute pendant **{duration} minutes**.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de timeout ce membre.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="unmute", aliases=["um"])
    async def unmute_member(self, ctx, user: str):
        """Unmute un membre - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        try:
            await member.timeout(None, reason=f"Unmute par {ctx.author}")
            
            embed = discord.Embed(
                title="🔊 Membre unmute",
                description=f"{member.mention} peut à nouveau parler.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de retirer le timeout.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="timeout", aliases=["to"])
    async def timeout_member(self, ctx, user: str, duration: int, *, reason: str = "Aucune raison"):
        """Alias de mute - Nécessite niveau Modérateur (2)"""
        await self.mute_member(ctx, user, duration, reason=reason)
    
    @commands.command(name="untimeout", aliases=["uto"])
    async def untimeout_member(self, ctx, user: str):
        """Alias de unmute - Nécessite niveau Modérateur (2)"""
        await self.unmute_member(ctx, user)
    
    # ==================== CLEAR (Modérateur - Niveau 2) ====================
    
    @commands.command(name="clear", aliases=["purge", "clean"])
    async def clear_messages(self, ctx, amount: int):
        """Supprime des messages - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        if amount < 1 or amount > 100:
            return await ctx.send("❌ Vous devez spécifier un nombre entre 1 et 100.")
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"✅ {len(deleted) - 1} message(s) supprimé(s).")
            await msg.delete(delay=5)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer des messages.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== LOCK/UNLOCK (Modérateur - Niveau 2) ====================
    
    @commands.command(name="lock", aliases=["lockdown"])
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        """Verrouille un salon - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        channel = channel or ctx.channel
        
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                send_messages=False,
                reason=f"Salon verrouillé par {ctx.author}"
            )
            
            embed = discord.Embed(
                title="🔒 Salon verrouillé",
                description=f"{channel.mention} a été verrouillé.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de modifier ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="unlock")
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        """Déverrouille un salon - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        channel = channel or ctx.channel
        
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                send_messages=None,
                reason=f"Salon déverrouillé par {ctx.author}"
            )
            
            embed = discord.Embed(
                title="🔓 Salon déverrouillé",
                description=f"{channel.mention} a été déverrouillé.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de modifier ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="slowmode", aliases=["slow"])
    async def set_slowmode(self, ctx, seconds: int, channel: discord.TextChannel = None):
        """Définit le slowmode - Nécessite niveau Modérateur (2)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 2:
            return await ctx.send("❌ Cette commande nécessite le niveau **Modérateur** ou supérieur.")
        
        channel = channel or ctx.channel
        
        if seconds < 0 or seconds > 21600:
            return await ctx.send("❌ Le slowmode doit être entre 0 et 21600 secondes (6 heures).")
        
        try:
            await channel.edit(slowmode_delay=seconds, reason=f"Slowmode par {ctx.author}")
            
            if seconds == 0:
                embed = discord.Embed(
                    title="⏱️ Slowmode désactivé",
                    description=f"Le slowmode de {channel.mention} a été désactivé.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="⏱️ Slowmode activé",
                    description=f"Le slowmode de {channel.mention} : **{seconds} secondes**.",
                    color=discord.Color.blue()
                )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de modifier ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== GESTION DES RÔLES (GS - Niveau 3) ====================
    
    @commands.command(name="addrole")
    async def add_role(self, ctx, user: str, role: discord.Role):
        """Ajoute un rôle - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Ce rôle est trop haut dans la hiérarchie pour le bot.")
        
        try:
            await member.add_roles(role, reason=f"Ajouté par {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Rôle ajouté",
                description=f"Le rôle {role.mention} a été ajouté à {member.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission d'ajouter ce rôle.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="removerole")
    async def remove_role(self, ctx, user: str, role: discord.Role):
        """Retire un rôle - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Ce rôle est trop haut dans la hiérarchie.")
        
        try:
            await member.remove_roles(role, reason=f"Retiré par {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Rôle retiré",
                description=f"Le rôle {role.mention} a été retiré à {member.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de retirer ce rôle.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="nick")
    async def change_nickname(self, ctx, user: str, *, nickname: str = None):
        """Change le pseudo - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        try:
            old_nick = member.display_name
            await member.edit(nick=nickname, reason=f"Modifié par {ctx.author}")
            
            embed = discord.Embed(
                title="✏️ Pseudo modifié",
                description=f"Le pseudo de {member.mention} a été modifié.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Ancien", value=old_nick, inline=True)
            embed.add_field(name="Nouveau", value=nickname or "Réinitialisé", inline=True)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de modifier ce pseudo.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== WARN (Support - Niveau 1) ====================
    
    @commands.command(name="warn")
    async def warn_member(self, ctx, user: str, *, reason: str = "Aucune raison"):
        """Avertit un membre - Nécessite niveau Support (1)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 1:
            return await ctx.send("❌ Cette commande nécessite le niveau **Support** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        can_moderate, error_msg = perms_cog.can_moderate_target(ctx.author, member)
        if not can_moderate:
            return await ctx.send(f"❌ {error_msg}")
        
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"{member.mention} a reçu un avertissement.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)
        
        # Envoie un DM
        try:
            dm_embed = discord.Embed(
                title="⚠️ Avertissement",
                description=f"Vous avez reçu un avertissement sur **{ctx.guild.name}**.",
                color=discord.Color.gold()
            )
            dm_embed.add_field(name="Raison", value=reason, inline=False)
            dm_embed.add_field(name="Modérateur", value=ctx.author.name, inline=False)
            await member.send(embed=dm_embed)
        except:
            await ctx.send("⚠️ Impossible d'envoyer un message privé au membre.")
    
    # ==================== MEMBERINFO (Support - Niveau 1) ====================
    
    @commands.command(name="memberinfo", aliases=["mi", "whois"])
    async def member_info(self, ctx, user: str = None):
        """Affiche les infos d'un membre - Nécessite niveau Support (1)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 1:
            return await ctx.send("❌ Cette commande nécessite le niveau **Support** ou supérieur.")
        
        if user:
            member = await self.find_member(ctx, user)
            if not member:
                return await ctx.send(f"❌ Membre `{user}` introuvable.")
        else:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"👤 Informations sur {member.display_name}",
            color=member.color
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Pseudo", value=member.name, inline=True)
        embed.add_field(name="Surnom", value=member.display_name, inline=True)
        
        embed.add_field(name="Compte créé", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="A rejoint", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Rôle le plus haut", value=member.top_role.mention, inline=True)
        
        roles = [role.mention for role in member.roles[1:]][:10]
        embed.add_field(
            name=f"Rôles ({len(member.roles) - 1})",
            value=" ".join(roles) if roles else "Aucun rôle",
            inline=False
        )
        
        # Niveau de permission du bot
        level = perms_cog.get_user_level(member)
        embed.add_field(
            name="🔐 Niveau bot",
            value=f"**{perms_cog.hierarchy[level]}** (niveau {level})",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))