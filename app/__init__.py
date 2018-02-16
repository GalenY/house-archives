from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

# tells flask which view function is responsible for logins, pages that require you to be logged in to view will first
# redirect you to this function, and then after logging in, back to the initially requested page
login.login_view = 'auth.login'

bootstrap = Bootstrap()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    # setting the flask configuration variables from a custom object's attributes
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)

    # register blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # set up email logging
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(mail_handler)

    return app

# at the bottom to avoid circular imports, apparently a common problem with flask apps
from app import models