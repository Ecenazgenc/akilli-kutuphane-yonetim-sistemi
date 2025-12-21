from flask import Blueprint, request, jsonify
from datetime import datetime
from services.book_service import book_service

book_bp = Blueprint('books', __name__, url_prefix='/api/books')


@book_bp.route('', methods=['GET'])
def get_all():
    try:
        books = book_service.get_all()
        return jsonify([b.to_dict() for b in books])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_one(book_id):
    try:
        book = book_service.get_by_id(book_id)
        if book:
            return jsonify(book.to_dict())
        return jsonify({"error": "Kitap bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@book_bp.route('', methods=['POST'])
def create():
    try:
        data = request.get_json()
        book = book_service.create(
            data.get('title'),
            data.get('authorId'),
            data.get('categoryId'),
            data.get('stockNumber', 1),
            data.get('yearOfPublication', datetime.now().year)
        )
        if book:
            return jsonify(book.to_dict()), 201
        return jsonify({"error": "Eklenemedi"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@book_bp.route('/<int:book_id>', methods=['PUT'])
def update(book_id):
    try:
        data = request.get_json()
        if book_service.update(
            book_id,
            data.get('title'),
            data.get('authorId'),
            data.get('categoryId'),
            data.get('stockNumber'),
            data.get('yearOfPublication')
        ):
            book = book_service.get_by_id(book_id)
            return jsonify(book.to_dict())
        return jsonify({"error": "Güncelleme başarısız"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete(book_id):
    try:
        if book_service.delete(book_id):
            return jsonify({"message": "Silindi"})
        return jsonify({"error": "Silinemedi"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
