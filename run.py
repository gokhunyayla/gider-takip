import os
from app import create_app, db
from app.models import User, Company, ExpenseCategory

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    db.create_all()
    
    # Create default data if not exists
    if Company.query.count() == 0:
        company = Company(name='Demo Şirket', tax_number='1234567890')
        db.session.add(company)
        db.session.commit()
        
        # Create expense categories
        categories = [
            'KIRTASİYE/AVANSAS', 'TÜRK TELEKOM', 'İNTERNETLER', 'AYEDAŞ',
            'MOTORLU TAŞITLAR VERGİSİ', 'DHL', 'KARGO', 'BANKA MASRAFLARI',
            'BİLGİSAYAR BAKIM/ALIM', 'MATBAA', 'AJANS', 'ARAÇ HGS',
            'ARAÇ BAKIM ONARIM', 'ARAÇ TRAFİK CEZALARI', 'FUAR', 'UÇAK BİLETİ',
            'OFİS ETKİNLİK', 'ÇİÇEK SEPETİ', 'ÇEVRE TEMİZLİK', 'VODAFONE',
            'TERCÜME', 'AİDAT', 'YAKIT', 'YEMEK KARTI', 'MUTFAK', 'DİĞER GİDERLER',
            'KİRA', 'OFİS TADİLAT', 'PERSONEL MAAŞ', 'PERSONEL PRİM',
            'PERSONEL TAZMİNATLAR', 'YOL', 'SGK'
        ]
        
        for cat_name in categories:
            cat = ExpenseCategory(name=cat_name, company_id=company.id)
            db.session.add(cat)
        
        db.session.commit()
        
        # Create demo user
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='Admin User',
                is_admin=True,
                company_id=company.id
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    app.run(
        host=app.config['APP_HOST'],
        port=app.config['APP_PORT'],
        debug=app.config['DEBUG']
    )