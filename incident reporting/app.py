import os
from flask import Flask, session, request, render_template, redirect, url_for, abort, jsonify
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

@app.route("/", methods=['GET', 'POST'])
def home():
    # normal page load
    if request.method == "GET":
        return render_template('home.html')
    # incident form submission
    else:
        type = request.form.get('type')
        date = request.form.get('popup-date')
        comment = request.form.get('comment')
        # escape ' character in comment
        comment = SQLquotes(comment)

        print(f"new incident form submission: {type}, {date}, {comment}")
        return render_template('home.html', alertmsg="Submission sent!")




if __name__ == '__main__':
    app.run(host='0.0.0.0')