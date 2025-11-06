from app.extensions import db


class Stream(db.Model):
    __tablename__ = "stream"
    id = db.Column(db.String(36), primary_key=True)
    tournament_id = db.Column(db.String(36), db.ForeignKey("tournament.id"), nullable=False)
    licence_id = db.Column(db.String(36), db.ForeignKey("licence.id"), nullable=False)
    stream_key = db.Column(db.String(36), nullable=False)
    live_chat_id = db.Column(db.String(36), nullable=True)

    fights = db.relationship("Fight", backref="stream", cascade="all, delete-orphan")

    def __init__(self, id, tournament_id, licence_id, stream_key=None, live_chat_id=None):
        self.id = id
        self.tournament_id = tournament_id
        self.licence_id = licence_id
        self.stream_key = stream_key
        self.live_chat_id = live_chat_id