"""TRANSACTION_CONTROLLER.PY - İşlem API (Admin)"""
from flask import Blueprint, jsonify
from services.borrow_service import borrow_service

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transaction_bp.route('', methods=['GET'])
def get_all():
    try:
        return jsonify([t.to_dict() for t in borrow_service.get_all_transactions()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    try:
        tx = borrow_service.get_transaction_by_id(id)
        return jsonify(tx.to_dict()) if tx else (jsonify({"error": "Bulunamadı"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return jsonify({"message": "Silindi"}) if borrow_service.delete_transaction(id) else (jsonify({"error": "Silinemedi"}), 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
