import subprocess
import time
import os

flask_process = None

def keep_alive():
    """Démarre Gunicorn avec Flask dans un processus séparé"""
    global flask_process
    
    port = os.environ.get('PORT', '10000')
    
    print("\n" + "=" * 60)
    print("🚀 DÉMARRAGE DU SERVEUR WEB (Gunicorn)")
    print(f"   Port: {port}")
    print("=" * 60)
    
    try:
        # Démarrer Gunicorn en arrière-plan
        flask_process = subprocess.Popen([
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',
            '--timeout', '120',
            '--log-level', 'info',
            'wsgi:app'
        ])
        
        print(f"✅ Gunicorn démarré (PID: {flask_process.pid})")
        print(f"   Le serveur écoute sur http://0.0.0.0:{port}")
        print("=" * 60 + "\n")
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        return flask_process
        
    except Exception as e:
        print(f"❌ ERREUR lors du démarrage de Gunicorn: {e}")
        import traceback
        traceback.print_exc()
        return None

def stop_flask():
    """Arrête le serveur Flask"""
    global flask_process
    if flask_process:
        print("\n🛑 Arrêt du serveur web...")
        flask_process.terminate()
        flask_process.wait()
        print("✅ Serveur web arrêté\n")