# DatenbankenUE
Datenbanksysteme Übung 4

Gorki, Kriz, Lehner, Mock


# ToDo:

## first.db:
- Entlehner: Trigger für techniker u kapitän
- Buchen: Key aus passagiernummer und passagennummer
- Entlehner: Trigger für union aus Techniker und Kapitäne

## html:
- check if registration form is empty
- on registration or login, return same html (register, home) with additional text "invalid number..."?
- add passage.html
- add buchungszeit.html

# Git FAQ:

## branches von anderen lokal herunterladen:
- git fetch                             # lädt alle branches herunter
- git branch --all                      # zeigt alle branches an
- git checkout *branch-von-anderen*     # branch wird ab jetzt auch nur mit $ git branch angezeigt

## sicheres pushen in master:
- git checkout master
- git merge *branch-der-in-master-soll*
- git push

## Verwerfen von abgeschlossenen commits (rollback):
- git checkout *branch-zu-resetten*
- git log
- git reset --hard *commit-hash*        # den hash aus log eingeben, zu dem man zurückkehren möchte
- git push -f                           # (force) push wird erzwungen und commit wird neuer HEAD

## neue files, die in allen branches sind:
ist nur etwas, was mich am Anfang sehr verwirrt hat. Wenn man neue files erstellt und diese nicht addet, oder committed,
ich weiß noch nicht welcher der kritische schritt ist, sind diese nicht in git und werden mit § git checkout <branch>
nicht verändert --> befinden sich also scheinbar in allen branches
Idee: solange man nichts addet ist es egal, in welchem branch man arbeitet, vllt auch für AlgoUE relevant...

# SQL FAQ:
## sqlite3 (interaktiv) Tipps:
- .db File mit "sqlite3 FILENAME.db" öffnen.
Abfragen möglich.
- Mittels ".schema" werden alle verwendeten Befehle zur Erstellung der Relationenschemata ausgegeben.
- Mittels ".dump" werden ALLE verwendeten Befehle zur Datenbankgenerierung ausgegeben (inkl. z.B. Werte).
- Sqlite3 interaktiven Modus beenden: .quit oder Ctrl + D
- Gui um DB anzuschauen: https://sqlitebrowser.org/dl/

## Notes SQLITE3 & Flask in Python
- insert dynamic variables in DB:  
	connection = sqlite2.connect('YourDB.db')  
	cursor = connection.cursor()  
	cursor.execute("INSERT INTO table(columnName1, columnName2) VALUES(?,?)", (yourVariable1, yourVariable2))  
	connection.commit()  
	cursor.close()  
	connection.close()  

# To Do im setup von Webpage:
- "Kosmetisch":
	nach Registrierung wird man auf Login weitergeleitet ohne informationen darüber zu erhalten ob registrierung korrekt war.	

- Kritisch:
	Login: Setup mit Zustandserhaltung, weiterverarbeitung von Daten und sicherheit (?)   
