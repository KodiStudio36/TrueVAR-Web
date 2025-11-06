from flask import Flask
from flask.cli import with_appcontext
import click, bcrypt
import uuid
from datetime import datetime

from config import Config
from app.extensions import db, mail
from app.scheduler import init_scheduler

from app.models.user import User
from app.models.session_token import SessionToken
from app.models.licence import Licence
from app.models.stream_key import StreamKey
from app.models.stream import Stream
from app.models.tournament import Tournament
from app.models.thumbnail import Thumbnail
from app.models.submission import Submission
from app.models.fight import Fight


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    mail.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.contact import bp as contact_bp
    app.register_blueprint(contact_bp, url_prefix='/contact')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    init_scheduler(app)


    def populate_stream_key():
        db.session.add(StreamKey("MyM83RtgHsajgB96RxWQug1738923371262452", "a679-y644-da7s-wm4k-dq5p", 1, 1))
        db.session.add(StreamKey("MyM83RtgHsajgB96RxWQug1745751261101076", "t366-gubp-ja6t-v5ps-efdk", 1, 2))
        db.session.add(StreamKey("MyM83RtgHsajgB96RxWQug1749142144422742", "p7p9-zvtz-3fr3-fp9h-23q3", 1, 3))
        db.session.add(StreamKey("MyM83RtgHsajgB96RxWQug1749142171574806", "hphg-4z1k-xd1e-cppy-5rhh", 1, 4))
        db.session.commit()

    @app.cli.command("create-tables")
    @with_appcontext
    def create_tables():
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully.")
        populate_stream_key()
        print("Tables populated successfully.")


    # ---------------- USER COMMANDS ----------------
    @app.cli.command("user")
    @with_appcontext
    @click.argument("command")
    @click.option("--email", help="User email")
    @click.option("--name", help="User name")
    @click.option("--passwd", help="User password")
    def user(command, email, name, passwd):
        if command == "add":
            if not email or not name or not passwd:
                print("Error: Missing arguments --email, --name, --passwd")
                return
            if User.query.filter_by(email=email).first():
                print(f"Error: User with email {email} already exists")
                return

            # Store password hash as session token (or extend authentication model later)
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passwd.encode("utf-8"), salt)

            user = User(email, name, hashed)
            db.session.add(user)

            db.session.commit()
            print(f"User {name} created with email {email}")

        elif command == "update":
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"Error: User with email {email} not found")
                return
            if name:
                user.name = name
            db.session.commit()
            print(f"User {email} updated")

        elif command == "remove":
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"Error: User with email {email} not found")
                return
            db.session.delete(user)
            db.session.commit()
            print(f"User {email} removed")

        else:
            print("Error: Command must be add|update|remove")


    # ---------------- LICENCE COMMANDS ----------------
    @app.cli.command("licence")
    @with_appcontext
    @click.argument("command")
    @click.option("--email", required=True, help="User Email")
    @click.option("--court", type=int, help="Court number")
    @click.option("--active", help="Activation date (dd-mm-yyyy)")
    def licence(command, email, court, active):
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: User with email {email} not found")

        date_format = "%d-%m-%Y"
        active_date = datetime.strptime(active, date_format).date() if active else None

        if command == "add":
            if not court:
                print("Error: Missing --court")
                return
            licence = Licence(user.id, court, active_date)
            db.session.add(licence)
            db.session.commit()
            print(f"Licence added for user {user.id} on court {court}")

        elif command == "remove":
            licence = Licence.query.filter_by(user_id=user.id, court=court).first()
            if not licence:
                print("Error: Licence not found")
                return
            db.session.delete(licence)
            db.session.commit()
            print("Licence removed")

        elif command == "activate":
            licence = Licence.query.filter_by(user_id=user.id, court=court).first()
            if not licence:
                print("Error: Licence not found")
                return
            licence.active = active_date
            db.session.commit()
            print(f"Licence activated on {active}")

        elif command == "deactivate":
            licence = Licence.query.filter_by(user_id=user.id, court=court).first()
            if not licence:
                print("Error: Licence not found")
                return
            licence.active = None
            db.session.commit()
            print("Licence deactivated")

        elif command == "check":
            licence = Licence.query.filter_by(user_id=user.id, court=court).first()
            if not licence:
                print("Error: Licence not found")
                return
            if licence.active and licence.active >= datetime.today().date():
                print("Licence is valid ✅")
            else:
                print("Licence is invalid ❌")

        else:
            print("Error: Command must be add|remove|activate|deactivate|check")


    # ---------------- TOURNAMENT COMMANDS ----------------
    @app.cli.command("tournament")
    @with_appcontext
    @click.argument("command")
    @click.option("--email", required=True, help="User Email")
    @click.option("--name", help="Tournament name")
    @click.option("--court_num", type=int, help="Number of courts")
    @click.option("--is_streaming", type=bool, default=False, help="Enable streaming")
    @click.option("--start", help="Start datetime (dd-mm-yyyy HH:MM)")
    def tournament(command, email, name, court_num, is_streaming, start):
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: User with email {email} not found")

        if command == "add":
            if not name or not court_num:
                print("Error: Missing --name or --court_num")
                return
            start_dt = datetime.strptime(start, "%d-%m-%Y %H:%M") if start else None
            tournament = Tournament(name, court_num, user.id, start_dt, is_streaming)
            db.session.add(tournament)
            db.session.commit()
            print(f"Tournament '{name}' created for user {user.id}")

        elif command == "remove":
            t = Tournament.query.filter_by(name=name, user_id=user.id).first()
            if not t:
                print("Error: Tournament not found")
                return
            db.session.delete(t)
            db.session.commit()
            print(f"Tournament '{name}' removed")

        else:
            print("Error: Command must be add|remove")


    return app