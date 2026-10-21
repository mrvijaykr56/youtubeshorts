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
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client_secrets_file = os.path.join(backend_dir, "client_secret.json")
token_file = os.path.join(backend_dir, "token.json")

scopes = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
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
                import json
                with open(token_file, "r") as tf:
                    token_data = json.load(tf)
                granted_scopes = set(token_data.get("scopes", []))
                if not set(scopes).issubset(granted_scopes):
                    print("⚠️ Existing token is missing newly requested scopes (youtube.force-ssl).", flush=True)
                    print("Re-authenticating to upgrade account permissions...", flush=True)
                    credentials = None
                else:
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
                import wsgiref.simple_server
                import wsgiref.util
                import webbrowser

                class RobustOAuthWSGIApp:
                    def __init__(self):
                        self.auth_response_uri = None

                    def __call__(self, environ, start_response):
                        uri = wsgiref.util.request_uri(environ)
                        if "code=" in uri or "error=" in uri:
                            self.auth_response_uri = uri
                            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                            return [b"""<html><body style="font-family:sans-serif;text-align:center;padding:50px;background:#0f172a;color:#f8fafc;">
                                <h1 style="color:#22c55e;">&#9989; YouTube Authorization Successful!</h1>
                                <p style="font-size:18px;">Full account management permissions granted.</p>
                                <p style="color:#94a3b8;">You may close this tab and return to the editor.</p>
                            </body></html>"""]
                        start_response("204 No Content", [])
                        return []

                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes
                )

                app = RobustOAuthWSGIApp()
                local_server = wsgiref.simple_server.make_server("localhost", 0, app)
                port = local_server.server_port
                flow.redirect_uri = f"http://localhost:{port}/"
                auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")

                print(f"\n👉 VISIT THIS URL TO AUTHORIZE:\n{auth_url}\n", flush=True)
                print("Waiting for browser callback...", flush=True)

                webbrowser.open(auth_url)

                while not app.auth_response_uri:
                    local_server.handle_request()

                local_server.server_close()

                auth_response = app.auth_response_uri.replace("http:", "https:")
                flow.fetch_token(authorization_response=auth_response)
                credentials = flow.credentials

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
