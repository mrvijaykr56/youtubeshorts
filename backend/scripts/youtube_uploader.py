import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

scopes = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def upload_video(video_path, title="My Shorts", description="Generated video", tags=None, privacy_status="private", category_id="1"):
    """
    Uploads a video to YouTube using the YouTube Data API v3.
    Requires client_secret.json to be present in the backend root directory.
    Uses token.json to persist and reuse authorization credentials.
    """
    if tags is None:
        tags = ["shorts", "generated"]
        
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_secret.json")
    token_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "token.json")

    if not os.path.exists(client_secrets_file):
        print("Warning: client_secret.json not found. Skipping YouTube upload.")
        return None

    credentials = None

    # 1. Try loading cached credentials from token.json
    if os.path.exists(token_file):
        print("[youtube_uploader] Loading cached OAuth credentials from token.json...", flush=True)
        try:
            credentials = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception as e:
            print(f"[youtube_uploader] Warning: failed to read token.json: {e}", flush=True)

    # 2. If credentials don't exist, are invalid, or expired, refresh or run flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("[youtube_uploader] Cached credentials expired. Attempting dynamic refresh...", flush=True)
            try:
                credentials.refresh(Request())
            except Exception as e:
                print(f"[youtube_uploader] Dynamic refresh failed: {e}. Falling back to clean OAuth flow.", flush=True)
                credentials = None
                
        if not credentials:
            print("[youtube_uploader] No valid credentials found. Launching local auth server flow...", flush=True)
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_local_server(port=0)

        # 3. Save active credentials back to cache for subsequent uploads
        try:
            with open(token_file, "w") as token:
                token.write(credentials.to_json())
            print(f"[youtube_uploader] [OK] Successfully saved active credentials cache to {token_file}", flush=True)
        except Exception as e:
            print(f"[youtube_uploader] Warning: failed to save credentials cache: {e}", flush=True)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # pyrefly: ignore [missing-attribute]
    request = youtube.videos().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": str(category_id)
          },
          "status": {
            "privacyStatus": privacy_status
          }
        },
        
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    response = request.execute()
    print(f"Uploaded successfully. Video ID: {response['id']}")
    return response['id']
