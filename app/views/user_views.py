from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User
from . import main_bp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(company_id=current_user.company_id).all()
    return render_template('pages/users.html', users=users)

@main_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    is_admin = request.form.get('is_admin') == 'on'
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
        return redirect(url_for('main.users'))
    
    if User.query.filter_by(email=email).first():
        flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
        return redirect(url_for('main.users'))
    
    # Create new user
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        is_admin=is_admin,
        company_id=current_user.company_id
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash(f'"{username}" kullanıcısı başarıyla eklendi.', 'success')
    return redirect(url_for('main.users'))

@main_bp.route('/users/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    user = User.query.filter_by(id=id, company_id=current_user.company_id).first_or_404()
    
    if user.id == current_user.id:
        flash('Kendi hesabınızı devre dışı bırakamazsınız.', 'danger')
        return redirect(url_for('main.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'aktif' if user.is_active else 'pasif'
    flash(f'"{user.username}" kullanıcısı {status} duruma getirildi.', 'success')
    return redirect(url_for('main.users'))

@main_bp.route('/users/<int:id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(id):
    user = User.query.filter_by(id=id, company_id=current_user.company_id).first_or_404()
    new_password = request.form.get('new_password')
    
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'"{user.username}" kullanıcısının şifresi değiştirildi.', 'success')
    return redirect(url_for('main.users'))

@main_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.filter_by(id=id, company_id=current_user.company_id).first_or_404()
    
    if user.id == current_user.id:
        flash('Kendi hesabınızı silemezsiniz.', 'danger')
        return redirect(url_for('main.users'))
    
    # Kullanıcının gider kayıtlarını kontrol et
    from app.models import ExpenseRecord
    expense_count = ExpenseRecord.query.filter_by(user_id=user.id).count()
    
    if expense_count > 0:
        flash(f'Bu kullanıcının {expense_count} adet gider kaydı bulunduğu için silinemez. Önce kullanıcıyı pasif yapın.', 'warning')
        return redirect(url_for('main.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'"{username}" kullanıcısı başarıyla silindi.', 'success')
    return redirect(url_for('main.users'))