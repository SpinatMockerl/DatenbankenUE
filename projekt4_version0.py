#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, redirect
import os

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
    Strasse varchar(50), HausNr int(3), TelefonNr int, PRIMARY KEY (SVNr))''')

curs.execute('''CREATE TABLE IF NOT EXISTS Telefonnummer( SVNr int(10), Telefon_nr int(12), \
    PRIMARY KEY (SVNr, Telefon_nr), FOREIGN KEY (SVNr) REFERENCES Personen(SVNr))''')

# insert data (if it does not exist)
try:
    curs.execute("INSERT INTO Person VALUES('1234567890', 'Laura', 'Lama', '2020', 'Wien', 'Zoostrasse', '20', '5555')")
except sqlite3.IntegrityError as error:
    print(error)
    print('Data does already exist')
# commit new stuff
connection.commit()

# close stuff
curs.close()
connection.close()

# Flask constructor: define application as Flask object
app = Flask(__name__)
app.secret_key = os.urandom(24)     # secret_key later used in session setup


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/returnHome', methods=["POST"])
def returnHome():
    return render_template('home.html')


@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        try:
            SvNr = request.form['SvNr']
            print(SvNr)
            with sqlite3.connect("DatabaseVersion0.db") as connection:
                curs = connection.cursor()
                curs.execute('SELECT SvNr FROM PERSON where SvNr = ?', (SvNr,) )
                SvNr_SQL = curs.fetchone()[0]
                print(SvNr_SQL)
                if int(SvNr) == int(SvNr_SQL):
                    session['SvNr'] = SvNr
                    return render_template('login.html')
        except:
            return render_template('register.html')
        finally:
            connection.close()


@app.route('/register', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def register():
    return render_template('register.html')


@app.route('/addPerson', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def addPerson():
    if request.method == "POST":
        SvNr = request.form['SvNr']
        Vorname = request.form["Vorname"]
        Nachname = request.form["Nachname"]
        PLZ = request.form["PLZ"]
        Ort = request.form["Ort"]
        Strasse = request.form["Strasse"]
        print(Strasse)
        HausNr = request.form["HausNr"]
        TelefonNr = request.form["TelefonNr"]

        try:
            connection = sqlite3.connect('DatabaseVersion0.db')
            curs = connection.cursor()
            curs.execute("INSERT INTO PERSON (SvNr, Vorname, Nachname, PLZ, Ort, Strasse, HausNr, TelefonNr) VALUES "
                         "(?, ?, ?, ?, ?, ?, ?, ?)", (SvNr, Vorname, Nachname, PLZ, Ort, Strasse, HausNr, TelefonNr))
            connection.commit()
            curs.close()
            print("Person was added to db")
            return render_template('addPerson.html')

        except sqlite3.IntegrityError as error:
            connection.rollback()
            print("Person was not added to db")
            return render_template('userExists.html')
        finally:
            connection.close()


if __name__ == '__main__':
    # Flask .run() function: runs application on local development server
    # debug = True will automatically update site when code changes
    app.run(debug=True)
