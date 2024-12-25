import base64
from datetime import date
from flask import jsonify, request
from app.api import bp
from app.authenticate import authenticate
from app.extensions import db

from app.models.user import User
from app.models.licence import Licence

@bp.route('/licence/authorize', methods=['POST'])
@authenticate
def authorize_licence(user: User):
    key = request.form['key']
    hash = request.form['hash']

    if not key or not hash:
        return jsonify({"error": "Licence key or computer hash is missing"}), 401
    
    licence: Licence = Licence.query.filter_by(user_email=user.email, key=key).first()

    if not licence:
        return jsonify({"error": "Licence not authorized"}), 401
    
    if not licence.active or licence.active < date.today():
        return jsonify({"error": "Licence not authorized"}), 401
    
    try:
        hash = base64.b64decode(hash.encode("ascii"))
    except:
        return jsonify({"error": "Invalid computer hash format"}), 401

    if licence.pc_hash:
        if licence.pc_hash == hash:
            return jsonify({"message": "ok"}), 200

    else:
        licence.pc_hash = hash
        db.session.commit()
        return jsonify({"message": "ok"}), 200

    return jsonify({"error": "Licence not authorized"}), 401
