from flask import Blueprint, request, jsonify
import sqlite3
import os

def delete_session_from_db(session_id):
    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    # Also delete chat history from chat_history.db
    conn2 = sqlite3.connect('chat_history.db')
    c2 = conn2.cursor()
    c2.execute('DELETE FROM message_store WHERE session_id = ?', (session_id,))
    conn2.commit()
    conn2.close()

class DeleteSessionHandler:
    bp = Blueprint('delete_session', __name__)

    @staticmethod
    @bp.route('/delete_session', methods=['POST'])
    def delete_session():
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No session_id provided'}), 400
        delete_session_from_db(session_id)
        return jsonify({'success': True})
