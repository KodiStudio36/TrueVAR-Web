import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required to manage YouTube livestreams
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Files
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_PICKLE = "youtube_token.pkl"

def main():
    # Check if the token already exists
    if os.path.exists(TOKEN_PICKLE):
        print(f"{TOKEN_PICKLE} already exists. Delete it if you want to reauthorize.")
        return

    # Run OAuth flow (opens browser)
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)

    # Save credentials to pickle for later use
    with open(TOKEN_PICKLE, "wb") as f:
        pickle.dump(creds, f)

    print(f"Authorization complete! Credentials saved to {TOKEN_PICKLE}.")

if __name__ == "__main__":
    main()
