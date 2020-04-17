import os
from flask import Flask, session, request, render_template, redirect, url_for, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
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
md = MetaData()
print('database connected')

# open Community_Crime_Statistics.csv [Community Name	Category	Crime Count	Date]
file = './Community_Crime_Statistics.csv'
tablename = 'calgarycrimedata'
colnames = ['Community', 'Category', 'Count', 'Date']
# get table primary key from database
table = Table(tablename, md, autoload=True, autoload_with=engine)

f = open(file, "r")  # open file
nrows = sum(1 for row in f)  # get number of rows
f = open(file, "r")  # reopen file
reader = csv.reader(f)

line = -1
for row in reader:
    line += 1

    if (line % 100) == 0:
        print("Progress: %(percent)s%%" % {'percent': line / nrows * 100})
    # at first row (assuming csv contains headings)
    if line == 0:
        continue

    # get values from first row
    values = []
    for value in row:
        values.append(SQLquotes(value)) # escape ' characters
    # check if row already exists in database
    command = "Select Count(*) from CalgaryCrimeData where Community='%(value1)s' And Category='%(value2)s' And Date='%(value4)s'" % {
        'value1': values[0], 'value2': values[1], 'value4': values[3]}
    num = db.execute(command).fetchall()
    if num[0][0] > 0:
        print("Skipping row: " + str(row) + " as it already exists in database")
        continue

    # construct INSERT SQL command from csv
    command = "INSERT INTO %(tablename)s(Community, Category, Count, Date) VALUES('%(value1)s', '%(value2)s', '%(value3)s', '%(value4)s')" % {
        'tablename': tablename, 'value1': values[0], 'value2': values[1], 'value3': values[2], 'value4': values[3]}

    db.execute(command)
    db.commit()
