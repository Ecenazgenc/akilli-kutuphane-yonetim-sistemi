"""
Author Controller - Yazar API Endpoints
"""

from flask import Blueprint, request, jsonify
from services.author_service import author_service

author_bp = Blueprint('authors', __name__, url_prefix='/api/authors')


@author_bp.route('', methods=['GET'])
def get_all():
    try:
        authors = author_service.get_all()
        return jsonify([a.to_dict() for a in authors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@author_bp.route('/<int:author_id>', methods=['GET'])
def get_one(author_id):
    try:
        author = author_service.get_by_id(author_id)
        if author:
            return jsonify(author.to_dict())
        return jsonify({"error": "Yazar bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@author_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        author = author_service.create(data.get('name'), data.get('lastName'), data.get('country', ''))
        if author:
            return jsonify(author.to_dict()), 201
        return jsonify({"error": "Eklenemedi"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@author_bp.route('/<int:author_id>', methods=['PUT'])
def update(author_id):
    try:
        data = request.get_json()
        if author_service.update(author_id, data.get('name'), data.get('lastName'), data.get('country', '')):
            author = author_service.get_by_id(author_id)
            return jsonify(author.to_dict())
        return jsonify({"error": "Güncelleme başarısız"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@author_bp.route('/<int:author_id>', methods=['DELETE'])
def delete(author_id):
    try:
        if author_service.delete(author_id):
            return jsonify({"message": "Silindi"})
        return jsonify({"error": "Silinemedi"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
