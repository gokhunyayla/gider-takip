from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from app.models import ExpenseCategory, ExpenseRecord, Company
from app import db
from datetime import datetime

@api_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    query = ExpenseRecord.query.filter_by(user_id=user_id)
    
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
    
    expenses = query.all()
    return jsonify([e.to_dict() for e in expenses])

@api_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    expense = ExpenseRecord(
        category_id=data['category_id'],
        company_id=data['company_id'],
        amount=data['amount'],
        month=data['month'],
        year=data['year'],
        description=data.get('description'),
        invoice_number=data.get('invoice_number'),
        user_id=user_id
    )
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify(expense.to_dict()), 201

@api_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = ExpenseCategory.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in categories])

@api_bp.route('/reports/summary', methods=['GET'])
@jwt_required()
def get_summary():
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get monthly expenses by category
    result = db.session.execute(
        """SELECT ec.name, er.month, SUM(er.amount) as total
        FROM expense_records er
        JOIN expense_categories ec ON er.category_id = ec.id
        WHERE er.year = :year
        GROUP BY ec.id, er.month
        ORDER BY ec.name, er.month""",
        {'year': year}
    )
    
    summary = {}
    for row in result:
        category_name = row[0]
        month = row[1]
        total = float(row[2])
        
        if category_name not in summary:
            summary[category_name] = {str(i): 0 for i in range(1, 13)}
        
        summary[category_name][str(month)] = total
    
    return jsonify(summary)