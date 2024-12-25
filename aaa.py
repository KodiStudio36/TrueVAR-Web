from flask import Flask, render_template, redirect, request
from flask.cli import with_appcontext
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import click, re
from models import db, User, Submission, Licence
from datetime import datetime, date

app = Flask(__name__)

app.secret_key = 'something really secret in here'
app.config["SECRET_KEY"] = 'something really secret in here'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587  # You can also use 2525 or 25
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = '30d9d42543cc09e4a508ae019d87f728'  # Replace with your actual password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route('/contact', defaults={'url': None}, methods=['POST'])
@app.route('/contact/<url>', methods=['POST'])
def contact(url):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
       
        # Custom validation
        if not name or not email or not message:
            print("error1")
            return redirect("/")
       
        if len(name) < 2 or len(name) > 50:
            print("error2")
            return redirect("/")
       
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("error3")
            return redirect("/")
       
        if len(message) < 10:
            print("error4")
            return redirect("/")

        print("here")

        msg = Message(subject='Contact Form Submission',
                      sender="contact@demomailtrap.com",
                      recipients=['truevarinfo@gmail.com'],
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

@app.cli.command("licence")
@with_appcontext
@click.argument("command")
@click.option("--email", help="Select user email", required=True)
@click.option("--key", help="Select licence number", required=True)
@click.option("--active", help="Select activation date")
def add_licence(command, email, key, active):
    date_format = "%d-%m-%Y"
    active = datetime.strptime(active, date_format).date() if active else None

    if not User.query.filter_by(email=email).first():
        print(f"Error: There is no 'USER' with email '{email}'")
        return
    
    is_key = False
    if Licence.query.filter_by(key=key).first():
        is_key = True

    if command == "add":
        if is_key:
            print(f"Error: There is already a licence with this activation key '{key}'")
            return
        
        print("Creating licence...")
        licence = Licence(email, key, active)
        db.session.add(licence)

        db.session.commit()
        print("Licence created successfully")

    elif command == "remove":
        if not is_key:
            print(f"Error: There is no licence with this activation key '{key}'")
            return
        
        print("Removing licence...")
        Licence.query.filter_by(key=key).delete()
        db.session.commit()
        print("Licence removed successfully")

    elif command == "activate":
        if not is_key:
            print(f"Error: There is no licence with this activation key '{key}'")
            return
        
        print(f"Activating licence to date {active.strftime(date_format)}...")
        licence = Licence.query.filter_by(key=key).first()
        licence.active = active
        db.session.commit()
        print("Licence activated successfully")

    elif command == "deactivate":
        if not is_key:
            print(f"Error: There is no licence with this activation key '{key}'")
            return
        
        print(f"Deactivating licence...")
        licence = Licence.query.filter_by(key=key).first()
        licence.active = None
        db.session.commit()
        print("Licence deactivated successfully")

    else:
        print("""Error: Wrong argument 'COMMAND'""")

