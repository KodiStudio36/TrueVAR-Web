from app.extensions import db


class SessionToken(db.Model):
    __tablename__ = "session_token"
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), primary_key=True, nullable=False)
    token = db.Column(db.String(255), primary_key=True, nullable=False)

    def __init__(self, user_id: str, token: str):
        self.user_id = user_id
        self.token = token