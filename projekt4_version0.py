#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, redirect, g
import os


# Flask constructor: define application as Flask object
app = Flask(__name__)
app.secret_key = os.urandom(24)     # secret_key later used in session setup


# check session ID
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
            connection = sqlite3.connect('first.db')
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
            connection = sqlite3.connect('first.db')
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


# BOOKING 0
@app.route('/logout', methods=["POST"])
def logout():
    session.pop('SvNr', None)
    return render_template('logout.html')


# BOOKING 1
@app.route('/login', methods=["POST"])
# To Do: enable get and redirect to home
def login():
    if request.method == "POST":
        session.pop('SvNr', None)
        try:
            SvNr = request.form['SvNr']
            with sqlite3.connect("first.db") as connection:
                curs = connection.cursor()
                curs.execute('SELECT distinct Abfahrtshafen FROM Passage')
                Abfahrtshafen = curs.fetchall()
                curs.execute('SELECT SvNr FROM PERSON where SvNr = (?)', (SvNr,))
                if curs.fetchone()[0]:
                    session['SvNr'] = SvNr
                    print("bis hier")
                    print(Abfahrtshafen)
                    return render_template(('login.html'), Abfahrtshafen=Abfahrtshafen)
        except:
            return render_template('register.html')
        finally:
            connection.close()


# BOOKING 2
@app.route('/selectDeparture', methods=["POST", "GET"])
def selectDeparture():
    print("!!")
    if g.SvNr and request.method == "POST":
        try:
            departure = request.form['Hafen']
            print(departure)
            connection = sqlite3.connect('first.db')
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT Zielhafen FROM Passage WHERE Abfahrtshafen = (?)", (departure,))
            destination = cursor.fetchall()
            print(destination)
            if destination:
                response = make_response(render_template('selectDestination.html', destination=destination))
                response.set_cookie('departure', departure)
                return response
            else:
                cursor.execute('SELECT distinct Abfahrtshafen FROM Passage')
                departure = cursor.fetchall()
                return render_template(('login.html'), Abfahrtshafen=departure,
                                       Error="Departure does not exist. Please choose one of the listed departures")

        #except Exception as e:
        #    return e
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
            connection = sqlite3.connect('first.db')
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
        connection = sqlite3.connect('first.db')
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT Abfahrtszeit FROM Passage WHERE Zielhafen = (?) AND Abfahrtshafen = (?)",
                       (destination, departure))
        SQL_time = cursor.fetchall()
        if (departureTime,) in SQL_time:
            if 'SvNr' in session:
                 SvNr = session['SvNr']
                 print(SvNr)
            response = make_response(render_template('confirmBooking.html', departure=departure, destination=destination, SvNr=SvNr, departureTime=departureTime))
            response.set_cookie('departureTime', departureTime)
            return response
        else:
            return render_template('selectDepartureTime.html', departureTime=SQL_time, Error="No departure at this time. Please choose another departure time")

    else:
        return render_template('notLoggedIn.html')


# BOOKING 5
@app.route('/addPassenger', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def addPassenger():
    if request.method == "POST":
        departureTime = request.cookies.get('departureTime', 0)

        departure = request.cookies.get('departure', 0)
        destination = request.cookies.get('destination', 0)
        # print('Ankunftshafen: ' + Ankunftshafen)
        # print('Ankunftszeit: ' + Ankunftszeit)
        # print('Abfahrtshafen: ' + departure)

        if 'SvNr' in session:
            SvNr = session['SvNr']
            print(SvNr)

        try:
            with sqlite3.connect("first.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    '''select Passagennummer from Passage where Zielhafen = (?) AND Abfahrtshafen = (?) AND Abfahrtszeit =(?)''',
                    (destination, departure, departureTime,))
                selectedPassagennummer = cursor.fetchone()[0]
                print(selectedPassagennummer)
        ## zurück senden falls es zu fehler kommt
        except:
            connection.rollback()
        finally:
            connection.close()

        # neue buchungsnummer erstellen
        try:
            with sqlite3.connect('first.db') as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT MAX(Buchungsnummer) FROM Buchen")

                Buchungsnummer = cursor.fetchone()[0]

                if Buchungsnummer == None:
                    hoechsteBuchungsnummer = 0
                else:
                    hoechsteBuchungsnummer = Buchungsnummer
                    print(hoechsteBuchungsnummer)
                print(hoechsteBuchungsnummer)
                neueBuchungsnummer = int(hoechsteBuchungsnummer) + 1
                print(neueBuchungsnummer)

        # was wäre eine gute exception?
        except:
            print('something went wrong')
        finally:
            connection.close()

        try:
            with sqlite3.connect('first.db') as connection:
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


# Basic setup if you want to check if session is active and only tehn do sth.
@app.route('/login_p', methods=["POST"])
def login_p():
    if g.SvNr:
        return render_template('dummyTemplate.html')

    else:
        return render_template('notLoggedIn.html')



if __name__ == '__main__':
    # Flask .run() function: runs application on local development server
    # debug = True will automatically update site when code changes
    app.run(debug=True)
