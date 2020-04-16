import os
from flask import Flask, session, request, render_template, redirect, url_for, abort, jsonify
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

# function to deal with quotes in SQL queries
def SQLquotes(str):
    if "'" in  str:
        return str.replace("'", "''")
    else:
        return str

app = Flask(__name__)

# Check for DATABASE_URL variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Load config
app.config.from_pyfile('config.cfg', silent=True)  # load settings from config.cfg
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
print('database connected')

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/", methods=['POST'])
def home():
    post_data = request.get_json()
    score = post_data['score']
    # check user's captcha score
    if score > 0.5:
        # escape ' character in comment
        post_data['comment'] = SQLquotes(post_data['comment'])
        print(f"new incident form submission: {post_data['type']}, {post_data['date']}, {post_data['community']}, {post_data['comment']}")
        return jsonify(status='success')
    else:
        print(f"reCaptcha score too low {score}")
        return jsonify(status='fail',comment='score too low')

@app.route("/cap", methods=['POST'])
def cap():
    if session.get("capScore") is None:  # initialize reCaptcha score to 0
        session["capScore"] = 0

    post_data = request.get_json()
    print(f"reCaptcha: {post_data['response']}")
    secretkey = '6LedK-oUAAAAAGdGu2rzhxww8Ud4eNJ4P_dJ0HiH'
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', params={'secret': secretkey, 'response':post_data['response']})
    r = r.json()
    print(r)
    session["capScore"] = r['score']
    session.modified = True
    print(session["capScore"])
    return r



if __name__ == '__main__':
    app.run()