from app.extensions import db

class Authentication(db.Model):
    __tablename__ = 'authentication'
    email = db.Column(db.String(100), db.ForeignKey('user.email'), primary_key=True)
    passwd = db.Column(db.LargeBinary)

    def __init__(self, email: str, passwd: str):
        self.email = email
        self.passwd = passwd
