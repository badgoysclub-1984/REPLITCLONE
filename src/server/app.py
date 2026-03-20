"""Web server for REPLITCLONE"""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to REPLITCLONE"

if __name__ == "__main__":
    app.run(debug=True)
