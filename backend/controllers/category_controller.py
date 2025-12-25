"""CATEGORY_CONTROLLER.PY - Kategori API"""
from flask import Blueprint, request, jsonify
from services.category_service import category_service

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@category_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([c.to_dict() for c in category_service.get_all()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@category_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        cat = category_service.get_by_id(id)
        return jsonify(cat.to_dict()) if cat else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@category_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        cat = category_service.create(data.get('name'))
        return (jsonify(cat.to_dict()), 201) if cat else (jsonify({"error": "Oluşturulamadı"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@category_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    try:
        data = request.get_json()
        return jsonify({"message": "Güncellendi"}) if category_service.update(id, data.get('name')) else (jsonify({"error": "Güncellenemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@category_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if category_service.delete(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
