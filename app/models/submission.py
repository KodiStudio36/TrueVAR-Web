from app.extensions import db

class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'))
    message = db.Column(db.Text)

    def __init__(self, email: str, message: str):
        self.user_email = email
        self.message = message
