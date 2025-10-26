import subprocess
import sys
import time

while True:
    print("🔄 Lancement du bot...")
    result = subprocess.run([sys.executable, "bot.py"])
    print(f"⚠️ Bot arrêté avec le code {result.returncode}, redémarrage dans 5 secondes...")
    time.sleep(5)
