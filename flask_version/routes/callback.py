from flask import Blueprint, request, redirect, url_for, session, flash
from models.auth import ClioApiToken, ClioApiGateway

from typing import Optional, Literal, Dict, Any, List
import sqlite3

callback_bp = Blueprint('callback', __name__)

@callback_bp.route('/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if state != session.get('oauth_state'):
        flash("Invalid state parameter.", "error")
        return redirect(url_for('index'))

    app_data = load_from_db("clio_api_gateway", session.get('app_id'))
    if not app_data:
        flash("Application not found", "error")
        return redirect(url_for('index'))

    gateway = ClioApiGateway(**app_data)
    token = ClioApiToken(gateway=gateway)
    try:
        token.exchange_code_for_token(code)
        session['access_token'] = token.access_token
        session['refresh_token'] = token.refresh_token
        session['expires_at'] = token.expires_at.isoformat()
        flash("Successfully authenticated!", "success")
    except ValueError as e:
        flash(f"Error retrieving token: {str(e)}", "error")
        return redirect(url_for('index'))

    return redirect(url_for('dashboard'))

@callback_bp.route('/auth/<int:app_id>')
def authenticate_app(app_id):
    app_data = load_from_db("clio_api_gateway", app_id)
    if not app_data:
        return "Application not found", 404
    session['app_id'] = app_id
    gateway = ClioApiGateway(**app_data)
    token = ClioApiToken(gateway=gateway)
    auth_url = token.generate_auth_url()
    return redirect(auth_url)

# Database operations
def save_to_db(table_name: str, data: Dict[str, Any]):
    conn = sqlite3.connect('clio_api.db')
    cursor = conn.cursor()
    keys, values = zip(*data.items())
    cursor.execute(f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({', '.join('?' for _ in values)})", values)
    conn.commit()
    conn.close()

def load_from_db(table_name: str, id: int) -> Dict[str, Any]:
    conn = sqlite3.connect('clio_api.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(zip([column[0] for column in cursor.description], row)) if row else None
