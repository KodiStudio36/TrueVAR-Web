from app.extensions import db


class Thumbnail(db.Model):
    __tablename__ = "thumbnail"
    tournament_id = db.Column(db.String(36), db.ForeignKey("tournament.id"), primary_key=True, nullable=False)
    court = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(255), primary_key=True, nullable=False)

    def __init__(self, tournament_id: str, court: int, path: str):
        self.tournament_id = tournament_id
        self.court = court
        self.path = path