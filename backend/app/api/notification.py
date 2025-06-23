from flask import Blueprint, jsonify

bp = Blueprint('notification', __name__)

@bp.route('/notification/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Notification API is working'})
