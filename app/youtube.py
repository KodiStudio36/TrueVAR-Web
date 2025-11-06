import os
import pickle, pytz, mimetypes
from datetime import datetime, timezone

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload

# Scopes: only need to manage livestreams
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TOKEN_PICKLE = "youtube_token.pkl"
CLIENT_SECRET_FILE = "client_secret.json"

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as f:
            creds = pickle.load(f)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("youtube", "v3", credentials=creds)

def create_playlist(title, description, privacy="private"):
    youtube = get_youtube_service()

    try:
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
        )
        response = request.execute()
        playlist_id = response["id"]
        print(f"✅ Success: Created new playlist with ID: {playlist_id}")
        return playlist_id
    except Exception as e:
        print(f"❌ Error: Failed to create playlist: {e}")
        return None

def add_video_to_playlist(playlist_id, video_id):
    youtube = get_youtube_service()

    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        request.execute()
        print(f"✅ Success: Broadcast ID {video_id} added to Playlist ID {playlist_id}.")
        return True
    except Exception as e:
        print(f"❌ Error: Failed to add video to playlist: {e}")
        return False

def schedule_livestream(title, description, start_time, stream_key, privacy="private"):
    youtube = get_youtube_service()

    # Convert to UTC explicitly
    if start_time.tzinfo is None:
        start_time = pytz.timezone("Europe/Bratislava").localize(start_time)  # adjust to your local tz
    start_time_utc = start_time.astimezone(pytz.UTC)

    start_iso = start_time_utc.isoformat()

    broadcast_request = youtube.liveBroadcasts().insert(
        part="snippet,contentDetails,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": start_iso
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            },
            "contentDetails": {
                "enableAutoStart": False,
                "enableAutoStop": False
            }
        }
    )
    broadcast_response = broadcast_request.execute()
    broadcast_id = broadcast_response["id"]

    # ⭐️ Get the liveChatId from the response snippet
    try:
        live_chat_id = broadcast_response["snippet"]["liveChatId"]
        print(f"✅ Extracted Live Chat ID: {live_chat_id}")
    except KeyError:
        print("❌ Error: liveChatId not found in broadcast response. Cannot post comment.")
        live_chat_id = None

    youtube.videos().update(
        part="snippet",
        body={
            "id": broadcast_id,
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "17",  # Sports
                "tags": ["Taekwondo", "Martial Arts", "Tournament", "Court"]
            }
        }
    ).execute()

    # Step 3: Bind broadcast to live stream
    bind_request = youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_key.id
    )
    bind_response = bind_request.execute()

    return broadcast_id, live_chat_id

def set_thumbnail(video_id, image_file_stream, filename=None):
    youtube = get_youtube_service()

    try:
        # Detect MIME type from filename (fallback to jpeg)
        if filename:
            mimetype, _ = mimetypes.guess_type(filename)
        else:
            mimetype = "image/jpeg"

        media = MediaIoBaseUpload(
            image_file_stream,
            mimetype=mimetype,
            resumable=False
        )

        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=media
        )
        response = request.execute()
        print(f"✅ Success: Uploaded thumbnail for Video ID {video_id}.")
        return True
    except Exception as e:
        print(f"❌ Error: Failed to set thumbnail for Video ID {video_id}. {e}")
        return False

def check_stream_status(stream_id):
    youtube = get_youtube_service()

    request = youtube.liveStreams().list(
        part="status",
        id=stream_id
    )
    response = request.execute()
    status = response["items"][0]["status"]["streamStatus"]
    return status  # "active" or "inactive"

def start_broadcast(broadcast_id):
    youtube = get_youtube_service()
    try:
        request = youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=broadcast_id,
            part="status"
        )
        response = request.execute()
        print(f"✅ Broadcast {broadcast_id} is now LIVE")
        return response
    except Exception as e:
        print(f"❌ Error starting broadcast: {e}")
        return None
    
def stop_broadcast(broadcast_id):
    youtube = get_youtube_service()
    try:
        request = youtube.liveBroadcasts().transition(
            broadcastStatus="complete",
            id=broadcast_id,
            part="status"
        )
        response = request.execute()
        print(f"🛑 Broadcast {broadcast_id} is now STOPPED")
        return response
    except Exception as e:
        print(f"❌ Error stopping broadcast: {e}")
        return None
    
def format_timestamp_link(broadcast_id, timestamp_seconds):
    return f"https://youtube.com/live/{broadcast_id}?t={timestamp_seconds}"

def get_livestream_runtime_timestamp(broadcast_id):
    youtube = get_youtube_service()
    request = youtube.liveBroadcasts().list(
        part="snippet,contentDetails,status",
        id=broadcast_id
    )
    response = request.execute()

    if not response["items"]:
        return None, None

    broadcast = response["items"][0]
    actual_start_time = broadcast["snippet"].get("actualStartTime")
    if not actual_start_time:
        return None, None

    start_time = datetime.fromisoformat(actual_start_time.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    delta = now - start_time
    total_seconds = int(delta.total_seconds())

    hours = total_seconds // 60 // 60
    minutes = total_seconds // 60 % 60
    seconds = total_seconds % 60
    timestamp = f"{f"{hours}:" if hours > 0 else ""}{minutes:02d}:{seconds:02d}"

    return timestamp, total_seconds

def get_live_chat_id(broadcast_id):
    youtube = get_youtube_service()
    response = youtube.liveBroadcasts().list(
        part="snippet",
        id=broadcast_id
    ).execute()

    items = response.get("items", [])
    if not items:
        print("No broadcast found.")
        return None

    live_chat_id = items[0]["snippet"].get("liveChatId")
    print("💬 liveChatId:", live_chat_id)
    return live_chat_id

def insert_live_chat_message(live_chat_id, message_text):
    youtube = get_youtube_service()
    """
    Inserts a new text message into the specified live chat.
    This function requires proper OAuth 2.0 authorization with appropriate scopes.
    """
    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "type": "textMessageEvent",
                    "liveChatId": live_chat_id,
                    "textMessageDetails": {
                        "messageText": message_text
                    }
                }
            }
        )
        response = request.execute()
        print(f"✅ Success: Posted live chat message: '{response['snippet']['textMessageDetails']['messageText']}'")
        return response
    except Exception as e:
        print(f"❌ Error: Failed to post live chat message. Ensure API scopes are correct and the chat is active: {e}")

def append_fight_messages_to_description(broadcast_id: str, messages: str):
    """
    Append messages string to the broadcast description on YouTube.
    """
    youtube = get_youtube_service()

    try:
        # 1️⃣ Fetch current broadcast snippet
        broadcast_response = youtube.liveBroadcasts().list(
            part="snippet",
            id=broadcast_id
        ).execute()

        items = broadcast_response.get("items", [])
        if not items:
            return False, "Broadcast not found"

        snippet = items[0]["snippet"]
        current_description = snippet.get("description", "")

        # 2️⃣ Append messages to description
        updated_description = f"{current_description}\n\nFights summary:\n{messages}"
        snippet["description"] = updated_description

        # 3️⃣ Update broadcast
        youtube.liveBroadcasts().update(
            part="snippet",
            body={
                "id": broadcast_id,
                "snippet": snippet
            }
        ).execute()

        return True, updated_description

    except Exception as e:
        print(f"❌ Error updating description: {e}")
        return False, str(e)