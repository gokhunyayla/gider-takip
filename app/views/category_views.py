from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import ExpenseCategory
from . import main_bp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/categories')
@login_required
def categories():
    categories = ExpenseCategory.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).order_by(ExpenseCategory.name).all()
    return render_template('pages/categories.html', categories=categories)

@main_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Kategori adı gereklidir.', 'danger')
        return redirect(url_for('main.categories'))
    
    # Aynı isimde kategori var mı kontrol et
    existing = ExpenseCategory.query.filter_by(
        name=name,
        company_id=current_user.company_id
    ).first()
    
    if existing:
        flash('Bu isimde bir kategori zaten mevcut.', 'warning')
        return redirect(url_for('main.categories'))
    
    category = ExpenseCategory(
        name=name,
        description=description,
        company_id=current_user.company_id
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash(f'"{name}" kategorisi başarıyla eklendi.', 'success')
    return redirect(url_for('main.categories'))

@main_bp.route('/categories/<int:id>/edit', methods=['POST'])
@login_required
def edit_category(id):
    category = ExpenseCategory.query.filter_by(
        id=id,
        company_id=current_user.company_id
    ).first_or_404()
    
    category.name = request.form.get('name', category.name)
    category.description = request.form.get('description', category.description)
    
    db.session.commit()
    
    flash(f'"{category.name}" kategorisi güncellendi.', 'success')
    return redirect(url_for('main.categories'))

@main_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = ExpenseCategory.query.filter_by(
        id=id,
        company_id=current_user.company_id
    ).first_or_404()
    
    # Kategoriyi silmek yerine pasif yap
    category.is_active = False
    db.session.commit()
    
    flash(f'"{category.name}" kategorisi silindi.', 'info')
    return redirect(url_for('main.categories'))

# API endpoint for getting categories
@main_bp.route('/categories/api/categories')
@login_required
def api_categories():
    categories = ExpenseCategory.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).order_by(ExpenseCategory.name).all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description
    } for cat in categories])