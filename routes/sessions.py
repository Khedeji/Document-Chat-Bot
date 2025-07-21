from flask import Blueprint, jsonify
from .shared import get_all_sessions

class SessionsHandler:
    bp = Blueprint('sessions', __name__)

    @staticmethod
    @bp.route('/sessions', methods=['GET'])
    def list_sessions():
        sessions = get_all_sessions()
        return jsonify({'sessions': sessions})
