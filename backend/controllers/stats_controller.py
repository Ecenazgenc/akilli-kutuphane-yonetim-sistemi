"""STATS_CONTROLLER.PY - İstatistik API"""
from flask import Blueprint, jsonify
from services.stats_service import stats_service
from config import DatabaseConfig

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        return jsonify(stats_service.get_admin_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_bp.route('/health', methods=['GET'])
def health_check():
    try:
        success, message = DatabaseConfig.test_connection()
        if success:
            return jsonify({"status": "healthy", "database": "connected"})
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": message}), 500
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
