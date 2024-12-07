from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def start():
    return "<h1>Hello world.</h1><p>OK.</p>"
