#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session
import os


#####################################################################################################################
# Tutorial: https://www.youtube.com/watch?v=o-vsdfCBpsU

# define connection, sqlite will create db file if not already there
connection = sqlite3.connect('DatabaseVersion0.db')

# define cursor
curs = connection.cursor()

# Create Tables
# enter sql statements in doc string format
curs.execute('''CREATE TABLE IF NOT EXISTS
    Person(SVNr int(10), Vorname varchar(10),
    Nachname varchar(10), PLZ int, Ort varchar(10),
    Straße varchar(50), HausNr int(3), TelefonNr int, PRIMARY KEY (SVNr))''')

curs.execute('''CREATE TABLE IF NOT EXISTS Telefonnummer( SVNr int(10), Telefon_nr int(12),
    PRIMARY KEY (SVNr, Telefon_nr), FOREIGN KEY (SVNr) REFERENCES Personen(SVNr))''')

# insert data (if it does not exist)
try:
    curs.execute('''INSERT INTO Person VALUES('1234567890', 'Laura', 'Lama', '2020', 'Wien', 'Zoostraße', '20', '5555')''')
except sqlite3.IntegrityError as error:
    print(error)
    print('Data does already exist')
# commit new stuff
connection.commit()

# close stuff
curs.close()
connection.close()
#####################################################################################################################
# insert into person table by filling out html form


# Flask constructior: define application as Flask object
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Flask route() function: tells app which URL should be called
# used to bind URL to function ( also possible with .add_url_rule() )
@app.route('/home')
def home():
    return render_template(('home.html'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        SvNr = request.form['SvNr']

        try:
            ## Error: TypeError: View function did not have valid response
            connection = sqlite3.connect('DatabaseVersion0.db')
            curs = connection.cursor()
            curs.execute('SELECT SvNr FROM PERSON where SvNr = ?', (SvNr,) )
            SvNr_SQL = curs.fetchone()[0]
            print(SvNr_SQL)
            print(SvNr)
            connection.commit()
            connection.close()
            if SvNr == SvNr_SQL:
                session['SvNr'] = SvNr
                return 'User exists'
                #return render_template(('person.html'))
        except TypeError as error:
            return render_template('register.html')


@app.route('/register', methods=["GET", "POST"])
# mehrere Telefon nummer nicht implementiert
def register():
    return render_template(('register.html'))

@app.route('/addPerson', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def register():
    SvNr = request.form['SvNr']
    Vorname = request.form["Vorname"]
    PLZ = request.form["PLZ"]
    Ort = request.form["Ort"]
    Straße = request.form["Straße"]
    HausNr = request.form["HausNr"]
    TelefonNr = request.form["TelefonNr"]

    # test if SvNr is already in DB

    try:
        connection = sqlite3.connect('DatabaseVersion0.db')
        curs = connection.cursor()
        curs.execute('''INSERT INTO Person IF NOT EXISTS VALUES('9876543210', 'Insert', 'Person', '2000', 'Wels', 'Zoostraße', '20', '5555')''')
        curs.commit()
        curs.close()
        connection.close()
        return render_template('addPerson.html')
    except sqlite3.IntegrityError as error:
        return 'Data does already exist'




@app.route('/userEnvironment')
def userEnvironment():
    identification = request.cookies.get('SvNr')
    return '<h1>welcome ' + identification + '</h1>'


#@app.route('/insertPerson')
# access page: http://localhost:5000/insertPerson
#def newPerson():
#    return render_template('person.html')





if __name__ == '__main__':
    # Flask .run() function: runs application on local developent server
    # debug = True will autoatically update site when code changes
    app.run(debug = True)
