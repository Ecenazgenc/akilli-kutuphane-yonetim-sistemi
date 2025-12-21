"""
Category Controller - Kategori API Endpoints
"""

from flask import Blueprint, request, jsonify
from services.category_service import category_service

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@category_bp.route('', methods=['GET'])
def get_all():
    try:
        categories = category_service.get_all()
        return jsonify([c.to_dict() for c in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_one(category_id):
    try:
        category = category_service.get_by_id(category_id)
        if category:
            return jsonify(category.to_dict())
        return jsonify({"error": "Kategori bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        category = category_service.create(data.get('name'))
        if category:
            return jsonify(category.to_dict()), 201
        return jsonify({"error": "Eklenemedi"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route('/<int:category_id>', methods=['PUT'])
def update(category_id):
    try:
        data = request.get_json()
        if category_service.update(category_id, data.get('name')):
            category = category_service.get_by_id(category_id)
            return jsonify(category.to_dict())
        return jsonify({"error": "Güncelleme başarısız"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete(category_id):
    try:
        if category_service.delete(category_id):
            return jsonify({"message": "Silindi"})
        return jsonify({"error": "Silinemedi"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
