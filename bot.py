import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import signal
import sys
import atexit
import time
from datetime import datetime

# keep_alive n'est plus nécessaire car Gunicorn démarre dans le Procfile

# Charger le token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Token Discord non trouvé !")
    sys.exit(1)

# Protection anti-double instance (OPTIMISÉ pour Render)
LOCK_FILE = "/tmp/discord_bot.lock"

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        print("⚠️ Instance déjà en cours, nettoyage...")
        try:
            os.remove(LOCK_FILE)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer le lock : {e}")
            print("✅ Tentative de démarrage malgré tout (normal sur Render)...")
    
    try:
        os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        print(f"🔒 Lock acquis (PID: {os.getpid()})")
        return True
    except Exception as e:
        print(f"⚠️ Erreur lock (ignorée) : {e}")
        return True  # On continue quand même sur Render

def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print("🔓 Lock libéré")
    except Exception as e:
        print(f"⚠️ Erreur libération lock : {e}")

atexit.register(release_lock)

# Intents
intents = discord.Intents.all()

# Bot sans help par défaut
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# Variables de contrôle
bot._ready_fired = False
bot._processed_commands = {}  # Track des commandes traitées

# Protection ULTIME anti-double
@bot.event
async def on_message(message):
    # Ignorer les bots
    if message.author.bot:
        return
    
    # Ne traiter QUE les messages avec préfixe
    if not message.content.startswith(bot.command_prefix):
        return
    
    # Créer une clé unique (message + auteur)
    msg_key = f"{message.id}_{message.author.id}"
    current_time = time.time()
    
    # Nettoyer les anciennes entrées (> 10 secondes)
    bot._processed_commands = {
        k: v for k, v in bot._processed_commands.items()
        if current_time - v < 10
    }
    
    # Vérifier si déjà traité
    if msg_key in bot._processed_commands:
        elapsed = current_time - bot._processed_commands[msg_key]
        print(f"🚫 COMMANDE BLOQUÉE (déjà traitée il y a {elapsed:.2f}s) - ID: {message.id}")
        return
    
    # Marquer comme traité AVANT de process
    bot._processed_commands[msg_key] = current_time
    
    print(f"✅ Commande traitée (ID: {message.id}) - {message.content[:50]}")
    
    # Traiter UNE SEULE fois
    await bot.process_commands(message)

# Event ready
@bot.event
async def on_ready():
    if bot._ready_fired:
        print("⚠️ on_ready déjà exécuté, ignoré")
        return
    
    bot._ready_fired = True
    
    # Enregistrer l'heure de démarrage pour le système de statut
    bot.uptime = datetime.utcnow()
    
    print("=" * 50)
    print(f"✅ Bot connecté : {bot.user} (ID: {bot.user.id})")
    print(f"📊 Serveurs : {len(bot.guilds)}")
    print(f"👥 Utilisateurs : {sum(g.member_count for g in bot.guilds)}")
    print(f"🔗 Latence : {round(bot.latency * 1000)}ms")
    print(f"🆔 Process ID : {os.getpid()}")
    print(f"🌐 Environnement : {'Render' if os.getenv('RENDER') else 'Local'}")
    print("=" * 50)
    
    # Avatar (optionnel)
    try:
        if os.path.exists("avatar.png"):
            with open("avatar.png", "rb") as f:
                avatar = f.read()
            await bot.user.edit(avatar=avatar)
            print("🖼️ Avatar mis à jour")
    except Exception as e:
        print(f"⚠️ Erreur avatar : {e}")

    # Configure le statut "Joue à +help"
    await bot.change_presence(
        activity=discord.Game(name="+help"),
        status=discord.Status.online
    )
    
    print("🚀 Bot opérationnel !\n")

# Logger les commandes
@bot.event
async def on_command(ctx):
    print(f"📝 Cmd: +{ctx.command.name} | {ctx.author} | Msg: {ctx.message.id}")

# Cogs à charger
COGS = [
    "cogs.help",
    "cogs.logs",
    "cogs.basic",
    "cogs.admin",
    "cogs.utils",
    "cogs.moderation",
    "cogs.fun",
    "cogs.economy",
    "cogs.giveaway",
    "cogs.gestion",
    "cogs.error",
    "cogs.permsystem",
    "cogs.logger",
    "cogs.tickets",
    "cogs.status",
    "cogs.owner"
]

# Chargement des cogs
async def load_cogs():
    print("\n📦 Chargement des cogs...")
    print("-" * 50)
    
    loaded = 0
    failed = []
    
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ {cog}")
            loaded += 1
        except commands.ExtensionNotFound:
            print(f"  ❌ {cog} : Introuvable")
            failed.append(cog)
        except commands.ExtensionAlreadyLoaded:
            print(f"  ⚠️ {cog} : Déjà chargé")
        except Exception as e:
            print(f"  ❌ {cog} : {e}")
            failed.append(cog)
    
    print("-" * 50)
    print(f"📊 {loaded}/{len(COGS)} cogs chargés")
    
    if failed:
        print(f"⚠️ Échecs : {', '.join(failed)}")
    
    print()

# Gestion arrêt propre
def handle_exit(signum, frame):
    print(f"\n🛑 Signal {signum}, arrêt propre...")
    release_lock()
    asyncio.create_task(shutdown())

async def shutdown():
    print("🔄 Fermeture...")
    await bot.close()
    print("✅ Bot arrêté proprement")

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Démarrage
async def start_bot():
    async with bot:
        await load_cogs()
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            print("❌ Token invalide !")
            release_lock()
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur démarrage : {e}")
            release_lock()
            sys.exit(1)

# Point d'entrée
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║     🤖 DÉMARRAGE DU BOT DISCORD     ║
    ╚══════════════════════════════════════╝
    """)
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis !")
        sys.exit(1)
    
    acquire_lock()
    
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel (Ctrl+C)")
        release_lock()
    except Exception as e:
        print(f"\n💥 ERREUR FATALE : {type(e).__name__}")
        print(f"   Message : {e}")
        release_lock()
        sys.exit(1)
    finally:
        release_lock()
        print("\n👋 Bot terminé")