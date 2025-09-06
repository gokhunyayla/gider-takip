from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from . import main_bp

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('pages/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from app.controllers.dashboard_controller import get_dashboard_data
    from app.models import ExpenseCategory
    
    period = request.args.get('period', 'month')
    category_id = request.args.get('category_id', type=int)
    compare = request.args.get('compare', 'none')
    
    data = get_dashboard_data(current_user.id, period, category_id, compare)
    data['selected_period'] = period
    data['selected_compare'] = compare
    
    # Get all categories for filter dropdown
    categories = ExpenseCategory.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).order_by(ExpenseCategory.name).all()
    data['categories'] = categories
    
    return render_template('pages/dashboard.html', **data)

@main_bp.route('/expenses')
@login_required
def expenses():
    from app.models import ExpenseRecord, ExpenseCategory
    from datetime import datetime
    
    # Get filter parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', None, type=int)
    category_id = request.args.get('category_id', None, type=int)
    
    # Build query
    query = ExpenseRecord.query
    
    if year:
        query = query.filter_by(year=year)
    if month:
        query = query.filter_by(month=month)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Get expenses with category info
    expenses = query.order_by(ExpenseRecord.created_at.desc()).all()
    
    # Get all categories for filter dropdown
    categories = ExpenseCategory.query.filter_by(is_active=True).order_by(ExpenseCategory.name).all()
    
    # Get current date for modal defaults
    now = datetime.now()
    
    return render_template('pages/expenses.html', 
                         expenses=expenses,
                         categories=categories,
                         current_year=year,
                         current_month=month,
                         modal_year=now.year,
                         modal_month=now.month,
                         modal_day=now.day)

@main_bp.route('/reports')
@login_required
def reports():
    return render_template('pages/reports.html')

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('pages/settings.html')