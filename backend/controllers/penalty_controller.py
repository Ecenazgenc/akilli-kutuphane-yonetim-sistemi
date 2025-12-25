"""PENALTY_CONTROLLER.PY - Ceza API (Admin)"""
from flask import Blueprint, jsonify
from services.penalty_service import penalty_service

penalty_bp = Blueprint('penalties', __name__, url_prefix='/api/penalties')

@penalty_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([p.to_dict() for p in penalty_service.get_all_penalties()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@penalty_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        p = penalty_service.get_penalty_by_id(id)
        return jsonify(p.to_dict()) if p else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@penalty_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if penalty_service.delete_penalty(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
