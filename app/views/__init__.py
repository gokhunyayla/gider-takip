from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

# Import routes
from . import main_views, auth_views, api_views, category_views, user_views, profile_views, expense_views