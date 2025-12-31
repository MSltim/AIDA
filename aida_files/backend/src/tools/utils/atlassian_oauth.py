import os
import json
import secrets
import hashlib
import base64
import http.server
import threading
import urllib.parse
import webbrowser
from typing import Optional, Tuple
from datetime import datetime, timedelta

import httpx


# =============================================================================
# ATLASSIAN OAUTH 2.0 CONFIGURATION
# =============================================================================
ATLASSIAN_OAUTH_CONFIG = {
    "client_id": os.getenv("ATLASSIAN_CLIENT_ID"),
    "client_secret": os.getenv("ATLASSIAN_SECRET_KEY"),  # Using SECRET_KEY from your .env
    "auth_url": "https://auth.atlassian.com/authorize",
    "token_url": "https://auth.atlassian.com/oauth/token",
    "redirect_uri": "http://localhost:8089/callback",
    "scopes": [
        "read:jira-work",
        "write:jira-work",
        "read:jira-user",
        "read:confluence-content.all",
        "write:confluence-content",
        "read:confluence-space.summary",
        "offline_access",  # For refresh token
    ],
}

# Token storage file (for persistence)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".atlassian_tokens.json")


class AtlassianOAuth:
    """
    Handles OAuth 2.0 (3LO) authentication for Atlassian MCP.
    
    This implements the Authorization Code flow with PKCE for secure authentication.
    """
    
    def __init__(self):
        self.client_id = ATLASSIAN_OAUTH_CONFIG["client_id"]
        self.client_secret = ATLASSIAN_OAUTH_CONFIG["client_secret"]
        self.auth_url = ATLASSIAN_OAUTH_CONFIG["auth_url"]
        self.token_url = ATLASSIAN_OAUTH_CONFIG["token_url"]
        self.redirect_uri = ATLASSIAN_OAUTH_CONFIG["redirect_uri"]
        self.scopes = ATLASSIAN_OAUTH_CONFIG["scopes"]
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Load existing tokens if available
        self._load_tokens()
    
    def _generate_pkce(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_verifier, code_challenge
    
    def _save_tokens(self):
        """Save tokens to file for persistence"""
        if self.access_token:
            data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            }
            with open(TOKEN_FILE, "w") as f:
                json.dump(data, f)
            print("  [OK] Tokens saved to file")
    
    def _load_tokens(self):
        """Load tokens from file if they exist"""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                if data.get("expires_at"):
                    self.token_expires_at = datetime.fromisoformat(data["expires_at"])
                print("  [OK] Loaded saved tokens")
            except Exception as e:
                print(f"  [WARN] Could not load saved tokens: {e}")
    
    def is_token_valid(self) -> bool:
        """Check if the current access token is valid"""
        if not self.access_token:
            return False
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return False
        return True
    
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            print("  [WARN] No refresh token available")
            return False
        
        print("  [REFRESH] Refreshing access token...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                
                if response.status_code == 200:
                    tokens = response.json()
                    self.access_token = tokens["access_token"]
                    self.refresh_token = tokens.get("refresh_token", self.refresh_token)
                    expires_in = tokens.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    self._save_tokens()
                    print("  [OK] Token refreshed successfully")
                    return True
                else:
                    print(f"  [FAIL] Refresh failed: {response.status_code}")
                    print(f"     {response.text}")
                    return False
            except Exception as e:
                print(f"  [FAIL] Refresh error: {e}")
                return False
    
    async def get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        # Check if we have a valid token
        if self.is_token_valid():
            return self.access_token
        
        # Try to refresh
        if self.refresh_token:
            if await self.refresh_access_token():
                return self.access_token
        
        # Need to do full OAuth flow
        return await self.authenticate()
    
    async def authenticate(self) -> Optional[str]:
        """
        Perform the full OAuth 2.0 authentication flow.
        Opens a browser for user authorization.
        """
        if not self.client_id or not self.client_secret:
            print("  [FAIL] Missing ATLASSIAN_CLIENT_ID or ATLASSIAN_CLIENT_SECRET in .env")
            return None
        
        print("\n  [AUTH] Starting Atlassian OAuth 2.0 authentication...")
        
        # Generate PKCE
        code_verifier, code_challenge = self._generate_pkce()
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(auth_params)}"
        
        # Set up callback server
        auth_code = None
        received_state = None
        server_error = None
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code, received_state, server_error
                
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                
                if "error" in params:
                    server_error = params.get("error_description", params["error"])[0]
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"<h1>[ERROR] Error: {server_error}</h1>".encode())
                elif "code" in params:
                    auth_code = params["code"][0]
                    received_state = params.get("state", [None])[0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>&#10004; Authorization successful!</h1><p>You can close this window.</p>")
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Invalid callback</h1>")
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        # Start local server
        server = http.server.HTTPServer(("localhost", 8089), CallbackHandler)
        server.timeout = 120  # 2 minute timeout
        
        # Open browser
        print(f"  [BROWSER] Opening browser for authorization...")
        print(f"     If browser doesn't open, visit:")
        print(f"     {auth_url[:80]}...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        print("  [WAITING] Waiting for authorization (2 min timeout)...")
        
        def handle_request():
            server.handle_request()
        
        thread = threading.Thread(target=handle_request)
        thread.start()
        thread.join(timeout=120)
        
        server.server_close()
        
        if server_error:
            print(f"  [FAIL] Authorization error: {server_error}")
            return None
        
        if not auth_code:
            print("  [FAIL] No authorization code received (timeout)")
            return None
        
        if received_state != state:
            print("  [FAIL] State mismatch - possible CSRF attack")
            return None
        
        print("  [OK] Authorization code received")
        
        # Exchange code for tokens
        print("  [EXCHANGE] Exchanging code for tokens...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": auth_code,
                        "redirect_uri": self.redirect_uri,
                        "code_verifier": code_verifier,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                
                if response.status_code == 200:
                    tokens = response.json()
                    self.access_token = tokens["access_token"]
                    self.refresh_token = tokens.get("refresh_token")
                    expires_in = tokens.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    self._save_tokens()
                    print("  [OK] OAuth authentication successful!")
                    return self.access_token
                else:
                    print(f"  [FAIL] Token exchange failed: {response.status_code}")
                    print(f"     {response.text}")
                    return None
            except Exception as e:
                print(f"  [FAIL] Token exchange error: {e}")
                return None


# Global OAuth handler
atlassian_oauth = AtlassianOAuth()
