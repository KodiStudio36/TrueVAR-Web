from app.extensions import db
import uuid


def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    passwd = db.Column(db.LargeBinary, nullable=False)

    sessions = db.relationship("SessionToken", backref="user", cascade="all, delete-orphan")
    licences = db.relationship("Licence", backref="user", cascade="all, delete-orphan")
    tournaments = db.relationship("Tournament", backref="user", cascade="all, delete-orphan")

    def __init__(self, email: str, name: str, passwd: str):
        self.email = email
        self.name = name
        self.passwd = passwd