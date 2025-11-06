from app.extensions import db


class Fight(db.Model):
    __tablename__ = "fight"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    stream_id = db.Column(db.String(36), db.ForeignKey("stream.id"))
    message = db.Column(db.String(36))

    def __init__(self, broadcast_id: str, message: str):
        self.broadcast_id = broadcast_id
        self.message = message