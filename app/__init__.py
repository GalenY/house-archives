from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# tells flask which view function is responsible for logins, pages that require you to be logged in to view will first
# redirect you to this function, and then after logging in, back to the initially requested page
login.login_view = 'login'
bootstrap = Bootstrap(app)


from app import routes, models