from datetime import datetime, timedelta, date
from sqlalchemy import func, and_
from app import db
from app.models import ExpenseRecord, ExpenseCategory

def get_dashboard_data(user_id, period='month', category_id=None, compare_mode='none'):
    """Dashboard verilerini period'a göre getir - basit ve anlaşılır"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    today = datetime.now().date()
    
    # Period'a göre tarih aralığı belirle
    if period == 'today':
        start_date = today
        end_date = today
        period_label = "Bugün"
    elif period == 'week':
        # Haftanın başı (Pazartesi)
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        period_label = "Bu Hafta"
    elif period == 'year':
        start_date = date(current_year, 1, 1)
        end_date = today
        period_label = "Bu Yıl"
    elif period == 'lastmonth':
        # Geçen ay
        if current_month == 1:
            start_date = date(current_year - 1, 12, 1)
            end_date = date(current_year - 1, 12, 31)
        else:
            start_date = date(current_year, current_month - 1, 1)
            # Geçen ayın son günü
            if current_month - 1 == 2:  # Şubat
                if current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0):
                    end_date = date(current_year, 2, 29)
                else:
                    end_date = date(current_year, 2, 28)
            elif current_month - 1 in [4, 6, 9, 11]:  # 30 günlük aylar
                end_date = date(current_year, current_month - 1, 30)
            else:  # 31 günlük aylar
                end_date = date(current_year, current_month - 1, 31)
        period_label = "Geçen Ay"
    else:  # month (default)
        start_date = date(current_year, current_month, 1)
        # Ayın son günü
        if current_month == 12:
            end_date = date(current_year, 12, 31)
        else:
            end_date = date(current_year, current_month + 1, 1) - timedelta(days=1)
        period_label = "Bu Ay"
    
    # Date filter - giderin ait olduğu ay/yıl'a göre
    if period == 'today':
        # Bugün için created_at kullan
        date_filter = and_(
            func.date(ExpenseRecord.created_at) >= start_date,
            func.date(ExpenseRecord.created_at) <= end_date
        )
    elif period == 'week':
        # Hafta için created_at kullan
        date_filter = and_(
            func.date(ExpenseRecord.created_at) >= start_date,
            func.date(ExpenseRecord.created_at) <= end_date
        )
    elif period == 'year':
        # Yıl için year alanı kullan
        date_filter = ExpenseRecord.year == current_year
    elif period == 'lastmonth':
        # Geçen ay için year ve month alanları kullan
        if current_month == 1:
            date_filter = and_(
                ExpenseRecord.year == current_year - 1,
                ExpenseRecord.month == 12
            )
        else:
            date_filter = and_(
                ExpenseRecord.year == current_year,
                ExpenseRecord.month == current_month - 1
            )
    else:  # month
        # Ay için year ve month alanları kullan
        date_filter = and_(
            ExpenseRecord.year == current_year,
            ExpenseRecord.month == current_month
        )
    
    # Kategori filtresi ekle
    if category_id:
        category_filter = ExpenseRecord.category_id == category_id
    else:
        category_filter = True  # Tüm kategoriler
    
    # Period toplam gideri
    period_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
        date_filter,
        category_filter
    ).scalar() or 0
    
    # Yıllık toplam (her zaman tüm yıl)
    yearly_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
        ExpenseRecord.year == current_year,
        category_filter
    ).scalar() or 0
    
    # Tüm giderler ödenmiş kabul edildiği için bu değerler 0
    unpaid_expenses = 0
    overdue_expenses = 0
    upcoming_payments = 0
    
    # Karşılaştırma için önceki period
    if period == 'today':
        compare_start = start_date - timedelta(days=1)
        compare_end = start_date - timedelta(days=1)
    elif period == 'week':
        compare_start = start_date - timedelta(days=7)
        compare_end = end_date - timedelta(days=7)
    elif period == 'year':
        compare_start = date(current_year-1, 1, 1)
        compare_end = date(current_year-1, today.month, today.day)
    elif period == 'lastmonth':
        # Geçen ayın önceki ayı
        if current_month == 1:  # Ocak ise, geçen ay Aralık, onun öncesi Kasım
            compare_start = date(current_year-1, 11, 1)
            compare_end = date(current_year-1, 11, 30)
        elif current_month == 2:  # Şubat ise, geçen ay Ocak, onun öncesi Aralık
            compare_start = date(current_year-1, 12, 1)
            compare_end = date(current_year-1, 12, 31)
        else:
            compare_start = date(current_year, current_month-2, 1)
            if current_month-2 == 2:  # Şubat
                compare_end = date(current_year, current_month-2, 28)
            elif current_month-2 in [4, 6, 9, 11]:  # 30 gün
                compare_end = date(current_year, current_month-2, 30)
            else:  # 31 gün
                compare_end = date(current_year, current_month-2, 31)
    else:  # month
        if current_month == 1:
            compare_start = date(current_year-1, 12, 1)
            compare_end = date(current_year-1, 12, 31)
        else:
            compare_start = date(current_year, current_month-1, 1)
            if current_month-1 == 2:  # Şubat
                compare_end = date(current_year, current_month-1, 28)
            elif current_month-1 in [4, 6, 9, 11]:  # 30 gün
                compare_end = date(current_year, current_month-1, 30)
            else:  # 31 gün
                compare_end = date(current_year, current_month-1, 31)
    
    # Karşılaştırma dönemi toplamı
    if period == 'month':
        # Önceki ay için year/month kullan
        if current_month == 1:
            comparison_filter = and_(
                ExpenseRecord.year == current_year - 1,
                ExpenseRecord.month == 12
            )
        else:
            comparison_filter = and_(
                ExpenseRecord.year == current_year,
                ExpenseRecord.month == current_month - 1
            )
        comparison_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
            comparison_filter,
            category_filter
        ).scalar() or 0
    elif period == 'lastmonth':
        # Geçen ayın önceki ayı için year/month kullan
        if current_month == 1:  # Ocak ise, geçen ayın öncesi Kasım
            comparison_filter = and_(
                ExpenseRecord.year == current_year - 1,
                ExpenseRecord.month == 11
            )
        elif current_month == 2:  # Şubat ise, geçen ayın öncesi Aralık
            comparison_filter = and_(
                ExpenseRecord.year == current_year - 1,
                ExpenseRecord.month == 12
            )
        else:
            comparison_filter = and_(
                ExpenseRecord.year == current_year,
                ExpenseRecord.month == current_month - 2
            )
        comparison_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
            comparison_filter,
            category_filter
        ).scalar() or 0
    elif period == 'year':
        # Önceki yıl
        comparison_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
            ExpenseRecord.year == current_year - 1,
            category_filter
        ).scalar() or 0
    else:
        # Diğer durumlar için created_at kullan
        comparison_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
            and_(
                func.date(ExpenseRecord.created_at) >= compare_start,
                func.date(ExpenseRecord.created_at) <= compare_end
            ),
            category_filter
        ).scalar() or 0
    
    # Değişim yüzdesi
    period_change = ((period_total - comparison_total) / comparison_total * 100) if comparison_total > 0 else 0
    
    # Trend grafiği verisi
    if period == 'today':
        trend_data = [float(period_total)]
        trend_labels = ['Bugün']
    elif period == 'week':
        # Haftalık - günlere göre
        trend_data = []
        trend_labels = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        
        for i in range(7):
            day = start_date + timedelta(days=i)
            if day <= today:
                daily_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
                    func.date(ExpenseRecord.created_at) == day,
                    category_filter
                ).scalar() or 0
                trend_data.append(float(daily_total))
            else:
                trend_data.append(0)
    elif period == 'year':
        # Yıllık - aylara göre
        trend_labels = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
        trend_data = []
        
        for month in range(1, 13):
            monthly_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
                ExpenseRecord.year == current_year,
                ExpenseRecord.month == month,
                category_filter
            ).scalar() or 0
            trend_data.append(float(monthly_total))
    elif period == 'lastmonth':
        # Geçen ay - günlere göre
        days_in_month = end_date.day
        trend_data = []
        trend_labels = []
        
        # Geçen ayın tüm giderlerini al
        if current_month == 1:
            monthly_expenses = ExpenseRecord.query.filter(
                ExpenseRecord.year == current_year - 1,
                ExpenseRecord.month == 12,
                category_filter
            ).all()
        else:
            monthly_expenses = ExpenseRecord.query.filter(
                ExpenseRecord.year == current_year,
                ExpenseRecord.month == current_month - 1,
                category_filter
            ).all()
        
        # Her gün için toplam hesapla
        daily_totals = {}
        for expense in monthly_expenses:
            # Eğer due_date varsa o günü kullan
            if expense.due_date and expense.due_date.month == (12 if current_month == 1 else current_month - 1):
                day_num = expense.due_date.day
            else:
                # Due date yoksa created_at tarihinin gününü kullan
                if hasattr(expense, 'created_at') and expense.created_at:
                    day_num = expense.created_at.day
                else:
                    day_num = 15  # Varsayılan
            
            if day_num not in daily_totals:
                daily_totals[day_num] = 0
            daily_totals[day_num] += float(expense.amount)
        
        # Grafik verilerini oluştur
        for day in range(1, days_in_month + 1):
            trend_labels.append(str(day))
            trend_data.append(daily_totals.get(day, 0))
    else:  # month
        # Aylık - günlere göre
        days_in_month = end_date.day
        trend_data = []
        trend_labels = []
        
        # Önce bu ayın tüm giderlerini al
        monthly_expenses = ExpenseRecord.query.filter(
            ExpenseRecord.year == current_year,
            ExpenseRecord.month == current_month,
            category_filter
        ).all()
        
        # Her gün için toplam hesapla
        daily_totals = {}
        for expense in monthly_expenses:
            # Eğer due_date varsa o günü kullan
            if expense.due_date and expense.due_date.month == current_month and expense.due_date.year == current_year:
                day_num = expense.due_date.day
            else:
                # Due date yoksa created_at tarihinin gününü kullan
                if hasattr(expense, 'created_at') and expense.created_at:
                    day_num = expense.created_at.day
                else:
                    day_num = 15  # Varsayılan
            
            if day_num not in daily_totals:
                daily_totals[day_num] = 0
            daily_totals[day_num] += float(expense.amount)
        
        # Grafik verilerini oluştur
        for day in range(1, days_in_month + 1):
            trend_labels.append(str(day))
            # Tüm günlerin verilerini göster (gelecek günler dahil)
            trend_data.append(daily_totals.get(day, 0))
    
    # Kategori dağılımı - period içinde
    category_distribution = db.session.query(
        ExpenseCategory.name,
        func.sum(ExpenseRecord.amount).label('total')
    ).join(
        ExpenseRecord, ExpenseCategory.id == ExpenseRecord.category_id
    ).filter(
        date_filter,
        category_filter
    ).group_by(ExpenseCategory.id).order_by(func.sum(ExpenseRecord.amount).desc()).limit(10).all()
    
    # Son giderler - period içinde
    recent_expenses = db.session.query(
        ExpenseRecord, ExpenseCategory
    ).join(
        ExpenseCategory, ExpenseRecord.category_id == ExpenseCategory.id
    ).filter(
        date_filter,
        category_filter
    ).order_by(ExpenseRecord.created_at.desc()).limit(10).all()
    
    # En çok harcanan kategoriler - period içinde
    top_categories = db.session.query(
        ExpenseCategory.name,
        func.sum(ExpenseRecord.amount).label('total'),
        func.count(ExpenseRecord.id).label('count')
    ).join(
        ExpenseRecord, ExpenseCategory.id == ExpenseRecord.category_id
    ).filter(
        date_filter,
        category_filter
    ).group_by(ExpenseCategory.id).order_by(func.sum(ExpenseRecord.amount).desc()).limit(5).all()
    
    # Kullanılan kategori sayısı
    used_categories = db.session.query(
        func.count(func.distinct(ExpenseRecord.category_id))
    ).filter(
        date_filter,
        category_filter
    ).scalar() or 0
    
    # Toplam kategori sayısı
    category_count = ExpenseCategory.query.filter_by(is_active=True).count()
    
    # Period kayıt sayısı
    period_record_count = ExpenseRecord.query.filter(date_filter, category_filter).count()
    
    # Karşılaştırma verilerini hesapla
    compare_data = {}
    comparison_expenses = []
    if compare_mode != 'none':
        # Karşılaştırma dönemi için tarih filtresi
        if compare_mode == 'previous':
            # Önceki dönem (zaten hesaplandı)
            compare_filter = comparison_filter if 'comparison_filter' in locals() else date_filter
            compare_label = "Önceki Dönem"
        elif compare_mode == 'lastyear':
            # Geçen yıl aynı dönem
            if period == 'month':
                compare_filter = and_(
                    ExpenseRecord.year == current_year - 1,
                    ExpenseRecord.month == current_month
                )
            elif period == 'lastmonth':
                if current_month == 1:
                    compare_filter = and_(
                        ExpenseRecord.year == current_year - 2,
                        ExpenseRecord.month == 12
                    )
                else:
                    compare_filter = and_(
                        ExpenseRecord.year == current_year - 1,
                        ExpenseRecord.month == current_month - 1
                    )
            elif period == 'year':
                compare_filter = ExpenseRecord.year == current_year - 1
            else:
                compare_filter = and_(
                    func.date(ExpenseRecord.created_at) >= date(current_year - 1, compare_start.month, compare_start.day),
                    func.date(ExpenseRecord.created_at) <= date(current_year - 1, compare_end.month, compare_end.day)
                )
            compare_label = "Geçen Yıl Aynı Dönem"
        
        # Karşılaştırma toplam
        compare_total = db.session.query(func.sum(ExpenseRecord.amount)).filter(
            compare_filter,
            category_filter
        ).scalar() or 0
        
        # Karşılaştırma trend verisi
        if period in ['month', 'lastmonth']:
            # Günlük karşılaştırma
            compare_trend_data = []
            for day in range(1, len(trend_labels) + 1):
                daily_compare = db.session.query(func.sum(ExpenseRecord.amount)).filter(
                    compare_filter,
                    func.extract('day', ExpenseRecord.due_date) == day,
                    category_filter
                ).scalar() or 0
                compare_trend_data.append(float(daily_compare))
        else:
            compare_trend_data = []
        
        # Karşılaştırma dönemi giderlerini getir
        comparison_expenses_raw = db.session.query(
            ExpenseRecord, ExpenseCategory
        ).join(
            ExpenseCategory, ExpenseRecord.category_id == ExpenseCategory.id
        ).filter(
            compare_filter,
            category_filter
        ).order_by(ExpenseRecord.amount.desc()).all()
        
        # Mevcut dönem giderlerini kategori bazında grupla
        current_expenses_by_category = {}
        for expense in db.session.query(
            ExpenseCategory.name,
            func.sum(ExpenseRecord.amount).label('total')
        ).join(
            ExpenseRecord, ExpenseCategory.id == ExpenseRecord.category_id
        ).filter(
            date_filter,
            category_filter
        ).group_by(ExpenseCategory.id).all():
            current_expenses_by_category[expense.name] = float(expense.total)
        
        # Karşılaştırma dönemi giderlerini kategori bazında grupla ve farkları hesapla
        comparison_expenses_by_category = {}
        for expense in db.session.query(
            ExpenseCategory.name,
            func.sum(ExpenseRecord.amount).label('total')
        ).join(
            ExpenseRecord, ExpenseCategory.id == ExpenseRecord.category_id
        ).filter(
            compare_filter,
            category_filter
        ).group_by(ExpenseCategory.id).all():
            category_name = expense.name
            compare_amount = float(expense.total)
            current_amount = current_expenses_by_category.get(category_name, 0)
            
            if compare_amount > 0:
                change_percent = ((current_amount - compare_amount) / compare_amount * 100)
            else:
                change_percent = 100 if current_amount > 0 else 0
                
            comparison_expenses_by_category[category_name] = {
                'compare_amount': compare_amount,
                'current_amount': current_amount,
                'change_percent': change_percent
            }
        
        # Detaylı gider listesini hazırla
        for e in comparison_expenses_raw[:20]:  # İlk 20 kayıt
            comparison_expenses.append({
                'date': e.ExpenseRecord.created_at.strftime('%d.%m.%Y'),
                'category': e.ExpenseCategory.name,
                'description': e.ExpenseRecord.description,
                'amount': float(e.ExpenseRecord.amount),
                'supplier': e.ExpenseRecord.supplier_name or '-',
                'invoice': e.ExpenseRecord.invoice_number or '-'
            })
        
        compare_data = {
            'compare_total': float(compare_total),
            'compare_label': compare_label,
            'compare_trend_data': compare_trend_data,
            'compare_change': ((period_total - compare_total) / compare_total * 100) if compare_total > 0 else 0,
            'comparison_expenses': comparison_expenses,
            'comparison_by_category': comparison_expenses_by_category
        }
    
    result = {
        'period_total': float(period_total),
        'period_label': period_label,
        'yearly_total': float(yearly_total),
        'category_count': category_count,
        'used_categories': used_categories,
        'period_record_count': period_record_count,
        'unpaid_count': unpaid_expenses,
        'overdue_count': overdue_expenses,
        'upcoming_payments': float(upcoming_payments),
        'period_change': period_change,
        'comparison_total': float(comparison_total),
        'trend_data': trend_data,
        'trend_labels': trend_labels,
        'category_distribution': [{'name': n, 'total': float(t)} for n, t in category_distribution],
        'top_categories': [{'name': n, 'total': float(t), 'count': c} for n, t, c in top_categories],
        'recent_expenses': [{
            'date': f"{e.ExpenseRecord.created_at.strftime('%d.%m.%Y')}",
            'category': e.ExpenseCategory.name,
            'description': e.ExpenseRecord.description,
            'amount': float(e.ExpenseRecord.amount),
            'payment_status': e.ExpenseRecord.payment_status,
            'supplier': e.ExpenseRecord.supplier_name
        } for e in recent_expenses],
        'current_year': current_year,
        'current_month': current_month,
        'current_date': datetime.now().strftime('%d %B %Y'),
        'selected_period': period,
        'selected_category': category_id
    }
    
    # Karşılaştırma verilerini ekle
    if compare_mode != 'none':
        result.update(compare_data)
    
    return result