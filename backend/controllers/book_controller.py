"""BOOK_CONTROLLER.PY - Kitap API"""
from flask import Blueprint, request, jsonify
from services.book_service import book_service

book_bp = Blueprint('books', __name__, url_prefix='/api/books')

@book_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([b.to_dict() for b in book_service.get_all()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        book = book_service.get_by_id(id)
        return jsonify(book.to_dict()) if book else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        book = book_service.create(data.get('title'), data.get('authorId'), data.get('categoryId'), data.get('stockNumber'), data.get('yearOfPublication'))
        return (jsonify(book.to_dict()), 201) if book else (jsonify({"error": "Oluşturulamadı"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    try:
        data = request.get_json()
        return jsonify({"message": "Güncellendi"}) if book_service.update(id, data.get('title'), data.get('authorId'), data.get('categoryId'), data.get('stockNumber'), data.get('yearOfPublication')) else (jsonify({"error": "Güncellenemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if book_service.delete(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
