#!/bin/python3

from flask import Flask, request
from waitress import serve

# Webhook location (ex: if URL is 873gear.com/webhook then locaiton is '/webhook')
WEBHOOK_LOCATION = "/webhook"

# Webhook port number
WEBHOOK_PORT = 3333

app = Flask(__name__)

@app.route(WEBHOOK_LOCATION, methods=["GET"])
def index():
    if request.method == "GET":
        do_stuff_and_things()

        success = """OK"""

        return success


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=WEBHOOK_PORT)