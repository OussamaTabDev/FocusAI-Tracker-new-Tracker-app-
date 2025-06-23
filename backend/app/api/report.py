from flask import Blueprint, jsonify

bp = Blueprint('report', __name__)

@bp.route('/report/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Report API is working'})
