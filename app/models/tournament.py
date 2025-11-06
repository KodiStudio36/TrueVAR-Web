from sqlalchemy import Null
from app.extensions import db
from datetime import datetime
import uuid


def generate_uuid():
    return str(uuid.uuid4())

class Tournament(db.Model):
    __tablename__ = "tournament"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100))
    is_streaming = db.Column(db.Boolean, default=False)
    court_num = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    scheduled = db.Column(db.Boolean, default=None)

    thumbnails = db.relationship("Thumbnail", backref="tournament", cascade="all, delete-orphan")
    streams = db.relationship("Stream", backref="tournament", cascade="all, delete-orphan")

    def __init__(self, name: str, court_num: int, user_id: str, start: datetime = None,location = None, is_streaming=False, scheduled=False):
        self.name = name
        self.court_num = court_num
        self.user_id = user_id
        self.start = start or datetime.utcnow()
        self.location = location
        self.is_streaming = is_streaming
        self.scheduled = scheduled