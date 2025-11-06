import base64
from datetime import date
from sqlalchemy import func, cast, Date
from flask import jsonify, request
from app.api import bp
from app.authenticate import authenticate_licence
from app.extensions import db

from app.models import tournament
from app.models.fight import Fight
from app.models.stream_key import StreamKey
from app.models.stream import Stream
from app.models.licence import Licence
from app.models.tournament import Tournament
from app.youtube import append_fight_messages_to_description, check_stream_status, format_timestamp_link, get_live_chat_id, get_livestream_runtime_timestamp, insert_live_chat_message, start_broadcast, stop_broadcast

@bp.route('/licence/stream/check', methods=['GET'])
@authenticate_licence
def licence_stream_check(licence: Licence):
    today = date.today()
    tournaments = [tournament for tournament in Tournament.query.filter(Tournament.user_id == licence.user_id).all() if tournament.start.date() == today]
    if len(tournaments) == 0:
        return jsonify({
            "error": "No tournament scheduled for today"
        }), 404

    tournament = tournaments[0]
    stream = Stream.query.filter_by(tournament_id=tournament.id, licence_id=licence.id).first()
    stream_id = StreamKey.query.filter_by(stream_key=stream.stream_key).first()

    if not stream_id:
        return jsonify({"error": "No stream linked with licence"}), 406

    response = check_stream_status(stream_id.id)

    if not response:
        return jsonify({"error": "Something went wrong"}), 500

    return response

@bp.route('/licence/stream/start', methods=['POST'])
@authenticate_licence
def licence_stream_start(licence: Licence):
    today = date.today()
    tournaments = [tournament for tournament in Tournament.query.filter(Tournament.user_id == licence.user_id).all() if tournament.start.date() == today]
    if len(tournaments) == 0:
        return jsonify({
            "error": "No tournament scheduled for today"
        }), 404
    tournament = tournaments[0]
    stream = Stream.query.filter_by(tournament_id=tournament.id, licence_id=licence.id).first()

    if not stream.id:
        return jsonify({"error": "No stream linked with licence"}), 406

    response = start_broadcast(stream.id)

    if not response:
        return jsonify({"error": "Something went wrong"}), 500

    return jsonify({"status": "ok"}), 200

@bp.route('/licence/stream/stop', methods=['POST'])
@authenticate_licence
def licence_stream_stop(licence: Licence):
    today = date.today()
    tournaments = [tournament for tournament in Tournament.query.filter(Tournament.user_id == licence.user_id).all() if tournament.start.date() == today]
    if len(tournaments) == 0:
        return jsonify({
            "error": "No tournament scheduled for today"
        }), 404
    tournament = tournaments[0]
    stream = Stream.query.filter_by(tournament_id=tournament.id, licence_id=licence.id).first()

    if not stream.id:
        return jsonify({"error": "No stream linked with licence"}), 406

    response = stop_broadcast(stream.id)

    fights = Fight.query.filter_by(stream_id=stream.id).order_by(Fight.id).all()
    if not fights:
        return jsonify({"error": "No fights found for this broadcast"}), 404

    # Combine messages into one string
    messages_str = "\n".join([fight.message for fight in fights])

    append_fight_messages_to_description(stream.id, "00:00 Start of the Tournament\n" + messages_str)

    if not response:
        return jsonify({"error": "Something went wrong"}), 500

    return jsonify({"status": "ok"}), 200

@bp.route('/licence/stream/fight', methods=['PUT'])
@authenticate_licence
def licence_stream_new_fight(licence: Licence):
    data = request.get_json()
    message = data.get("message", "").strip()

    today = date.today()
    tournaments = [tournament for tournament in Tournament.query.filter(Tournament.user_id == licence.user_id).all() if tournament.start.date() == today]
    if len(tournaments) == 0:
        return jsonify({
            "error": "No tournament scheduled for today"
        }), 404
    tournament = tournaments[0]
    stream = Stream.query.filter_by(tournament_id=tournament.id, licence_id=licence.id).first()

    if not message:
        return jsonify({"error": "Message text required"}), 400

    # You should have live_chat_id stored with the licence or retrievable via broadcast_id
    if not stream.live_chat_id:
        return jsonify({"error": "Live chat not found or inactive"}), 404

    # Get livestream timestamp
    timestamp, total_seconds = get_livestream_runtime_timestamp(stream.id)
    formatted_message = f"{timestamp} {message}"

    db.session.add(Fight(stream.id, formatted_message))
    db.session.commit()

    success = insert_live_chat_message(stream.live_chat_id, formatted_message)

    if not success:
        live_chat_id = get_live_chat_id(stream.id)
        success = insert_live_chat_message(live_chat_id, formatted_message)

        if not success:
            return jsonify({"error": "Failed to post message"}), 500
        
        else:
            stream.live_chat_id = live_chat_id
            db.session.commit()

    return jsonify({"status": "ok", "sent": formatted_message}), 200
