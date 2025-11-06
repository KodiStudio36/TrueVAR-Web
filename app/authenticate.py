from flask import jsonify

from functools import wraps
from flask import request, jsonify, redirect, url_for

from app.models.user import User
from app.models.session_token import SessionToken
from app.models.licence import Licence

def validate_token(token: str):
    if not token:
        return None
    session = SessionToken.query.filter_by(token=token).first()
    if not session:
        return None
    return User.query.filter_by(id=session.user_id).first()

def validate_licence(licence: str):
    if not licence:
        return None
    session = Licence.query.filter_by(id=licence).first()
    if not session:
        return None
    return session

def authenticate_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.cookies.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        user = validate_token(token)
        if not user:
            # Redirect to login page if not authenticated
            return redirect(url_for("auth.login_page"))
        return f(*args, user=user, **kwargs)
    return decorated_function

def authenticate_licence(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.cookies.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        licence = validate_licence(token)
        if not licence:
            # Redirect to login page if not authenticated
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, licence=licence, **kwargs)
    return decorated_function
