from datetime import datetime

from flask import Flask
from flask.cli import with_appcontext
import click, bcrypt

from config import Config
from app.extensions import db, mail

from app.models.user import User
from app.models.authentication import Authentication
from app.models.submission import Submission
from app.models.licence import Licence
from app.models.shop_item import ShopItem

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    mail.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.shop import bp as shop_bp
    app.register_blueprint(shop_bp, url_prefix='/shop')

    from app.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.contact import bp as contact_bp
    app.register_blueprint(contact_bp, url_prefix='/contact')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')



    @app.cli.command("create-tables")
    @with_appcontext
    def create_tables():
        print("Creating tables...")
        db.create_all()
        populate()
        print("Tables created successfully.")

    def populate():
        db.session.add(ShopItem("ShopItem1", 85.3, "/shop/shopitem1"))
        db.session.add(ShopItem("ShopItem2", 85.3))
        db.session.add(ShopItem("ShopItem3", 85.3, "/shop/shopitem3"))

        db.session.commit()

    @app.cli.command("user")
    @with_appcontext
    @click.argument("command")
    @click.option("--email", help="Select user email", required=True)
    @click.option("--name", help="Select user name")
    @click.option("--passwd", help="Select user password")
    def user(command, email, name, passwd):
        if command == "add":
            if Authentication.query.filter_by(email=email).first():
                print(f"Error: There is already an 'USER' with email '{email}'")
                return
            
            if not passwd:
                print(f"Error: Missing argument 'PASSWD'")
                return
            
            user = User.query.filter_by(email=email).first()

            if not user:
                if not name:
                    print(f"Error: Missing argument 'NAME'")
                    return
                
                user = User(email, name)
                db.session.add(user)
            
            print("Creating user...")

            bytes = passwd.encode('utf-8')
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(bytes, salt)
            
            authentication = Authentication(email, hash)
            db.session.add(authentication)

            db.session.commit()
            print("User created successfully")

        else:
            print("""Error: Wrong argument 'COMMAND'""")

    @app.cli.command("licence")
    @with_appcontext
    @click.argument("command")
    @click.option("--email", help="Select user email", required=True)
    @click.option("--key", help="Select licence number", required=True)
    @click.option("--active", help="Select activation date")
    def licence(command, email, key, active):
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

        elif command == "migrate":
            if not is_key:
                print(f"Error: There is no licence with this activation key '{key}'")
                return
            
            print(f"Migrating licence...")
            licence: Licence = Licence.query.filter_by(key=key).first()
            licence.pc_hash = None
            db.session.commit()
            print("Licence migrated successfully")

        else:
            print("""Error: Wrong argument 'COMMAND'""")



    return app