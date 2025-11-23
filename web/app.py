
import flask
import requests
from flask import sessions, Flask, render_template
from dotenv import load_dotenv

app = Flask(__name__)

@app.route('/')
def u3_project():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)