from flask import Blueprint, request, jsonify
import uuid
from .shared import add_session

class NewSessionHandler:
    bp = Blueprint('new_session', __name__)

    @staticmethod
    @bp.route('/new_session', methods=['POST'])
    def new_session():
        data = request.get_json(silent=True) or {}
        session_name = data.get('session_name')
        if session_name and session_name.strip():
            session_id = session_name.strip()
        else:
            session_id = str(uuid.uuid4())
        add_session(session_id)
        return jsonify({'session_id': session_id})
