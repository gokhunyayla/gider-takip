from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User
from . import main_bp

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('pages/profile.html')

@main_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    
    user.full_name = request.form.get('full_name')
    user.email = request.form.get('email')
    
    # Check if email is already taken by another user
    existing_user = User.query.filter_by(email=user.email).first()
    if existing_user and existing_user.id != user.id:
        flash('Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.', 'danger')
        return redirect(url_for('main.profile'))
    
    db.session.commit()
    flash('Profil bilgileriniz güncellendi.', 'success')
    return redirect(url_for('main.profile'))

@main_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get(current_user.id)
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Verify current password
    if not user.check_password(current_password):
        flash('Mevcut şifreniz hatalı.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Check password length
    if len(new_password) < 6:
        flash('Yeni şifre en az 6 karakter olmalıdır.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Update password
    user.set_password(new_password)
    db.session.commit()
    
    flash('Şifreniz başarıyla değiştirildi.', 'success')
    return redirect(url_for('main.profile'))