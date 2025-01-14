from flask import Flask, request, redirect, render_template, url_for
from dotenv import load_dotenv, set_key
from urllib.parse import urlencode
import os

from routes.routes import token_routes, update_app, set_globals

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.register_blueprint(token_routes)

# OAuth 2.0 Configuration
client_id = os.getenv("CLIENT_ID", "").strip()
client_secret = os.getenv("CLIENT_SECRET", "").strip()
redirect_uri = os.getenv("REDIRECT_URI")

globals_set = False
def update_env(new_client_id, new_client_secret, new_redirect_uri):
    # Save the new values to the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    set_key(dotenv_path, "CLIENT_ID", new_client_id)
    set_key(dotenv_path, "CLIENT_SECRET", new_client_secret)
    set_key(dotenv_path, "REDIRECT_URI", new_redirect_uri)
    
@app.route('/')
def index():
    """Render the index page and check if CLIENT_ID and CLIENT_SECRET are missing."""
    global client_id, client_secret, redirect_uri, globals_set
    # Check both global variables and environment variables
    missing_env = not (
        client_id and client_secret and redirect_uri and
        client_id != "ChangeMe" and client_secret != "ChangeMe"
    )
    
    if not missing_env and not globals_set:
        set_globals()
        globals_set = True
    print(f"CLIENT_ID: {client_id}, CLIENT_SECRET: {client_secret}, missing_env: {missing_env}")
    return render_template('token_manager.html', missing_env=missing_env, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

@app.route('/set_env', methods=['POST'])
def set_env():
    """Save client_id and client_secret to the .env file."""
    new_client_id = request.form.get('client_id')
    new_client_secret = request.form.get('client_secret')
    new_redirect_uri = request.form.get('redirect_uri')

    if not new_client_id or not new_client_secret:
        return "Both Client ID and Client Secret are required.", 400

    # Update the global variables directly
    global client_id, client_secret, redirect_uri, globals_set
    client_id = new_client_id
    client_secret = new_client_secret
    redirect_uri = new_redirect_uri

    update_env(new_client_id, new_client_secret, new_redirect_uri)
    
    if not globals_set:
        set_globals()
        update_app(new_client_id, new_client_secret, new_redirect_uri)
        globals_set = True
    else:
        update_app(new_client_id, new_client_secret, new_redirect_uri)
    # Redirect to /authorize to continue the OAuth process
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", True)
    app.run(host=FLASK_HOST, debug=FLASK_DEBUG, port=FLASK_PORT, use_reloader=False)
