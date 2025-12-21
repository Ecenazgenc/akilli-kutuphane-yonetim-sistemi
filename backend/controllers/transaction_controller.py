"""
Transaction Controller - İşlem API Endpoints (Admin)
"""

from flask import Blueprint, request, jsonify
from services.borrow_service import borrow_service

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')


@transaction_bp.route('', methods=['GET'])
def get_all():
    """Tüm işlemleri getir"""
    try:
        transactions = borrow_service.get_all_transactions()
        return jsonify([t.to_dict() for t in transactions])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@transaction_bp.route('', methods=['POST'])
def create():
    """Yeni işlem oluştur (Admin)"""
    try:
        data = request.get_json()
        success, message, tx = borrow_service.create_transaction_admin(
            data.get('bookId'),
            data.get('userId')
        )
        if success:
            return jsonify(tx.to_dict()), 201
        return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@transaction_bp.route('/<int:tx_id>', methods=['DELETE'])
def delete(tx_id):
    """İşlem sil"""
    try:
        if borrow_service.delete_transaction(tx_id):
            return jsonify({"message": "Silindi"})
        return jsonify({"error": "Silinemedi"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
