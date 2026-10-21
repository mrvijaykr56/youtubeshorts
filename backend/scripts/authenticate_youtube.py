"""
YouTube Channel Authentication Utility
Authenticates with Google YouTube Data API v3 and stores the OAuth token in backend/token.json
for seamless one-click uploading to @MagicalTalesKidz.
"""

import os
import sys
import traceback

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client_secrets_file = os.path.join(backend_dir, "client_secret.json")
token_file = os.path.join(backend_dir, "token.json")

scopes = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def authenticate():
    print("=" * 65, flush=True)
    print("🔐 YouTube OAuth Setup for @MagicalTalesKidz", flush=True)
    print("=" * 65, flush=True)
    
    if not os.path.exists(client_secrets_file):
        print(f"\n❌ Error: '{client_secrets_file}' not found.", flush=True)
        return False

    try:
        import google_auth_oauthlib.flow
        import googleapiclient.discovery
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        credentials = None
        if os.path.exists(token_file):
            print("Found existing token.json, verifying...", flush=True)
            try:
                credentials = Credentials.from_authorized_user_file(token_file, scopes)
            except Exception as e:
                print(f"Token read error: {e}", flush=True)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("Refreshing expired credentials...", flush=True)
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f"Refresh failed: {e}. Initiating new browser login...", flush=True)
                    credentials = None

            if not credentials:
                print("\nInitiating clean OAuth flow...", flush=True)
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes
                )
                
                # Single, clean invocation of run_local_server
                # It starts a local server on port 8080 (or ephemeral), automatically generates
                # the exact authorization URL, prints it, and opens the user's default browser.
                credentials = flow.run_local_server(
                    port=0,
                    authorization_prompt_message="\n👉 VISIT THIS URL TO AUTHORIZE:\n{url}\n\nWaiting for browser callback...",
                    open_browser=True
                )

            with open(token_file, "w") as f:
                f.write(credentials.to_json())
            print(f"\n✅ Credentials successfully saved to {token_file}!", flush=True)

        # Verify which channel is connected
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        channels_res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        if "items" in channels_res and len(channels_res["items"]) > 0:
            ch = channels_res["items"][0]
            title = ch["snippet"]["title"]
            custom_url = ch["snippet"].get("customUrl", "")
            subs = ch["statistics"].get("subscriberCount", "0")
            print("\n🎉 CONNECTED CHANNEL DETAILS:", flush=True)
            print(f"   Channel Name: {title}", flush=True)
            print(f"   Handle: {custom_url}", flush=True)
            print(f"   Subscribers: {subs}", flush=True)
            print(f"   Status: READY FOR AUTOMATED UPLOADS!", flush=True)
        else:
            print("Connected, but no primary channel found for this Google account.", flush=True)

        return True
    except Exception as exc:
        print(f"\n❌ Authentication failed: {exc}", flush=True)
        traceback.print_exc()
        return False

if __name__ == "__main__":
    authenticate()
