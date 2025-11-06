from app.extensions import db


class StreamKey(db.Model):
    __tablename__ = "stream_key"
    id = db.Column(db.String(36), primary_key=True)
    stream_key = db.Column(db.String(36), nullable=False)
    tournament = db.Column(db.Integer, nullable=False)
    court = db.Column(db.Integer, nullable=False)

    def __init__(self, id: str, stream_key: str, tournament: int, court: int):
        self.id = id
        self.stream_key = stream_key
        self.tournament = tournament
        self.court = court