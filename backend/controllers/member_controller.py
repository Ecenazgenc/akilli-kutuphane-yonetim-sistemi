"""
Member Controller - Üye Kendi İşlemleri API Endpoints
"""

from flask import Blueprint, request, jsonify
from services.auth_service import auth_service
from services.borrow_service import borrow_service
from services.penalty_service import penalty_service
from services.stats_service import stats_service

member_bp = Blueprint('member', __name__, url_prefix='/api')


def get_current_user():
    """Token'dan aktif kullanıcıyı getirir"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    return auth_service.get_user_from_token(token)


@member_bp.route('/borrow', methods=['POST'])
def borrow_book():
    """Kitap ödünç al"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        data = request.get_json()
        book_id = data.get('bookId')
        
        print(f"[MemberController.borrow_book] User {user.Id} kitap {book_id} ödünç alıyor")
        
        success, message, tx = borrow_service.borrow_book(user.Id, book_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "transaction": tx.to_dict() if tx else None
            }), 201
        
        return jsonify({"error": message}), 400
        
    except Exception as e:
        print(f"[MemberController.borrow_book] HATA: {e}")
        return jsonify({"error": str(e)}), 500


@member_bp.route('/my/transactions', methods=['GET'])
def get_my_transactions():
    """Kendi işlemlerimi getir"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        transactions = borrow_service.get_user_transactions(user.Id)
        return jsonify([t.to_dict() for t in transactions])
        
    except Exception as e:
        print(f"[MemberController.get_my_transactions] HATA: {e}")
        return jsonify({"error": str(e)}), 500


@member_bp.route('/my/penalties', methods=['GET'])
def get_my_penalties():
    """Kendi cezalarımı getir"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        print(f"[MemberController.get_my_penalties] User {user.Id} cezalarını istiyor")
        
        penalties = penalty_service.get_user_penalties(user.Id)
        
        print(f"[MemberController.get_my_penalties] {len(penalties)} ceza bulundu")
        
        result = []
        for p in penalties:
            result.append(p.to_dict())
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[MemberController.get_my_penalties] HATA: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@member_bp.route('/my/stats', methods=['GET'])
def get_my_stats():
    """Kendi istatistiklerimi getir"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        print(f"[MemberController.get_my_stats] User {user.Id} istatistik istiyor")
        
        stats = stats_service.get_user_stats(user.Id)
        
        print(f"[MemberController.get_my_stats] Stats: {stats}")
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"[MemberController.get_my_stats] HATA: {e}")
        return jsonify({"error": str(e)}), 500


@member_bp.route('/my/transactions/<int:tx_id>/return', methods=['POST'])
def return_my_book(tx_id):
    """Kitabımı iade et"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        print(f"[MemberController.return_my_book] User {user.Id} işlem {tx_id} iade ediyor")
        
        success, message, tx = borrow_service.return_book(tx_id, user.Id)
        
        print(f"[MemberController.return_my_book] Sonuç: success={success}, message={message}")
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "transaction": tx.to_dict() if tx else None
            })
        
        return jsonify({"error": message}), 400
        
    except Exception as e:
        print(f"[MemberController.return_my_book] HATA: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@member_bp.route('/my/penalties/<int:penalty_id>/pay', methods=['POST'])
def pay_my_penalty(penalty_id):
    """Cezamı öde"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Oturum gerekli"}), 401
        
        print(f"[MemberController.pay_my_penalty] User {user.Id} ceza {penalty_id} ödüyor")
        
        success, message = penalty_service.pay_penalty(penalty_id, user.Id)
        
        print(f"[MemberController.pay_my_penalty] Sonuç: success={success}, message={message}")
        
        if success:
            return jsonify({
                "success": True,
                "message": message
            })
        
        return jsonify({"error": message}), 400
        
    except Exception as e:
        print(f"[MemberController.pay_my_penalty] HATA: {e}")
        return jsonify({"error": str(e)}), 500
