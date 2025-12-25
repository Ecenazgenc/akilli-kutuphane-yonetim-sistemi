"""
MEMBER_CONTROLLER.PY - Üye İşlemleri API

Stored Procedure Kullanır:
- /api/borrow -> sp_BorrowBook
- /api/my/transactions/{id}/return -> sp_ReturnBook (+ Trigger ile ceza)
- /api/my/penalties/{id}/pay -> sp_PayPenalty
"""
from flask import Blueprint, request, jsonify
from services.auth_service import auth_service
from services.borrow_service import borrow_service
from services.penalty_service import penalty_service
from services.stats_service import stats_service

member_bp = Blueprint('member', __name__, url_prefix='/api')

def get_current_user():
    """Token'dan kullanıcıyı al"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return auth_service.get_user_from_token(token)

@member_bp.route('/borrow', methods=['POST'])
def borrow_book():
    """Kitap ödünç al - sp_BorrowBook STORED PROCEDURE kullanır"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        data = request.get_json()
        success, message, tx = borrow_service.borrow_book(user.Id, data.get('bookId'))
        
        if success:
            return jsonify({"success": True, "message": message, "transaction": tx.to_dict() if tx else None}), 201
        return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/my/transactions', methods=['GET'])
def get_my_transactions():
    """Kendi işlemlerimi listele"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        return jsonify([t.to_dict() for t in borrow_service.get_user_transactions(user.Id)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/my/penalties', methods=['GET'])
def get_my_penalties():
    """Kendi cezalarımı listele"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        return jsonify([p.to_dict() for p in penalty_service.get_user_penalties(user.Id)])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/my/stats', methods=['GET'])
def get_my_stats():
    """Kendi istatistiklerimi getir"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        return jsonify(stats_service.get_user_stats(user.Id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/my/transactions/<int:tx_id>/return', methods=['POST'])
def return_my_book(tx_id):
    """Kitap iade et - sp_ReturnBook + trg_CalculatePenalty"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        success, message, tx = borrow_service.return_book(tx_id, user.Id)
        
        if success:
            return jsonify({"success": True, "message": message, "transaction": tx.to_dict() if tx else None})
        return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/my/penalties/<int:penalty_id>/pay', methods=['POST'])
def pay_my_penalty(penalty_id):
    """Ceza öde - sp_PayPenalty STORED PROCEDURE kullanır"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        success, message = penalty_service.pay_penalty(penalty_id, user.Id)
        
        if success:
            return jsonify({"success": True, "message": message})
        return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
