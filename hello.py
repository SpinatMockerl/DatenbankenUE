from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

# flask installieren, über $ pip install Flask oder Python interpreter in PyCharm
# env FLASK_APP=hello.py flask run
# output auf: http://127.0.0.1:5000/
# exit mit strg+c
