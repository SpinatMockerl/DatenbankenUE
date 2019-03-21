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
# To Do: enable get and redirect to home
def login():
    if request.method == "POST":
        session.pop('SvNr', None)
        try:
            SvNr = request.form['SvNr']
            with sqlite3.connect("first.db") as connection:
                curs = connection.cursor()
                curs.execute('SELECT SvNr FROM PERSON where SvNr = ?', (SvNr,) )
                SvNr_SQL = curs.fetchone()[0]

                curs.execute('SELECT distinct Abfahrtshafen FROM Passage')
                Abfahrtshafen = curs.fetchall()
                if int(SvNr) == int(SvNr_SQL):
                    session['SvNr'] = SvNr
                    return render_template('login.html', Abfahrtshafen=Abfahrtshafen)
        finally:
            connection.close()



@app.route('/register', methods=["POST"])
def register():
        return render_template(('register.html'))

@app.route('/addPerson', methods=["POST"])
def addPerson():
    if request.method == "POST":
        SvNr = request.form['SvNr']
        Vorname = request.form["Vorname"]
        Nachname = request.form["Nachname"]
        PLZ = request.form["PLZ"]
        Ort = request.form["Ort"]
        Strasse = request.form["Strasse"]
        HausNr = request.form["HausNr"]

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

@app.route('/selectDeparture', methods=["POST", "GET"])
def selectDeparture():
    if g.SvNr:
        if request.method == "POST":
            try:
                destination = request.form['Hafen']
                print(destination)
                connection = sqlite3.connect('first.db')
                cursor = connection.cursor()
                cursor.execute("SELECT DISTINCT Abfahrtshafen FROM Passage WHERE Zielhafen LIKE ('%' || ? || '%')", (destination,))
                departureFrom = cursor.fetchone()

                response = make_response(render_template('selectDeparture.html', departureFrom=departureFrom))
                session['Ankunftshafen'] = destination
                response.set_cookie('Ankunftshafen', destination)

                return response
            #except Exception as e:
            #    return e
            finally:
                connection.close()
    return 'Not logged in'


@app.route('/selectArrivalTime', methods=["POST"])
def selectArrivalTime():
    if g.SvNr:
        try:
            departureFrom = request.form['Hafen']
            connection = sqlite3.connect('first.db')
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT Ankunftszeit FROM Passage WHERE Zielhafen = ?", (departureFrom ,))
            arrivalTime = cursor.fetchall()

            response = make_response(render_template('selectArrivalTime.html', arrivalTime=arrivalTime))
            response.set_cookie('Abfahrtshafen', departureFrom)

            session['Abfahrtshafen'] = departureFrom
            return response
        finally:
            connection.close()
    return 'Not logged in'

@app.route('/confirmBooking', methods=['POST'])
def confirmBooking():
    if g.SvNr:
        Ankunftszeit = request.form['Ankunftszeit']

        Abfahrtshafen = request.cookies.get('Abfahrtshafen', 0)
        #print(Abfahrtshafen)
        Ankunftshafen = request.cookies.get('Ankunftshafen', 0)
        #print(Ankunftshafen)
        if 'SvNr' in session:
             SvNr = session['SvNr']
             print(SvNr)
        # if 'Ankunftshafen' in session:
        #     Ankunftshafen = session['Ankunftshafen']
        #     print(Ankunftshafen)
        # if 'Abfahrtshafen' in session:
        #     Abfahrtshafen = session['Abfahrtshafen']
        response = make_response(render_template('confirmBooking.html', Ankunftshafen=Ankunftshafen, Abfahrtshafen=Abfahrtshafen, SvNr=SvNr, Ankunftszeit=Ankunftszeit))
        response.set_cookie('Ankunftszeit', Ankunftszeit)
        return response

@app.route('/addPassenger', methods=["POST"])
def addPassenger():
    if g.SvNr:
        Ankunftszeit = request.cookies.get('Ankunftszeit', 0)
        Abfahrtshafen = request.cookies.get('Abfahrtshafen', 0)
        print(Abfahrtshafen)
        Ankunftshafen = request.cookies.get('Ankunftshafen', 0)
        print(Ankunftshafen)
        if 'SvNr' in session:
            SvNr = session['SvNr']
            print(SvNr)


        try:
            connection = sqlite3.connect('first.db')
            cursor = connection.cursor()

            # richtige passage fürs buchen finden
            cursor.execute('''select Passagennummer from Passage where Zielhafen LIKE ('%' || ? || '%') 
                    AND Abfahrtshafen LIKE ('%' || ? || '%') AND Ankunftszeit LIKE ('%' || ? || '%') ''', (Ankunftshafen, Abfahrtshafen, Ankunftszeit,))
            Passagennummer = cursor.fetchone()[0]
            print(Passagennummer)

            # Passagier erstellen
            cursor.execute('SELECT MAX(Passagiernummer) from Passagier')
            hochstePassagierNr = cursor.fetchone()[0]
            if hochstePassagierNr == None:
                PassagierNrNeu = 1
            else:
                PassagierNrNeu = hochstePassagierNr + 1
            print(PassagierNrNeu)

            #buchung 



            # buchen

            return render_template('dummyTemplate.html')
        finally:
            connection.close()
    return 'Not logged in'


# Basic setup if you want to check if session is active and only tehn do sth.
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
