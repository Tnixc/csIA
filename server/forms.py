from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import InputRequired, DataRequired

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

class KeywordSearchForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    submit = SubmitField("Search")