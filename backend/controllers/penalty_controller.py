"""
Penalty Controller - Ceza API Endpoints (Admin)
"""

from flask import Blueprint, jsonify
from services.penalty_service import penalty_service

penalty_bp = Blueprint('penalties', __name__, url_prefix='/api/penalties')


@penalty_bp.route('', methods=['GET'])
def get_all_penalties():
    """Tüm cezaları getir (Admin)"""
    try:
        print("[PenaltyController.get_all_penalties] İstek alındı")
        
        penalties = penalty_service.get_all_penalties()
        
        print(f"[PenaltyController.get_all_penalties] {len(penalties)} ceza döndürülüyor")
        
        result = []
        for p in penalties:
            result.append(p.to_dict())
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[PenaltyController.get_all_penalties] HATA: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@penalty_bp.route('/<int:penalty_id>', methods=['GET'])
def get_penalty(penalty_id):
    """Tek ceza getir"""
    try:
        penalty = penalty_service.get_penalty_by_id(penalty_id)
        if penalty:
            return jsonify(penalty.to_dict())
        return jsonify({"error": "Ceza bulunamadı"}), 404
    except Exception as e:
        print(f"[PenaltyController.get_penalty] HATA: {e}")
        return jsonify({"error": str(e)}), 500


@penalty_bp.route('/<int:penalty_id>', methods=['DELETE'])
def delete_penalty(penalty_id):
    """Ceza sil (Admin)"""
    try:
        if penalty_service.delete_penalty(penalty_id):
            return jsonify({"message": "Ceza silindi"})
        return jsonify({"error": "Ceza silinemedi"}), 400
    except Exception as e:
        print(f"[PenaltyController.delete_penalty] HATA: {e}")
        return jsonify({"error": str(e)}), 500
