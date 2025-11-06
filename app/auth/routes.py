from flask import Blueprint, render_template, request, redirect, url_for, make_response
from werkzeug.security import check_password_hash
import uuid, bcrypt

from app.auth import bp

from app.models.user import User
from app.models.session_token import SessionToken
from app.extensions import db

@bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template("login.html", error="Email and password are required.")

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template("login.html", error="Invalid credentials.")

    # bcrypt expects bytes
    if not bcrypt.checkpw(password.encode("utf-8"), user.passwd):
        return render_template("login.html", error="Invalid credentials.")

    # Generate a new bearer token
    token = str(uuid.uuid4())
    session = SessionToken(user_id=user.id, token=token)
    db.session.add(session)
    db.session.commit()

    response = make_response(redirect(url_for("dashboard.dashboard")))
    response.set_cookie("Authorization", f"Bearer {token}")
    return response