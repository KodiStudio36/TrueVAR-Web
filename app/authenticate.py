import bcrypt
from functools import wraps
from flask import request, jsonify

from app.models.user import User
from app.models.authentication import Authentication

# Mock token validation function
def validate_creds(email: str, passwd: str):
    """Validate the token (mock example)."""
    # Replace with actual token validation logic
    auth: Authentication = Authentication.query.filter_by(email=email).first()
    passwd = passwd.encode('utf-8')

    if auth and bcrypt.checkpw(passwd, auth.passwd) :
        return User.query.filter_by(email=email).first()
    
    return None

# Authentication decorator
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        email = request.headers.get('Email')
        passwd = request.headers.get('Password')
        if not email or not passwd:
            return jsonify({"error": "Authorization headers are missing"}), 401
        
        # Check if the token is valid
        user = validate_creds(email, passwd)
        if not user:
            return jsonify({"error": "Invalid authorization headers"}), 401
        
        # Proceed with the request if authenticated
        return f(*args, user=user, **kwargs)
    return decorated_function