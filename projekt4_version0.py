import sqlite3
from flask import Flask, render_template, make_response, request

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

curs.execute('''CREATE TABLE IF NOT EXISTS Telefonnummer( SVNr int(10), Telefon_nr int(12), \
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

app = Flask(__name__)


@app.route('/home')
def home():
    return render_template(('home.html'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        response = make_response(render_template('login.html'))
        return response

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template(('register.html'))

#@app.route('/insertPerson')
# access page: http://localhost:5000/insertPerson
#def newPerson():
#    return render_template('person.html')



if __name__ == '__main__':
    app.run(debug = True)
