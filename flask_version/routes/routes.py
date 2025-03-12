from flask import Blueprint, request, redirect, session, render_template, jsonify, url_for
import os
import base64
import requests

from urllib.parse import urlencode

# OAuth 2.0 Configuration
client_id = None
client_secret = None
redirect_uri = None
authorization_base_url = None
token_url = None
deauthorize_url = None

token_routes = Blueprint('token_routes', __name__)

def update_app(new_client_id, new_client_secret, new_redirect_uri):
    print("Updating App")
    global client_id, client_secret, redirect_uri
    client_id = new_client_id
    client_secret = new_client_secret
    redirect_uri = new_redirect_uri
    print(f"New client updated: {client_id}")
    print(f"New secret updated: {client_secret}")
    print(f"New secret updated: {redirect_uri}")

def set_globals():
    global client_id, client_secret, redirect_uri, authorization_base_url, token_url, deauthorize_url
    client_id = os.getenv("CLIENT_ID", "").strip()
    client_secret = os.getenv("CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("REDIRECT_URI")
    authorization_base_url = os.getenv("AUTH_BASE_URL")
    token_url = os.getenv("TOKEN_URL")
    deauthorize_url = os.getenv("DEAUTHORIZE_URL")    
    
@token_routes.route('/authorize')
def authorize():
    """Start the OAuth process or prompt for missing variables."""
    if not client_id or not client_secret or client_id == "ChangeMe" or client_secret == "ChangeMe":
        return redirect(url_for('index', missing_env=True))
    
    # Continue with OAuth process
    state = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8')
    session['oauth_state'] = state
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    print(params)
    authorization_url = f"{authorization_base_url}?{urlencode(params)}"
    return redirect(authorization_url)

@token_routes.route('/callback')
def callback():
    if request.args.get('state') != session.pop('oauth_state', None):
        return "Error: State mismatch", 400

    authorization_code = request.args.get('code')
    if not authorization_code:
        return "Error: Missing authorization code", 400

    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return f"Failed to obtain token: {response.text}", 400

    token_response = response.json()
    if "access_token" in token_response:

        return render_template(
            'callback.html',
            token_type=token_response.get("token_type"),
            access_token=token_response.get("access_token"),
            expires_in=token_response.get("expires_in"),
            refresh_token=token_response.get("refresh_token"),
        )
    else:
        return "Failed to obtain access token.", 400
    
@token_routes.route('/refresh_token', methods=['POST'])
def refresh_token():
    """Route to refresh the access token using the refresh token."""
    # Load the current refresh token
    refresh_token = request.json.get("refresh_token")  # Get from request payload
    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    # Data for token refresh
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    # Send POST request to the token endpoint
    response = requests.post(token_url, data=data)

    # Handle response
    if response.status_code == 200:
        token_response = response.json()
        return jsonify(token_response)  # Return the new token data
    else:
        return jsonify({"error": "Failed to refresh token", "details": response.text}), response.status_code

@token_routes.route('/revoke_token', methods=['POST'])
def revoke_token():
    """Route to revoke the access token."""
    token = request.json.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    data = {"token": token}

    try:
        response = requests.post(deauthorize_url, data=data, auth=(client_id, client_secret), timeout=10)

        if response.status_code == 200:
            return jsonify({"message": "Token successfully revoked"})
        else:
            return jsonify({"error": "Failed to revoke token", "details": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while contacting the deauthorization server", "details": str(e)}), 500
