from flask import Blueprint, jsonify

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Dashboard API is working'})
