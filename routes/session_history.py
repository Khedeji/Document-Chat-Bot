from flask import Blueprint, request, jsonify
from .shared import SQLChatMessageHistory

class SessionHistoryHandler:
    bp = Blueprint('session_history', __name__)

    @staticmethod
    @bp.route('/session_history', methods=['GET'])
    def session_history():
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'history': []})
        try:
            chat_history = SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")
            history = []
            for msg in chat_history.messages:
                sender = 'user' if msg.type == 'human' else 'bot'
                history.append({'sender': sender, 'text': msg.content})
            return jsonify({'history': history})
        except Exception as e:
            return jsonify({'history': [], 'error': str(e)})
