from flask import Blueprint, jsonify

bp = Blueprint('activity', __name__)

@bp.route('/activity/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Activity API is working'})
