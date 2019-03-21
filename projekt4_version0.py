#!/usr/bin/env python
# coding: utf8

import sqlite3
from flask import Flask, render_template, make_response, request, session, redirect
import os

# Tutorial: https://www.youtube.com/watch?v=o-vsdfCBpsU

# define connection, sqlite will create db file if not already there
connection = sqlite3.connect('first.db')

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
# Telefonnummer nicht implementiert
try:
    curs.execute("INSERT INTO Person VALUES('1234567890', 'Laura', 'Lama', '2020', 'Wien', 'Zoostrasse', '20')")
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
            SVNr = request.form['SVNr']
            print(SVNr)
            with sqlite3.connect("first.db") as connection:
                curs = connection.cursor()
                curs.execute('SELECT SVNr FROM PERSON where SVNr = ?', (SVNr,))
                if curs.fetchone()[0]:
                    session['SVNr'] = SVNr
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
        SVNr = request.form['SVNr']
        Vorname = request.form["Vorname"]
        Nachname = request.form["Nachname"]
        PLZ = request.form["PLZ"]
        Ort = request.form["Ort"]
        Strasse = request.form["Strasse"]
        print(Strasse)
        Hausnr = request.form["HausNr"]
        TelefonNr = request.form["TelefonNr"]

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


if __name__ == '__main__':
    # Flask .run() function: runs application on local development server
    # debug = True will automatically update site when code changes
    app.run(debug=True)
