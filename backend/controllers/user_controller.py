"""USER_CONTROLLER.PY - Kullanıcı API"""
from flask import Blueprint, request, jsonify
from services.user_service import user_service

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([u.to_dict() for u in user_service.get_all()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        user = user_service.get_by_id(id)
        return jsonify(user.to_dict()) if user else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        user = user_service.create(data.get('fullName'), data.get('email'), data.get('password'), data.get('role', 'user'))
        return (jsonify(user.to_dict()), 201) if user else (jsonify({"error": "Oluşturulamadı"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    try:
        data = request.get_json()
        return jsonify({"message": "Güncellendi"}) if user_service.update(id, data.get('fullName'), data.get('email'), data.get('role')) else (jsonify({"error": "Güncellenemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if user_service.delete(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
