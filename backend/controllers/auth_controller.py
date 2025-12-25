"""AUTH_CONTROLLER.PY - Kimlik Doğrulama API"""
from flask import Blueprint, request, jsonify
from services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        success, result, user = auth_service.login(data.get('email'), data.get('password'))
        if success:
            return jsonify({"success": True, "token": result, "user": user.to_dict()})
        return jsonify({"error": result}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        success, message, user = auth_service.register(data.get('fullName'), data.get('email'), data.get('password'))
        if success:
            return jsonify({"success": True, "message": message, "user": user.to_dict()}), 201
        return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        auth_service.logout(token)
        return jsonify({"success": True, "message": "Çıkış yapıldı"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
