from flask import Flask, session, abort, redirect, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
import os
import pathlib
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import speech_recognition as sr
import soundfile
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'static/files'

db = SQLAlchemy(app)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

class CallDatabase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    calltext = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time = db.Column(db.String(500), nullable=False)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/login")
        else:
            return function(*args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        try:
            token = request.json.get('credential')
            if not token:
                return jsonify({"success": False, "message": "No credential provided"}), 400

            idinfo = id_token.verify_oauth2_token(token, google_auth_requests.Request(), GOOGLE_CLIENT_ID)
            session["google_id"] = idinfo['sub']
            session["name"] = idinfo['name']
            return jsonify({"success": True})
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 401
        except Exception as e:
            return jsonify({"success": False, "message": "An error occurred"}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    if "google_id" in session:
        return redirect("/home")
    return render_template("login.html")

@app.route("/home")
@login_is_required
def home():
    return render_template("base.html")

@app.route("/home/report")
@login_is_required
def report():
    return render_template("report.html")

@app.route("/home/manage")
@login_is_required
def manage():
    return render_template("base.html")

def stt_Cantonese(audio_file):
    data, samplerate = soundfile.read(audio_file)
    soundfile.write(audio_file, data, samplerate, subtype='PCM_16')
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="yue-HK")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return None

@app.route("/home/translate", methods=['GET', 'POST'])
@login_is_required
def translate():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename("audio_file.wav")))

    return render_template("translate.html", form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=80, debug=True)