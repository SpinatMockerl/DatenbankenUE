#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, g
import os


# Flask constructor: define application as Flask object
app = Flask(__name__)
app.secret_key = os.urandom(24)     # secret_key later used in session setup
database = 'first.db'


# required for session ID cookie
@app.before_request
def before_request():
    g.SvNr = None
    if 'SvNr' in session:
        g.SvNr = session['SvNr']


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/returnHome', methods=["POST"])
def returnHome():
    return render_template('home.html')


# REGISTER 1
@app.route('/register', methods=["POST"])
def register():
    return render_template('register.html')


# REGISTER 2
@app.route('/addPerson', methods=["POST"])
def addPerson():
    if request.method == "POST":
        SVNr = request.form['SVNr']
        Vorname = request.form["Vorname"]
        Nachname = request.form["Nachname"]
        PLZ = request.form["PLZ"]
        Ort = request.form["Ort"]
        Strasse = request.form["Strasse"]
        HausNr = request.form["HausNr"]

        try:
            connection = sqlite3.connect(database)
            curs = connection.cursor()
            curs.execute("INSERT INTO PERSON (SVNr, Vorname, Nachname, PLZ, Ort, Strasse, Hausnr) VALUES "
                         "(?, ?, ?, ?, ?, ?, ?)", (SVNr, Vorname, Nachname, PLZ, Ort, Strasse, HausNr))
            connection.commit()
            curs.close()
            print("Person was added to db")
            return render_template('addPerson.html')

        except sqlite3.IntegrityError:
            connection.rollback()
            print("Person was not added to db")
            return render_template('userExists.html')
        finally:
            connection.close()
    else:
        return render_template('home.html')


# DELETE 1
@app.route('/delete', methods=["POST"])
def delete():
    return render_template('delete.html')


# DELETE 2
@app.route('/deleteEntry', methods=["POST"])
def deleteEntry():
    if request.method == "POST":
        table = request.form["table"]
        entry = request.form["entry"]
        if table.lower() == "person":
            Pkey = "SVNr"
        elif table.lower() == "passage":
            Pkey = "Passagennumer"
        elif table.lower() == "buchen":
            Pkey = "Buchungsnummer"
        else:
            return render_template("delete.html", Error="This relation does not exist")
        print(table + "\n" + Pkey + "\n" + entry)
        try:
            connection = sqlite3.connect(database)
            curs = connection.cursor()
            curs.execute("SELECT * FROM {} WHERE {} = (?)".format(table, Pkey, entry), (entry,))
            if curs.fetchone():
                curs.execute("DELETE FROM {} WHERE {} = (?)".format(table, Pkey), (entry,))
                connection.commit()
                curs.close()
                print("{} was removed from {}".format(entry, table))
                return render_template('home.html')
            else:
                return render_template("delete.html", Error="This entry does not exist")

        except sqlite3.IntegrityError:
            connection.rollback()
            print("{} was not removed from {}".format(entry, table))
            return render_template('home.html')
        finally:
            connection.close()
    else:
        return render_template('home.html')


# BOOKING 0
@app.route('/logout', methods=["POST"])
def logout():
    response = make_response(render_template('logout.html'))
    session.pop('SvNr', None)
    response.set_cookie('departure', expires=0)
    response.set_cookie('destination', expires=0)
    response.set_cookie('departureTime', expires=0)
    return response


# BOOKING 1
@app.route('/selectDeparture', methods=["POST"])
def selectDeparture():
    if request.method == "POST":
        session.pop('SvNr', None)
        try:
            SvNr = request.form['SvNr']
            connection = sqlite3.connect(database)
            curs = connection.cursor()
            curs.execute('SELECT distinct Abfahrtshafen FROM Passage')
            departure = curs.fetchall()
            curs.execute('SELECT SvNr FROM PERSON where SvNr = (?)', (SvNr,))
            if curs.fetchone()[0]:
                session['SvNr'] = SvNr
                return render_template(('selectDeparture.html'), Abfahrtshafen=departure)
        except:
            return render_template('register.html')
        finally:
            connection.close()
    else:
        return render_template('home.html')


# BOOKING 2
@app.route('/selectDestination', methods=["POST", "GET"])
def selectDestination():
    if g.SvNr and request.method == "POST":
        try:
            departure = request.form['Hafen']
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT Zielhafen FROM Passage WHERE Abfahrtshafen = (?)", (departure,))
            destination = cursor.fetchall()
            if destination:
                response = make_response(render_template('selectDestination.html', destination=destination))
                response.set_cookie('departure', departure)
                return response
            else:
                cursor.execute('SELECT distinct Abfahrtshafen FROM Passage')
                departure = cursor.fetchall()
                return render_template(('selectDeparture.html'), Abfahrtshafen=departure,
                                       Error="Departure does not exist. Please choose one of the listed departures")
        finally:
            connection.close()
    else:
        return render_template('notLoggedIn.html')


# BOOKING 3
@app.route('/selectDepartureTime', methods=["POST"])
def selectDepartureTime():
    if g.SvNr:
        try:
            destination = request.form['Hafen']
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            departure = request.cookies.get('departure', 0)
            cursor.execute("SELECT DISTINCT Abfahrtszeit FROM Passage WHERE Zielhafen = (?) AND Abfahrtshafen = (?)", (destination, departure))
            departureTime = cursor.fetchall()
            if departureTime:
                response = make_response(render_template('selectDepartureTime.html', departureTime=departureTime))
                response.set_cookie('destination', destination)
                return response
            else:
                cursor.execute("SELECT DISTINCT Zielhafen FROM Passage WHERE Abfahrtshafen = (?)", (departure,))
                destination = cursor.fetchall()
                return render_template('selectDestination.html', destination=destination,
                                       Error="Destination does not exist. Please choose one of the listed destinations")
        finally:
            connection.close()
    else:
        return render_template('notLoggedIn.html')


# BOOKING 4
@app.route('/confirmBooking', methods=['POST'])
def confirmBooking():
    if g.SvNr:
        departureTime = request.form['departureTime']
        departure = request.cookies.get('departure', 0)
        destination = request.cookies.get('destination', 0)
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT Abfahrtszeit FROM Passage WHERE Zielhafen = (?) AND Abfahrtshafen = (?)",
                       (destination, departure))
        SQL_time = cursor.fetchall()
        if (departureTime,) in SQL_time:
            try:
                cursor.execute("SELECT Vorname FROM PERSON where SvNr = (?)", (session['SvNr'],))
                person = cursor.fetchone()[0]
            except:
                person = session['SvNr']
            response = make_response(render_template('confirmBooking.html', departure=departure,
                                                     destination=destination, person=person,
                                                     departureTime=departureTime))
            response.set_cookie('departureTime', departureTime)
            return response
        else:
            return render_template('selectDepartureTime.html', departureTime=SQL_time,
                                   Error="No departure at this time. Please choose another departure time")

    else:
        return render_template('notLoggedIn.html')


# BOOKING 5
@app.route('/addPassenger', methods=["POST"])
def addPassenger():
    if request.method == "POST":
        departure = request.cookies.get('departure', 0)
        destination = request.cookies.get('destination', 0)
        departureTime = request.cookies.get('departureTime', 0)

        if 'SvNr' in session:
            SvNr = session['SvNr']

        # find Passagennummer
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute(
                '''select Passagennummer from Passage where Zielhafen = (?) 
                AND Abfahrtshafen = (?) AND Abfahrtszeit =(?)''', (destination, departure, departureTime,))
            selectedPassagennummer = cursor.fetchone()[0]
        except:
            connection.rollback()
        finally:
            connection.close()

        # create Buchungsnummer
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("SELECT MAX(Buchungsnummer) FROM Buchen")
            Buchungsnummer = cursor.fetchone()[0]
            if Buchungsnummer == None:
                hoechsteBuchungsnummer = 0
            else:
                hoechsteBuchungsnummer = Buchungsnummer
            neueBuchungsnummer = int(hoechsteBuchungsnummer) + 1
        except:
            connection.rollback()
            print('something went wrong')
        finally:
            connection.close()

        # create Buchung
        try:
            connection = sqlite3.connect(database)
            Klasse = '0'
            curs = connection.cursor()
            curs.execute("SELECT SVNR, Passagennummer FROM buchen")
            for i in curs.fetchall():
                if SvNr in i and selectedPassagennummer in i:
                    return render_template('bookingalreadyexists.html')

            curs.execute("INSERT INTO BUCHEN (Buchungsnummer, SVNR, Passagennummer, Klasse) VALUES (?, ?, ?, ?)",
                         (neueBuchungsnummer, SvNr, selectedPassagennummer, Klasse,))
            print("Buchung eingetragen")
            connection.commit()
            curs.close()
            return render_template('bookingDone.html')
        except:
            connection.rollback()
            print("Buchung nicht eingetragen")
            return render_template('bookingalreadyexists.html')
        finally:
            connection.close()


# Basic setup if you want to check if session is active and only then do sth.
@app.route('/dummy', methods=["POST"])
def dummy():
    if g.SvNr:
        return render_template('dummyTemplate.html')
    else:
        return render_template('notLoggedIn.html')


if __name__ == '__main__':
    # Flask .run() function: runs application on local development server
    # debug = True will automatically update site when code changes
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True)
