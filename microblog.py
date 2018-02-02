from app import app, db
from app.models import User, Post, Youtube, Song, SongRating

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Youtube': Youtube, 'Song': Song, 'SongRating': SongRating}