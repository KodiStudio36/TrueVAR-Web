from app.extensions import db

class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    authentication = db.relationship('Authentication', backref='user')
    submissions = db.relationship('Submission', backref='user')
    licences = db.relationship('Licence', backref='user')

    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name