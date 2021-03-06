from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Youtube


class AddSongForm(FlaskForm):
    url = StringField('YouTube URL:', validators=[DataRequired()])
    submit = SubmitField('Add Song')

    def validate_url(self, url):
        if not Youtube.valid_url(url.data):
            # raise Exception('didn\'t work')
            raise ValidationError('There was a problem with the URL. Please enter the URL of a single Youtube video.')
        else:
            if Youtube.query.filter_by(youtube_id=Youtube.get_query_string_dict(url.data).get('v')[0]).first():
                raise ValidationError('This video was already added!')

