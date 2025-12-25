"""CONTROLLERS - API Endpoint'leri"""
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.author_controller import author_bp
from controllers.category_controller import category_bp
from controllers.book_controller import book_bp
from controllers.transaction_controller import transaction_bp
from controllers.penalty_controller import penalty_bp
from controllers.member_controller import member_bp
from controllers.stats_controller import stats_bp

__all__ = ['auth_bp', 'user_bp', 'author_bp', 'category_bp', 'book_bp', 'transaction_bp', 'penalty_bp', 'member_bp', 'stats_bp']
