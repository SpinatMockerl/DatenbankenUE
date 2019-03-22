#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, redirect, g
import os



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
# To Do: enable get and redirect to home
def login():
    if request.method == "POST":
        session.pop('SvNr', None)
        try:
            SvNr = request.form['SvNr']
            with sqlite3.connect("first.db") as connection:
                curs = connection.cursor()
                curs.execute('SELECT distinct Abfahrtshafen FROM Passage')
                Abfahrtshafen = curs.fetchall
                curs.execute('SELECT SvNr FROM PERSON where SvNr = ?', (SvNr,))
                if curs.fetchone()[0]:
                    session['SvNr'] = SvNr
                    return render_template('login.html', Abfahrtshafen=Abfahrtshafen)
        except:
            return render_template('register.html')
        finally:
            connection.close()


@app.route('/register', methods=["POST"])
def register():
    return render_template('register.html')


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
                         "(?, ?, ?, ?, ?, ?, ?)", (SVNr, Vorname, Nachname, PLZ, Ort, Strasse, Hausnr))
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


@app.route('/passage', methods=["POST"])
def passage():
    return render_template('passage.html')


@app.route('/inputPassage', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def inputPassage():
    if request.method == "POST":
        Abfahrtshafen = request.form['Abfahrtshafen']
        Zielhafen = request.form["Zielhafen"]
        try:
            connection = sqlite3.connect('first.db')
            curs = connection.cursor()
            curs.execute('SELECT Passagennummer FROM PASSAGE where Abfahrtshafen = ? and Zielhafen = ?',
                         (Abfahrtshafen, Zielhafen))
            try:
                Passage_SQL = curs.fetchone()[0]
                if Passage_SQL:
                    print("Passage vorhanden")
                    connection.commit()
                    curs.close()
                    # Platzhalter für Weitergabe von Variablen an nächste Seite und dort Zugriff auf SQL mit Buchungserstellung?

                    return render_template('passageTime.html')

            except:
                connection.rollback()
                print("Passage nicht vorhanden")
                connection.commit()
                curs.close()
                print("Passagenabfrage durchgeführt")
                return render_template('home.html')

        except:
            connection.rollback()
            print("Passagenabfrage wurde nicht durchgeführt")
            return render_template('home.html')
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


@app.route('/inputPassageTime', methods=["POST"])
# mehrere Telefon nummer nicht implementiert
def inputPassageTime():
    if request.method == "POST":
        # Abfahrtszeit = request.form['Abfahrtszeit']
        # Passagennummer =
        try:
            connection = sqlite3.connect('first.db')
            curs = connection.cursor()
            # Abfrage welche die nächste Buchungsnummer ist?
            # Buchungsnummer =
            # curs.execute("INSERT INTO BUCHEN (Buchungsnummer, SVNR Passagennummer) VALUES "
            #              "(?, ?, ?)", (Buchungsnummer, SVNr, Passagennummer))
            print("Buchung eingetragen")
            connection.commit()
            curs.close()
            return render_template('bookingDone.html')

        except:
            connection.rollback()
            print("Buchung nicht eingetragen")
            return render_template('home.html')
        finally:
            connection.close()


@app.route('/delete', methods=["POST"])
def delete():
    return render_template('delete.html')


@app.route('/deleteEntry', methods=["POST"])
def deleteEntry():
    if request.method == "POST":
        table = request.form["table"]
        Pkey = ""
        entry = request.form["entry"]
        if table == "PERSON":
            Pkey = "SVNr"
        elif table == "PASSAGE":
            Pkey = "Passagennumer"
        elif table == "BUCHUNG":
            Pkey = "Buchungsnummer"
        print(table + "\n" + Pkey + "\n" + entry)
        try:
            connection = sqlite3.connect('first.db')
            curs = connection.cursor()
            # Injection risk
            curs.execute("DELETE FROM {} WHERE {} =  {}".format(table, Pkey, entry))
            connection.commit()
            curs.close()
            print("{} was removed from {}".format(entry, table))
            return render_template('home.html')

        except sqlite3.IntegrityError:
            connection.rollback()
            print("{} was not removed from {}".format(entry, table))
            return render_template('home.html')
        finally:
            connection.close()


@app.route('/logout', methods=["POST"])
def logout():
    session.pop('SvNr', None)
    return "Logout was successful"


if __name__ == '__main__':
    # Flask .run() function: runs application on local development server
    # debug = True will automatically update site when code changes
    app.run(debug=True)
