import os, uuid
from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta
from app.authenticate import authenticate_redirect
from app.dashboard import bp
from app.models.user import User
from app.extensions import db
from app.scheduler import schedule_tournament

from app.models.tournament import Tournament
from app.models.thumbnail import Thumbnail
from app.models.licence import Licence
from app.models.stream_key import StreamKey


UPLOAD_FOLDER = "app/static/uploads"
MAX_FILE_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_MIMES = ['image/jpeg', 'image/png']

@bp.route("/")
@authenticate_redirect
def dashboard(user):
    licences = user.licences  # SQLAlchemy relationship
    tournaments = user.tournaments  # SQLAlchemy relationship

    return render_template(
        "dashboard.html",
        user=user,
        licences=licences,
        tournaments=tournaments
    )

# Tournament creation page
@bp.route("/tournament/create", methods=["GET"])
@authenticate_redirect
def create_tournament_page(user):
    return render_template("create_tournament.html", user=user)

@bp.route("/tournament/create", methods=["POST"])
@authenticate_redirect
def create_tournament(user):
    name = request.form.get("name")
    start_date = request.form.get("start_date")
    start_time = request.form.get("start_time")
    court_num = request.form.get("court_num")
    location = request.form.get("location")
    is_streaming = bool(request.form.get("is_streaming"))

    if not name or not court_num or not start_date or not start_time or not location:
        return render_template("create_tournament.html", user=user, error="All fields are required.")

    try:
        start_str = f"{start_date} {start_time}"
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        court_num = int(court_num)
    except ValueError:
        return render_template("create_tournament.html", user=user, error="Invalid date, time, or court number.")

    uploaded_files = request.files.getlist('thumbnails')
    files_to_process = []
    
    if is_streaming:
        # Check file count matching court number
        if len(uploaded_files) != court_num:
            return render_template(
                "create_tournament.html", 
                user=user, 
                error=f"Streaming requires {court_num} thumbnails, but {len(uploaded_files)} were uploaded."
            )

        # Validate each file size and type
        for file in uploaded_files:
            if file.filename == '':
                return render_template(
                    "create_tournament.html", 
                    user=user, 
                    error="One or more thumbnail inputs were left empty."
                )
            
            # Reset pointer to start for size check
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0) # IMPORTANT: Reset pointer for later reading by YouTube API
            
            if file_size > MAX_FILE_SIZE:
                return render_template(
                    "create_tournament.html", 
                    user=user, 
                    error=f"File {file.filename} is too large. Max size is 2MB."
                )
            
            if file.mimetype not in ALLOWED_IMAGE_MIMES:
                 return render_template(
                    "create_tournament.html", 
                    user=user, 
                    error=f"File {file.filename} is not a supported image type (JPEG or PNG)."
                )

            files_to_process.append(file)

    tournament = Tournament(
        name=name,
        court_num=court_num,
        user_id=user.id,
        start=start,
        location=location,
        is_streaming=is_streaming
    )
    db.session.add(tournament)
    db.session.commit()

    for idx, file in enumerate(files_to_process, start=1):
        ext = file.filename.rsplit(".", 1)[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(save_path)

        thumbnail = Thumbnail(tournament.id, idx, unique_name)

        db.session.add(thumbnail)
        db.session.commit()

    now = datetime.utcnow()
    tomorrow_end = now + timedelta(days=1) + timedelta(days=1)

    if is_streaming and tournament.start <= tomorrow_end:
        schedule_tournament(tournament)

    return redirect(url_for("dashboard.dashboard"))

@bp.route("/tournament/delete/<tournament_id>", methods=["POST"])
@authenticate_redirect
def delete_tournament(user, tournament_id):
    tournament = Tournament.query.filter_by(id=tournament_id, user_id=user.id).first()
    if not tournament:
        return redirect(url_for("dashboard.dashboard"))
    
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for("dashboard.dashboard"))