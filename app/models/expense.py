from datetime import datetime
from app import db

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='expense_categories')
    expense_records = db.relationship('ExpenseRecord', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'company_id': self.company_id,
            'is_active': self.is_active
        }

class ExpenseRecord(db.Model):
    __tablename__ = 'expense_records'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    invoice_number = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    due_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)
    supplier_name = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='expense_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'company_id': self.company_id,
            'amount': float(self.amount),
            'month': self.month,
            'year': self.year,
            'description': self.description,
            'invoice_number': self.invoice_number,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }