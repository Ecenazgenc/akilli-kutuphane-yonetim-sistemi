"""AUTHOR_CONTROLLER.PY - Yazar API"""
from flask import Blueprint, request, jsonify
from services.author_service import author_service

author_bp = Blueprint('authors', __name__, url_prefix='/api/authors')

@author_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([a.to_dict() for a in author_service.get_all()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@author_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        author = author_service.get_by_id(id)
        return jsonify(author.to_dict()) if author else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@author_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        author = author_service.create(data.get('name'), data.get('lastName'), data.get('country'))
        return (jsonify(author.to_dict()), 201) if author else (jsonify({"error": "Oluşturulamadı"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@author_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    try:
        data = request.get_json()
        return jsonify({"message": "Güncellendi"}) if author_service.update(id, data.get('name'), data.get('lastName'), data.get('country')) else (jsonify({"error": "Güncellenemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@author_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if author_service.delete(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
