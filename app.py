from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Servidor funcionando correctamente en Railway!"

if __name__ == "__main__":
    from waitress import serve
    import os
    print("🚀 Servidor iniciando en http://0.0.0.0:5000")
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
