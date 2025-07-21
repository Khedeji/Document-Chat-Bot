from flask import Flask
from flask_cors import CORS
import os
import sqlite3
from dotenv import load_dotenv

def init_sessions_db():
    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

load_dotenv()
init_sessions_db()


from routes.chat import ChatHandler
from routes.sessions import SessionsHandler
from routes.session_history import SessionHistoryHandler
from routes.new_session import NewSessionHandler
from routes.delete_session import DeleteSessionHandler

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

# Register Blueprints

app.register_blueprint(ChatHandler.bp)
app.register_blueprint(SessionsHandler.bp)
app.register_blueprint(SessionHistoryHandler.bp)
app.register_blueprint(NewSessionHandler.bp)
app.register_blueprint(DeleteSessionHandler.bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9999)
