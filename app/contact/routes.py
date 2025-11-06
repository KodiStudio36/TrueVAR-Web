import re
from flask import render_template, request, redirect
from flask_mail import Message
from app.contact import bp
from app.extensions import db, mail

from config import Config
from app.models.user import User
from app.models.submission import Submission

@bp.route('/', methods=['GET'])
def index():
    return render_template('contact/index.html')

@bp.route('/form', defaults={'url': None}, methods=['POST'])
@bp.route('/form/<url>', methods=['POST'])
def form(url):
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Custom validation
    if not name or not email or not message:
        print("error1")
        return redirect(f"/{url}" if url else "/")

    if len(name) < 2 or len(name) > 50:
        print("error2")
        return redirect(f"/{url}" if url else "/")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("error3")
        return redirect(f"/{url}" if url else "/")

    if len(message) == 0:
        print("error4")
        return redirect(f"/{url}" if url else "/")

    msg = Message(subject='Contact Form Submission',
                    sender=Config.SENDER_EMAIL,
                    recipients=[Config.MY_EMAIL],
                    html=render_template("email.html", name=name, email=email, message=message))

    if not User.query.filter_by(email=email).first():
        user = User(email, name)
        db.session.add(user)

    submission = Submission(email, message)
    db.session.add(submission)
        
    db.session.commit()

    # Send email
    mail.send(msg)
    return redirect(f"/{url}" if url else "/")