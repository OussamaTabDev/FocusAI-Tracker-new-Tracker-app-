from flask import Blueprint, jsonify

bp = Blueprint('kids_mode', __name__)

@bp.route('/kids_mode/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Kids Mode API is working'})
