import os
from flask import Flask, send_from_directory
from auth import requires_auth

app = Flask(__name__)

@app.route("/")
@requires_auth
def hello():
    return send_from_directory('build', 'index.html')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
