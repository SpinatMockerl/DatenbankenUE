#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, redirect, g
import os


# Flask constructior: define application as Flask object
app = Flask(__name__)
app.secret_key = os.urandom(24) # secret_key later used in session setup

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        session.pop('SvNr', None)
        try:
            SvNr = request.form['SvNr']
            print(SvNr)
            with sqlite3.connect("first.db") as connection:
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
        return render_template(('register.html'))

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
        #TelefonNr = request.form["TelefonNr"]

        try:
            connection = sqlite3.connect('first.db')
            curs = connection.cursor()
            curs.execute("INSERT INTO PERSON (SvNr, Vorname, Nachname, PLZ, Ort, Strasse, HausNr) VALUES (?, ?, ?, ?, ?, ?, ?)", (SvNr, Vorname, Nachname, PLZ, Ort, Strasse, HausNr))
            connection.commit()
            curs.close()

            return render_template(('home.html'))

        except sqlite3.IntegrityError as error:
            connection.rollback()
            return render_template(('home.html'))
        finally:
            connection.close()

@app.route('/login_p', methods=["POST"])
def login_p():
    if g.SvNr:
        return render_template('dummyTemplate.html')
    return 'Not logged in'



# before request
@app.before_request
def before_request():
    g.SvNr = None
    if 'SvNr' in session:
        g.SvNr = session['SvNr']
# teardown in case something goes wrong

@app.route('/logout', methods=["POST"])
def logout():
    session.pop('SvNr', None)
    return "Logout was successful"


if __name__ == '__main__':
    # Flask .run() function: runs application on local developent server
    # debug = True will autoatically update site when code changes
    app.run(debug = True)
