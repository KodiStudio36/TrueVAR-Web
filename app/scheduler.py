from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.extensions import db
from app.models.thumbnail import Thumbnail
from app.models.tournament import Tournament
from app.models.stream_key import StreamKey
from app.models.stream import Stream
from app.models.licence import Licence
from app.youtube import schedule_livestream, create_playlist, add_video_to_playlist, set_thumbnail

def schedule_tournament(tournament: Tournament):
    try:
        # playlist_id = create_playlist(tournament.name, f"Official Taekwondo livestreams from {tournament.name}", "private")

        for i in range(tournament.court_num):
            court_number = i + 1
            # current_file = files_to_process[i]

            stream_key = StreamKey.query.filter_by(court=court_number).first()
            if not stream_key:
                raise Exception(f"Stream key for Court {court_number} not found.")
            
            description = (
                f"🏆 {tournament.name} - Taekwondo Tournament\n"
                f"📍{tournament.location}\n\n"
                f"This livestream covers all matches happening on court number {court_number}.\n"
                f"Follow along for live Taekwondo action, updated match results, and highlights!\n\n"
                f"📢 Subscribe to stay updated on Taekwondo events and future livestreams."
            )

            video_id, live_chat_id = schedule_livestream(
                title=f"{tournament.name} Court {court_number}",
                description=description,
                start_time=tournament.start,
                stream_key=stream_key,
                privacy="unlisted",
            )

            thumbnail = Thumbnail.query.filter(
                Thumbnail.tournament_id == tournament.id,
                Thumbnail.court == court_number
            ).first()

            with open(f"app/static/uploads/{thumbnail.path}", "rb") as f:
                set_thumbnail(video_id, f)

            # Add stream to playlist
            # if playlist_id:
            #     add_video_to_playlist(playlist_id, video_id)

            licence = Licence.query.filter_by(user_id=tournament.user_id, court=court_number).first()
            if licence:
                db.session.add(Stream(video_id, tournament.id, licence.id, stream_key.stream_key, live_chat_id))

            tournament.scheduled = True
            db.session.commit()
    except Exception as e:
        print(f"Failed to schedule livestream: {e}")

def schedule_tournaments(app):
    with app.app_context():
        """Run every day at e.g. 06:00, schedule livestreams for tournaments starting tomorrow."""
        print("scheduler ran")
        now = datetime.utcnow()
        tomorrow_start = now + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(days=1)

        tournaments = Tournament.query.filter(
            Tournament.start >= tomorrow_start,
            Tournament.start < tomorrow_end,
            Tournament.is_streaming == True,
            Tournament.scheduled == None  # only if not already scheduled
        ).all()

        print(tomorrow_start, tomorrow_end, tournaments)

        for tournament in tournaments:
            schedule_tournament(tournament)

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: schedule_tournaments(app),
        trigger="cron",
        hour=16,
        minute=55,
    )
    scheduler.start()