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

def SQLSanatize(str):
    badchars = '(){}[]"'
    badchars = badchars + "'"
    for i in badchars:
        str = str.replace(i,'')
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
        # send data to database
        db.execute("INSERT INTO CrimeReviews (Community, Category, Date, Comment) VALUES (:Com, :Cat, :Dat, :Comm)",
                   {"Com": post_data['community'], "Cat": post_data['type'], "Dat": post_data['date'], "Comm": post_data['comment']})
        db.commit()

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

@app.route("/query", methods=['GET'])
def query():
    community = request.args.get('community')
    date = request.args.get('date')
    incident = request.args.get('incident')
    # get rid of invalid characters
    community = SQLSanatize(community)
    date = SQLSanatize(date)
    incident = SQLSanatize(incident)
    #print(f"Query: Communities:{community} Incidents: {incident}, years: {date}")

    # Create query command
    command = "Select * from CalgaryCrimeData where"
    if community != '':
        command = command + " LOWER(Community) IN ("
        s = community.split(',')
        for i in s:
            command = command + "LOWER('" + i + "'), "
        command = command[:-2]
        command = command + ")"
        if incident != '' or date != '':
            command = command + " AND"


    if incident != '':
        command = command + " LOWER(Category) IN ("
        s = incident.split(',')
        for i in s:
            command = command + "LOWER('" + i + "'), "
        command = command[:-2]
        command = command + ")"
        if date != '':
            command = command + " AND"

    if date != '':
        command = command + " date_part('year',Date) IN ("
        s = date.split(',')
        for i in s:
            command = command + i + ", "
        command = command[:-2]
        command = command + ")"
    print(command)

    # submit the query to psql
    data = db.execute(command).fetchall()
    print('response!')

    # convert to json
    data_dict = [dict(row) for row in data]


    return jsonify(status='success', data=data_dict)



if __name__ == '__main__':
    app.run()