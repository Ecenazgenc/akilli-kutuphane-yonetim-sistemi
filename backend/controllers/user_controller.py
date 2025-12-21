"""
User Controller - Kullanıcı API Endpoints
"""

from flask import Blueprint, request, jsonify
from services.user_service import user_service

user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('', methods=['GET'])
def get_all():
    """Tüm kullanıcıları getir"""
    try:
        users = user_service.get_all()
        return jsonify([u.to_dict() for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_one(user_id):
    """Kullanıcı getir"""
    try:
        user = user_service.get_by_id(user_id)
        if user:
            return jsonify(user.to_dict())
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('', methods=['POST'])
def create():
    """Kullanıcı ekle"""
    try:
        data = request.get_json()
        user = user_service.create(
            data.get('fullName'),
            data.get('email'),
            data.get('password', '123456'),
            data.get('role', 'user')
        )
        if user:
            return jsonify(user.to_dict()), 201
        return jsonify({"error": "Eklenemedi"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update(user_id):
    """Kullanıcı güncelle"""
    try:
        data = request.get_json()
        if user_service.update(user_id, data.get('fullName'), data.get('email'), data.get('role')):
            user = user_service.get_by_id(user_id)
            return jsonify(user.to_dict())
        return jsonify({"error": "Güncelleme başarısız"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete(user_id):
    """Kullanıcı sil"""
    try:
        if user_service.delete(user_id):
            return jsonify({"message": "Silindi"})
        return jsonify({"error": "Silinemedi"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
