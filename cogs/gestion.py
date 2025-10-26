import discord
from discord.ext import commands
from datetime import datetime

class Gestion(commands.Cog):
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
        
        # Par pseudo ou nom
        user_input_lower = user_input.lower()
        for member in ctx.guild.members:
            if (member.name.lower() == user_input_lower or 
                member.display_name.lower() == user_input_lower or
                user_input_lower in member.name.lower() or
                user_input_lower in member.display_name.lower()):
                return member
        
        return None
    
    # ==================== GESTION DES SALONS (GS - Niveau 3) ====================
    
    @commands.command(name="createchannel", aliases=["createchan"])
    async def create_channel(self, ctx, channel_type: str, *, name: str):
        """Crée un salon (text/voice) - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        channel_type = channel_type.lower()
        
        try:
            if channel_type in ["text", "txt", "t"]:
                channel = await ctx.guild.create_text_channel(
                    name=name,
                    reason=f"Créé par {ctx.author}"
                )
                embed = discord.Embed(
                    title="✅ Salon textuel créé",
                    description=f"{channel.mention} a été créé.",
                    color=discord.Color.green()
                )
            elif channel_type in ["voice", "vocal", "v"]:
                channel = await ctx.guild.create_voice_channel(
                    name=name,
                    reason=f"Créé par {ctx.author}"
                )
                embed = discord.Embed(
                    title="✅ Salon vocal créé",
                    description=f"**{channel.name}** a été créé.",
                    color=discord.Color.green()
                )
            else:
                return await ctx.send("❌ Type invalide. Utilisez `text` ou `voice`.")
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de créer des salons.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="deletechannel", aliases=["delchan"])
    async def delete_channel(self, ctx, channel: discord.TextChannel = None):
        """Supprime un salon - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        channel = channel or ctx.channel
        
        try:
            channel_name = channel.name
            await channel.delete(reason=f"Supprimé par {ctx.author}")
            
            if channel != ctx.channel:
                embed = discord.Embed(
                    title="✅ Salon supprimé",
                    description=f"Le salon **{channel_name}** a été supprimé.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="renamechannel", aliases=["renamechan"])
    async def rename_channel(self, ctx, channel: discord.TextChannel = None, *, new_name: str = None):
        """Renomme un salon - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if not new_name:
            return await ctx.send("❌ Vous devez spécifier un nouveau nom.")
        
        channel = channel or ctx.channel
        
        try:
            old_name = channel.name
            await channel.edit(name=new_name, reason=f"Renommé par {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Salon renommé",
                description=f"**{old_name}** → **{new_name}**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de renommer ce salon.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== GESTION DES RÔLES (GS - Niveau 3) ====================
    
    @commands.command(name="createrole")
    async def create_role(self, ctx, *, name: str):
        """Crée un rôle - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        try:
            role = await ctx.guild.create_role(
                name=name,
                reason=f"Créé par {ctx.author}"
            )
            
            embed = discord.Embed(
                title="✅ Rôle créé",
                description=f"{role.mention} a été créé.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de créer des rôles.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="deleterole")
    async def delete_role(self, ctx, role: discord.Role):
        """Supprime un rôle - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Ce rôle est trop haut dans la hiérarchie.")
        
        try:
            role_name = role.name
            await role.delete(reason=f"Supprimé par {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Rôle supprimé",
                description=f"Le rôle **{role_name}** a été supprimé.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer ce rôle.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="editrole")
    async def edit_role(self, ctx, role: discord.Role, option: str, *, value: str):
        """Modifie un rôle (name/color) - Nécessite niveau GS (3)
        Exemple: !editrole @Role name Nouveau Nom
                 !editrole @Role color #FF5733"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Ce rôle est trop haut dans la hiérarchie.")
        
        try:
            if option.lower() == "name":
                old_name = role.name
                await role.edit(name=value, reason=f"Modifié par {ctx.author}")
                embed = discord.Embed(
                    title="✅ Nom du rôle modifié",
                    description=f"**{old_name}** → **{value}**",
                    color=discord.Color.blue()
                )
            elif option.lower() == "color" or option.lower() == "colour":
                value = value.strip('#')
                color = discord.Color(int(value, 16))
                await role.edit(color=color, reason=f"Modifié par {ctx.author}")
                embed = discord.Embed(
                    title="✅ Couleur du rôle modifiée",
                    description=f"{role.mention} a maintenant la couleur `#{value}`",
                    color=color
                )
            else:
                return await ctx.send("❌ Option invalide. Utilisez `name` ou `color`.")
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Couleur invalide. Format: #RRGGBB")
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de modifier ce rôle.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    # ==================== GESTION MASS ACTIONS (GS - Niveau 3) ====================
    
    @commands.command(name="massrole")
    async def mass_role(self, ctx, action: str, role: discord.Role, *, target: str = None):
        """Ajoute/retire un rôle en masse - Nécessite niveau GS (3)
        Exemples: !massrole add @Role all
                  !massrole remove @Role bots
                  !massrole add @Role humans"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Ce rôle est trop haut dans la hiérarchie.")
        
        action = action.lower()
        if action not in ["add", "remove", "give", "take"]:
            return await ctx.send("❌ Action invalide. Utilisez `add` ou `remove`.")
        
        # Détermine les cibles
        target = (target or "all").lower()
        if target in ["all", "tous", "everyone"]:
            members = ctx.guild.members
        elif target in ["bots", "bot"]:
            members = [m for m in ctx.guild.members if m.bot]
        elif target in ["humans", "humains", "users"]:
            members = [m for m in ctx.guild.members if not m.bot]
        else:
            return await ctx.send("❌ Cible invalide. Utilisez `all`, `bots` ou `humans`.")
        
        msg = await ctx.send(f"⏳ Traitement en cours...")
        
        success = 0
        failed = 0
        
        try:
            for member in members:
                try:
                    if action in ["add", "give"]:
                        if role not in member.roles:
                            await member.add_roles(role, reason=f"Mass role par {ctx.author}")
                            success += 1
                    else:
                        if role in member.roles:
                            await member.remove_roles(role, reason=f"Mass role par {ctx.author}")
                            success += 1
                except:
                    failed += 1
            
            embed = discord.Embed(
                title="✅ Action en masse terminée",
                description=f"Rôle: {role.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="✅ Réussis", value=str(success), inline=True)
            embed.add_field(name="❌ Échoués", value=str(failed), inline=True)
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ Erreur : {e}")
    
    # ==================== INFORMATIONS SERVEUR (GS - Niveau 3) ====================
    
    @commands.command(name="servinfo", aliases=["sinfo"])
    async def server_info(self, ctx):
        """Affiche les infos du serveur - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 Informations sur {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="👑 Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="📅 Créé le", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)
        
        embed.add_field(name="👥 Membres", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="📝 Salons", value=f"{len(guild.text_channels)} textuels\n{len(guild.voice_channels)} vocaux", inline=True)
        embed.add_field(name="🎭 Rôles", value=f"{len(guild.roles)}", inline=True)
        
        embed.add_field(name="🔐 Niveau de vérification", value=str(guild.verification_level).capitalize(), inline=True)
        embed.add_field(name="💬 Notifications", value=str(guild.default_notifications).replace('_', ' ').title(), inline=True)
        
        boosts = guild.premium_subscription_count
        level = guild.premium_tier
        embed.add_field(name="✨ Boosts", value=f"Niveau {level}\n{boosts} boosts", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="roleinfo", aliases=["ri"])
    async def role_info(self, ctx, role: discord.Role):
        """Affiche les infos d'un rôle - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        embed = discord.Embed(
            title=f"🎭 Informations sur {role.name}",
            color=role.color
        )
        
        embed.add_field(name="🆔 ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="🎨 Couleur", value=f"`{role.color}`", inline=True)
        embed.add_field(name="📊 Position", value=f"{role.position}", inline=True)
        
        embed.add_field(name="👥 Membres", value=f"{len(role.members)}", inline=True)
        embed.add_field(name="📌 Mentionnable", value="✅" if role.mentionable else "❌", inline=True)
        embed.add_field(name="🔄 Affiché séparément", value="✅" if role.hoist else "❌", inline=True)
        
        embed.add_field(name="📅 Créé le", value=f"<t:{int(role.created_at.timestamp())}:R>", inline=True)
        
        await ctx.send(embed=embed)
    
    # ==================== NETTOYAGE (GS - Niveau 3) ====================
    
    @commands.command(name="purgebots")
    async def purge_bots(self, ctx, limit: int = 100):
        """Supprime les messages des bots - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if limit < 1 or limit > 100:
            return await ctx.send("❌ La limite doit être entre 1 et 100.")
        
        try:
            deleted = await ctx.channel.purge(
                limit=limit,
                check=lambda m: m.author.bot
            )
            
            msg = await ctx.send(f"✅ {len(deleted)} message(s) de bots supprimé(s).")
            await msg.delete(delay=5)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer des messages.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="purgeuser")
    async def purge_user(self, ctx, user: str, limit: int = 100):
        """Supprime les messages d'un utilisateur - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        member = await self.find_member(ctx, user)
        if not member:
            return await ctx.send(f"❌ Membre `{user}` introuvable.")
        
        if limit < 1 or limit > 100:
            return await ctx.send("❌ La limite doit être entre 1 et 100.")
        
        try:
            deleted = await ctx.channel.purge(
                limit=limit,
                check=lambda m: m.author == member
            )
            
            msg = await ctx.send(f"✅ {len(deleted)} message(s) de {member.mention} supprimé(s).")
            await msg.delete(delay=5)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer des messages.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @commands.command(name="purgeembeds")
    async def purge_embeds(self, ctx, limit: int = 100):
        """Supprime les messages avec embeds - Nécessite niveau GS (3)"""
        perms_cog = self.get_perms_cog()
        if not perms_cog:
            return await ctx.send("❌ Système de permissions non chargé.")
        
        if perms_cog.get_user_level(ctx.author) < 3:
            return await ctx.send("❌ Cette commande nécessite le niveau **GS (Gestion)** ou supérieur.")
        
        if limit < 1 or limit > 100:
            return await ctx.send("❌ La limite doit être entre 1 et 100.")
        
        try:
            deleted = await ctx.channel.purge(
                limit=limit,
                check=lambda m: len(m.embeds) > 0
            )
            
            msg = await ctx.send(f"✅ {len(deleted)} message(s) avec embeds supprimé(s).")
            await msg.delete(delay=5)
            
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas la permission de supprimer des messages.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

async def setup(bot):
    await bot.add_cog(Gestion(bot))