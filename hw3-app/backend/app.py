from flask import Flask, jsonify, redirect, session, send_from_directory
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from dotenv import load_dotenv
from pymongo import MongoClient
from comment_routes import comment_bp
import os

#Load evn var based on FLASK_EVN
load_dotenv(dotenv_path='../.env')

env_mode = os.getenv("FLASK_ENV", "production")

if env_mode == "development":
    load_dotenv(dotenv_path='../.env.dev')
elif env_mode == "production":
    load_dotenv(dotenv_path='../.env.prod')

# Create Flask app and configure static/template paths
static_path = os.getenv('STATIC_PATH', '../frontend/dist')
template_path = os.getenv('TEMPLATE_PATH', '../frontend/dist')

app = Flask(__name__, static_folder=static_path, template_folder=template_path)

app.secret_key = os.urandom(24)
#Comment routes
app.register_blueprint(comment_bp)

oauth = OAuth(app)

#One time token for safety (Even those this project doesn't care)
nonce = generate_token()

oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    #server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

#TBH the env var is little bti strange, string with space in it
#Can also simply hard code the name here
client = oauth.create_client(os.getenv('OIDC_CLIENT_NAME'))

mongo_uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database()
users_collection = db.users

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    return client.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = client.authorize_access_token()
    nonce = session.get('nonce')

    user_info = client.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
    session['user'] = user_info
    # Store or update user in MongoDB
    if user_info:
        users_collection.update_one(
            {"sub": user_info["sub"]},     
            {"$set": user_info},           
            upsert=True                    
        )
    return redirect('/')

# Get Userinfo
@app.route('/me')
def me():
    return jsonify(session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
