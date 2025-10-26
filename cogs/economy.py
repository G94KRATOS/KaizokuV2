# cogs/economy.py
import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "economy.json"
SHOP_FILE = "shop.json"

def load_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_json(DATA_FILE)
        self.shop = load_json(SHOP_FILE)

    # --- Gestion XP et coins automatiques ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user = str(message.author.id)
        if user not in self.data:
            self.data[user] = {"xp": 0, "coins": 0, "last_daily": None}
        self.data[user]["xp"] += 1
        self.data[user]["coins"] += 1
        save_json(DATA_FILE, self.data)

    # --- Profil utilisateur ---
    @commands.command()
    async def profil(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user = str(member.id)
        coins = self.data.get(user, {}).get("coins", 0)
        xp = self.data.get(user, {}).get("xp", 0)
        embed = discord.Embed(title=f"Profil de {member}", color=discord.Color.green())
        embed.add_field(name="XP", value=xp)
        embed.add_field(name="Coins", value=coins)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)

    # --- Récompense journalière ---
    @commands.command()
    async def daily(self, ctx):
        user = str(ctx.author.id)
        if user not in self.data:
            self.data[user] = {"xp": 0, "coins": 0, "last_daily": None}

        last = self.data[user].get("last_daily")
        now = datetime.utcnow()

        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_dt)
                await ctx.send(f"⏳ Vous avez déjà récupéré votre daily ! Temps restant : {remaining}")
                return

        reward = 100
        self.data[user]["coins"] += reward
        self.data[user]["last_daily"] = now.isoformat()
        save_json(DATA_FILE, self.data)
        await ctx.send(f"✅ {ctx.author.mention}, vous avez reçu **{reward} coins** !")

    # --- Transfert de coins ---
    @commands.command()
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ Montant invalide.")
            return
        sender = str(ctx.author.id)
        receiver = str(member.id)
        if sender not in self.data or self.data[sender]["coins"] < amount:
            await ctx.send("❌ Vous n'avez pas assez de coins.")
            return
        if receiver not in self.data:
            self.data[receiver] = {"xp": 0, "coins": 0, "last_daily": None}

        self.data[sender]["coins"] -= amount
        self.data[receiver]["coins"] += amount
        save_json(DATA_FILE, self.data)
        await ctx.send(f"💸 {ctx.author.mention} a donné {amount} coins à {member.mention} !")

    # --- Leaderboard ---
    @commands.command()
    async def leaderboard(self, ctx):
        sorted_data = sorted(self.data.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
        embed = discord.Embed(title="🏆 Top 10 Coins", color=discord.Color.gold())
        for i, (user_id, stats) in enumerate(sorted_data, start=1):
            user = self.bot.get_user(int(user_id))
            name = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{i}. {name}", value=f"{stats['coins']} coins", inline=False)
        await ctx.send(embed=embed)

    # --- Admin commands ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        user = str(member.id)
        if user not in self.data:
            self.data[user] = {"xp": 0, "coins": 0, "last_daily": None}
        self.data[user]["coins"] += amount
        save_json(DATA_FILE, self.data)
        await ctx.send(f"✅ {amount} coins ajoutés à {member.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removecoins(self, ctx, member: discord.Member, amount: int):
        user = str(member.id)
        if user not in self.data:
            self.data[user] = {"xp": 0, "coins": 0, "last_daily": None}
        self.data[user]["coins"] = max(self.data[user]["coins"] - amount, 0)
        save_json(DATA_FILE, self.data)
        await ctx.send(f"✅ {amount} coins retirés de {member.mention}.")

    # --- Boutique ---
    @commands.command()
    async def shop(self, ctx):
        if not self.shop:
            await ctx.send("La boutique est vide pour le moment.")
            return
        embed = discord.Embed(title="🛒 Boutique", color=discord.Color.blue())
        for item, price in self.shop.items():
            embed.add_field(name=item, value=f"{price} coins", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, *, item):
        user = str(ctx.author.id)
        if item not in self.shop:
            await ctx.send("❌ Cet item n'existe pas dans la boutique.")
            return
        price = self.shop[item]
        if self.data.get(user, {}).get("coins", 0) < price:
            await ctx.send("❌ Vous n'avez pas assez de coins.")
            return
        self.data[user]["coins"] -= price
        # Tu peux ajouter ici un inventaire si tu veux
        save_json(DATA_FILE, self.data)
        await ctx.send(f"✅ {ctx.author.mention} a acheté **{item}** pour {price} coins !")

    # --- Admin ajouter item boutique ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addshop(self, ctx, item, price: int):
        self.shop[item] = price
        save_json(SHOP_FILE, self.shop)
        await ctx.send(f"✅ L'item **{item}** a été ajouté à la boutique pour {price} coins.")

async def setup(bot):
    await bot.add_cog(Economy(bot))
