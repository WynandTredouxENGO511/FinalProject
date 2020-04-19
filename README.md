# FinalProject
Final project for the ENGO551 course during the Winter2020 semester
Authors: Wynand Tredoux, AAron Chen

## Files and Folders
	/backend - flask server that handles sql query requests from the frontend
		Community_Crime_Statistics.csv - crime data from https://data.calgary.ca/Health-and-Safety/Community-Crime-Statistics/78gh-n26t
		app.bat - run this to start flask server on windows
		app.py - python code for backend
		app.sh - run this to start flask server on linux/MaxOS (same as app.bat)
		config.cfg - configuration file for flask
		import_crime.py - python script to import Community_Crime_Statistics.csv
		requirements.txt - python requirements, install with pip install -r requirements.txt
		sql.txt - psql code to create tables used by the flask server
	/frontend - js frontend using vue and node.js
		/public - folder containing all files that need to be accessed by Vue
		/src - folder containing all js source code
			/assest - website logo
			/components - folder for .js files used by Vue
				leaflet.vue - js code for main map interface
				toolbar.vue - js code for everything besides the main map interface
			/plugins - folder for Vue plugins (we only used vuetify.js)
			App.vue - root of the Vue application
			main.js - js code to initialize App.vue
			babel.config.js - config for babel compiler
			package-lock.json/package.json - list of all vue dependencies to be installed when you run npm install\
			vue.config.js - config file for Vue
	/psql test - simple python code to check that flask can communicate with the psql server properly
  
## Installation
### Frontend

After cloning you need to install all the node modules (make sure you have node.js installed) by using the command

```console
npm install 
```

while in the /frontend directory. Once that is done installing to start the frontend development server use the command

```console
npm run serve
```

and the default address will be http://localhost:8080/. To close the server press CTRL + C or CTRL + D in the terminal.

### Backend

Make sure you have python 3 (version 3.6.9 was used for this project) and pip/pip3 installed. Navigate to /backend and run
```
pip install -r requirements.txt
```
or
```
pip3 install -r requirements.txt
```
Once that has finished, you need to install psql from https://www.postgresql.org/download/

This project assumes that your psql server is running on http://localhost:5432, and has a user `postgres` with password `ENGO551`. The postgres user's password can be changed by running `ALTER USER postgres WITH PASSWORD 'ENGO551';` in a psql terminal

To test that the psql server is working properly you can create/populate a test table by pasting the following commands into a psql terminal:
```
Create Table test(id SERIAL PRIMARY KEY,
name VARCHAR NOT NULL,
number SMALLINT);

INSERT INTO test(name, number) VALUES('testman',420);
INSERT INTO test(name, number) VALUES('testman2',421);
```
And run `app.bat` or `app.sh` under /psql test. You should see the following output:
```
database connected
[(1, 'testman', 420), (2, 'testman2', 421)]
```
Once you've verified that flask can communicate with your psql server you need to create the following 2 tables:
```
Create Table CalgaryCrimeData(
	Community VARCHAR(50) NOT NULL,
	Category VARCHAR(50) NOT NULL,
	Count INT NOT NULL,
	Date DATE NOT NULL,
	PRIMARY KEY(Community, Category, Date)
);

Create Table CrimeReviews(
	id SERIAL NOT NULL,
	Community VARCHAR(50) NOT NULL,
	Category VARCHAR(50) NOT NULL,
	Date DATE NOT NULL,
	Comment TEXT,
	PRIMARY KEY(id)
);
```
Then run `import_crime.py` with the environment variable `DATABASE_URL=postgresql://postgres:ENGO551@localhost/postgres` to populate the CalgaryCrimeData table with data from the Community_Crime_Statistics.csv

Now you can start the backend server by running `app.bat` or `app.sh` in /backend
