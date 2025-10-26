from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Discord</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin: 0; }
            p { font-size: 1.2em; margin: 10px 0; }
            .status { 
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #00ff00;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot Discord</h1>
            <p><span class="status"></span> Bot en ligne et opérationnel</p>
            <p>Préfixe des commandes : <strong>+</strong></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "bot": "running",
        "service": "discord-bot"
    }, 200

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)