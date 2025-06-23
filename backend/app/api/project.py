from flask import Blueprint, jsonify

bp = Blueprint('project', __name__)

@bp.route('/project/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Project API is working'})
