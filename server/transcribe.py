from flask import Blueprint, render_template
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
import speech_recognition as sr
import soundfile
from .forms import UploadFileForm

transcribe = Blueprint('transcribe', __name__)

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


@transcribe.route("/home/transcribe", methods=['GET', 'POST'])
@login_required
def transcribe_audio():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'static/files', secure_filename("audio_file.wav")))

    return render_template("transcribe.html", form=form)
