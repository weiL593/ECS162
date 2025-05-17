from flask import Flask, redirect, url_for, session, send_from_directory, jsonify
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(dotenv_path='../.env')

# Create Flask app and configure static/template paths
static_path = os.getenv('STATIC_PATH', '../frontend/dist')
template_path = os.getenv('TEMPLATE_PATH', '../frontend/dist')

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
app.secret_key = os.urandom(24)

# Configure OAuth (Dex)
oauth = OAuth(app)
nonce = generate_token()
oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    authorization_endpoint="http://dex:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

# Return NYT API key
@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

# Login with Dex
@app.route('/login')
def login():
    session['nonce'] = nonce
    return oauth.flask_app.authorize_redirect('http://localhost:8000/authorize', nonce=nonce)

# Dex callback
@app.route('/authorize')
def authorize():
    token = oauth.flask_app.authorize_access_token()
    user_info = oauth.flask_app.parse_id_token(token, nonce=session.get('nonce'))
    session['user'] = user_info
    return redirect('/')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Serve frontend files
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
