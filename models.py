from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key= True, unique = True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")


    @classmethod
    def register(cls, username, password, first_name, last_name, email):

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        user = cls( username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email)
        
        db.session.add(user)
        db.session.commit()
        return user


class Feedback(db.Model):
    
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key = True, unique = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable = False)