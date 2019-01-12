from datetime import datetime
from app import db, login
from flask_login import UserMixin
from flask import current_app
from werkzeug import generate_password_hash, check_password_hash
from hashlib import md5
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode
from time import time
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(300))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    song_ratings = db.relationship('SongRating', back_populates='user')

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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

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




class Youtube(db.Model):
    __tablename__ = 'youtube'
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(12))
    title = db.Column(db.String(100), index=True)
    start_time_seconds = db.Column(db.Integer)
    duration = db.Column(db.String(8))
    duration_seconds = db.Column(db.Integer)
    type = db.Column(db.String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'youtube',
        'polymorphic_on': 'type'
    }

    url_prefixes = ['https://youtu.be/', 'https://www.youtube.com/watch?v=']

    def __repr__(self):
        return '<Youtube {}>'.format(self.title if self.title else 'Untitled')


    @staticmethod
    def valid_url(url):
        if any((url.startswith(prefix) for prefix in Youtube.url_prefixes)):
            # check if given url is valid
            if requests.get(url).status_code == 200:
                # check if we can extract video id from url and then rebuild a valid url from it
                if requests.get(Youtube.url_prefixes[1] + Youtube.get_query_string_dict(url).get('v')[0]).status_code == 200:
                    return True

        return False

        # This code checked the validity of the url using the youtube api
        #
        # r = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id&id={}&key={}'.format(
        #     Youtube.get_query_string_dict(url).get('v')[0], current_app.config['YOUTUBE_API_KEY']))
        # if r.status_code == 200:
        #     if len(r.json()['items']) == 1:
        #         return True


    @staticmethod
    def get_query_string_dict(youtube_url):
        qs = parse_qs(urlparse(youtube_url).query)
        if qs.get('v') == None and youtube_url.startswith(Youtube.url_prefixes[0]):
            if youtube_url.find('?') != -1:
                qs['v'] = [youtube_url[17:youtube_url.find('?')]]
            else:
                qs['v'] = [youtube_url[17:]]
        return qs

    def set_values(self, url, using_api=False):
        qs = self.get_query_string_dict(url)
        self.youtube_id = qs['v'][0]
        if qs.get('t'):
            self.start_time_seconds = qs.get('t')[0]
        else:
            self.start_time_seconds = 0

        # get title and duration info about video using youtube api
        if using_api:
            json = requests.get(
                'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={}&key={}'.format(
                    self.youtube_id, current_app.config['YOUTUBE_API_KEY'])).json()
            try:
                self.title = json['items'][0]['snippet']['title']
            except:
                pass

            try:
                # duration string in youtube format e.g. "PT1H54M7S"
                d = json['items'][0]['contentDetails']['duration']
            except:
                d = None

        # scraping title and duration info instead
        else:
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                title = soup.find('meta', attrs={"itemprop": "name"}).get('content')
                if title:
                    self.title = title
                # duration string in youtube format e.g. "PT1H54M7S"
                d = soup.find('meta', attrs={"itemprop": "duration"}).get('content')

        # if we found a duration string in youtube format e.g. "PT1H54M7S"
        if d:
            # setting self.duration and self.duration_seconds
            duration_seconds = 0
            d = d[2:]
            index = d.find('H')
            if index != -1:
                duration_seconds += 3600 * int(d[:index])
                d = d[index + 1:]
            index = d.find('M')
            if index != -1:
                duration_seconds += 60 * int(d[:index])
                d = d[index + 1:]
            index = d.find('S')
            if index != -1:
                duration_seconds += int(d[:index])

            hours, remaining_seconds = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remaining_seconds, 60)
            if hours > 0:
                duration = '{}:{}:{}'.format(hours, minutes, seconds)
            else:
                duration = '{}:{}'.format(minutes, seconds)

            self.duration_seconds = duration_seconds
            self.duration = duration

    def get_embed(self, start_time=0, autoplay=0):
        url = 'https://www.youtube.com/embed/' + self.youtube_id + '?'
        url += urlencode({'start': start_time, 'autoplay': autoplay})
        return url


class Song(Youtube):
    rating = db.Column(db.Float)
    ratings = db.relationship('SongRating', back_populates='song')

    __mapper_args__ = {
        'polymorphic_identity': 'song'
    }

    def __repr__(self):
        return '<Song {}>'.format(self.title if self.title else 'Untitled')

    def update_rating(self):
        pass


class SongRating(db.Model):
    __tablename__ = 'songrating'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('youtube.id'), primary_key=True)
    rating = db.Column(db.Float)
    user = db.relationship('User', back_populates='song_ratings')
    song = db.relationship('Song', back_populates='ratings')

    def __repr__(self):
        return '<SongRating(user_id={}, song_id={}, rating={})>'.format(self.user_id, self.song_id, self.rating)

'''
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

