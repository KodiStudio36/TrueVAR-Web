from app.extensions import db
from datetime import date
import uuid


def generate_uuid():
    return str(uuid.uuid4())

class Licence(db.Model):
    __tablename__ = "licence"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    court = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    active = db.Column(db.Date, nullable=True)
    pc_hash = db.Column(db.LargeBinary)

    streams = db.relationship("Stream", backref="licence", cascade="all, delete-orphan")

    def __init__(self, user_id: str, court: int, active: date = None, pc_hash=None):
        self.user_id = user_id
        self.court = court
        self.active = active
        self.pc_hash = pc_hash