from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug import generate_password_hash, check_password_hash
from hashlib import md5
import requests

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(300))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)



'''
class YouTube(db.Model):
    # Table Attributes
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    title = db.Column(db.String(100))

    prefixes = ['https://youtu.be/', 'https://www.youtube.com/watch?v=']

    @classmethod
    def valid_url(cls, full_url):
        if any((full_url.startswith(prefix) for prefix in cls.prefixes)):
            r = requests.get(full_url)
            if r.status_code == 200:
                if len(r.json()['items']) == 1:
                    return True
        return False


    def initializer(self,):
        if full_url.startswith(cls.prefixes[0]):
            if full_url.find('?') != -1:
                vid_id = full_url[17:full_url.find('?')]
            else:
                vid_id = full_url[17:]

        elif self.full_url.start

    def get_embed(self, start_time=False, autoplay=False):



class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(400), unique=True)
    title =


function playsong() {
	document.getElementById("player").src="https://www.youtube.com/embed/7Cz3CHpVSeA?autoplay=1";
}



YouTube ()

Music ( Title(if not specified, default to scraping it from soundcloud or youtube), Artist(optional), tags/genres/styles(optional), uploaded_by, URL/type,)

Video ( Title(if not specified, default to youtube title), Dancers(Users), Song(more thought for this), style, tags, uploaded_by, YouTube URL)

User/Dancer (id, username, email, password, about_me, last_seen, name, crew, favorite/highest_rated_videos, favorite/highest_rated_songs, videos_of_me(link to filtered videos page), showcase_video, facebook, twitter, instagram, youtube,)
'''

