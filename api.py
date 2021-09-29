from flask import Flask
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from threading import Thread

# Creating the api
app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)


f = open('data.base','r')
quotes = f.read().split(',')
f.close()
"""Opening and reading quotes"""

f = open('sug.base','w')#database to hold suggessions

@app.route('/')#main endpoint to get a quote (no rate limits)
def samuel():
    return {"quote":quotes[random.randint(0,len(quotes))]}


@app.route('/submit/<data>')
@limiter.limit("20/minute")
def submit(data):
    f.write(f"{data},")
    return "200"

def run():
    app.run(deubug=True)


def keep_alive():
    server = Thread(target=run)
    server.start()