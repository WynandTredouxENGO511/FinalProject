import os
from flask import Flask, session, request, render_template, redirect, url_for, abort, jsonify
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker

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
    response_object = {'status': 'success'}
    # incident form submission
    if request.method == "POST":
        post_data = request.get_json()
        # escape ' character in comment
        post_data['comment'] = SQLquotes(post_data['comment'])
        print(f"new incident form submission: {post_data['type']}, {post_data['date']}, {post_data['comment']}")
    return jsonify(response_object)





if __name__ == '__main__':
    app.run()