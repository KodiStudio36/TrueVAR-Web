from app.extensions import db
from datetime import date

class Licence(db.Model):
    __tablename__ = "licence"
    key = db.Column(db.String(100), primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'))
    active = db.Column(db.Date)
    pc_hash = db.Column(db.LargeBinary)

    def __init__(self, email: str, key: str, active: date, pc_hash=None):
        self.user_email = email
        self.key = key
        self.active = active
        self.pc_hash = pc_hash