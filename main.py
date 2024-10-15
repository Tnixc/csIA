from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from flask import session, abort, redirect, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import pathlib
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import speech_recognition as sr
import soundfile

app = Flask(__name__)
app.config ['SECRET_KEY'] = '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'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'static/files'

db = SQLAlchemy(app)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow http traffic for local dev
GOOGLE_CLIENT_ID = "888946891767-ddsprhbd0kgmt0l95bbfhheir6b1r33h.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")



flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/home")


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect("/")

@app.route("/")
def loginpage():
    return "Hello World <a href='/login'><button>Login</button></a>"

@app.route("/home")
@login_is_required
def home():
    return render_template("base.html") #f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a><a href='/home/report'><button>Report</button></a><a href='/home/translate'><button>Translate</button></a>"

@app.route("/home/report")
@login_is_required
def report():
    return render_template("report.html")

@app.route("/home/manage")
@login_is_required
def manage():
    return render_template("base.html")

class CallDatabase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    calltext = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(500), nullable=False)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

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
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename("audio_file.wav"))) # Then save the file
        
    return render_template("translate.html", form = form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

