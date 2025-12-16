from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Admin, Payment, Complaint
from datetime import datetime, timezone, timedelta
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_photos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'id_proofs'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'payment_proofs'), exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder, prefix=''):
    """Save uploaded file with secure filename"""
    if file and file.filename and allowed_file(file.filename):
        # Get file extension
        ext = file.filename.rsplit('.', 1)[1].lower()
        # Generate unique filename using UUID
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        # Secure the filename
        filename = secure_filename(filename)
        # Full path
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        # Save file
        file.save(filepath)
        # Return relative path for database storage
        return os.path.join('uploads', folder, filename).replace('\\', '/')
    return None

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Helper function to check admin login
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check tenant login
def tenant_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('tenant_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return redirect(url_for('admin_login'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill all fields', 'error')
            return render_template('admin_login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_tenants = User.query.count()
    total_payments = Payment.query.count()
    pending_payments = Payment.query.filter_by(status='pending').count()
    approved_payments = Payment.query.filter_by(status='approved').count()
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='pending').count()
    resolved_complaints = Complaint.query.filter_by(status='resolved').count()
    
    return render_template('admin_dashboard.html',
                         total_tenants=total_tenants,
                         total_payments=total_payments,
                         pending_payments=pending_payments,
                         approved_payments=approved_payments,
                         total_complaints=total_complaints,
                         pending_complaints=pending_complaints,
                         resolved_complaints=resolved_complaints)

@app.route('/admin/add_tenant', methods=['GET', 'POST'])
@admin_required
def add_tenant():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        room_number = request.form.get('room_number')
        monthly_rent = request.form.get('monthly_rent')
        deposit_amount = request.form.get('deposit_amount')
        deposit_paid_date = request.form.get('deposit_paid_date')
        password = request.form.get('password')
        
        # File uploads
        profile_photo = request.files.get('profile_photo')
        id_proof_photo = request.files.get('id_proof_photo')
        
        # Validation - required fields
        if not all([name, email, phone, room_number, monthly_rent, password]):
            flash('Please fill all required fields', 'error')
            return render_template('add_tenant.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('add_tenant.html')
        
        # Validate file uploads if provided
        if profile_photo and profile_photo.filename:
            if not allowed_file(profile_photo.filename):
                flash('Profile photo must be a JPG, JPEG, or PNG file', 'error')
                return render_template('add_tenant.html')
        
        if id_proof_photo and id_proof_photo.filename:
            if not allowed_file(id_proof_photo.filename):
                flash('ID proof must be a JPG, JPEG, or PNG file', 'error')
                return render_template('add_tenant.html')
        
        try:
            monthly_rent = float(monthly_rent)
            deposit_amount_val = float(deposit_amount) if deposit_amount else None
            deposit_date_obj = None
            
            if deposit_paid_date:
                try:
                    deposit_date_obj = datetime.strptime(deposit_paid_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid deposit paid date format', 'error')
                    return render_template('add_tenant.html')
            
            # Save uploaded files
            profile_photo_path = None
            id_proof_photo_path = None
            
            if profile_photo and profile_photo.filename:
                profile_photo_path = save_uploaded_file(profile_photo, 'profile_photos', 'profile')
                if not profile_photo_path:
                    flash('Error saving profile photo', 'error')
                    return render_template('add_tenant.html')
            
            if id_proof_photo and id_proof_photo.filename:
                id_proof_photo_path = save_uploaded_file(id_proof_photo, 'id_proofs', 'idproof')
                if not id_proof_photo_path:
                    flash('Error saving ID proof photo', 'error')
                    return render_template('add_tenant.html')
            
            # Create user
            user = User(
                name=name,
                email=email,
                phone=phone,
                room_number=room_number,
                monthly_rent=monthly_rent,
                profile_photo=profile_photo_path,
                id_proof_photo=id_proof_photo_path,
                deposit_amount=deposit_amount_val,
                deposit_paid_date=deposit_date_obj
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'Tenant {name} added successfully!', 'success')
            return redirect(url_for('view_tenants'))
        except ValueError as e:
            flash('Invalid amount format', 'error')
        except Exception as e:
            flash(f'Error adding tenant: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_tenant.html')

@app.route('/admin/tenants')
@admin_required
def view_tenants():
    tenants = User.query.order_by(User.created_at.desc()).all()
    return render_template('tenants.html', tenants=tenants)

@app.route('/admin/tenant/<int:tenant_id>')
@admin_required
def tenant_detail(tenant_id):
    tenant = User.query.get_or_404(tenant_id)
    payments = Payment.query.filter_by(tenant_id=tenant_id).order_by(Payment.created_at.desc()).all()
    return render_template('tenant_detail.html', tenant=tenant, payments=payments)

@app.route('/admin/payments')
@admin_required
def view_payments():
    status_filter = request.args.get('status', 'all')
    query = Payment.query
    
    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'approved':
        query = query.filter_by(status='approved')
    
    payments = query.order_by(Payment.created_at.desc()).all()
    return render_template('admin_payments.html', payments=payments, status_filter=status_filter)

@app.route('/admin/monthly-payment-status', methods=['GET', 'POST'])
@admin_required
def admin_monthly_payment_status():
    # Month options consistent with tenant payment form
    month_options = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    current_year = datetime.utcnow().year
    year_options = list(range(current_year - 2, current_year + 6))  # e.g., 2023-2030 rolling window

    selected_month = request.args.get('month') or request.form.get('month') or month_options[0]
    selected_year = int(request.args.get('year') or request.form.get('year') or current_year)

    # Map month name to month number
    month_to_num = {name: idx for idx, name in enumerate(month_options, start=1)}
    selected_month_num = month_to_num.get(selected_month, 1)

    # End of selected month for join-date filtering
    next_month = selected_month_num % 12 + 1
    next_month_year = selected_year + (1 if selected_month_num == 12 else 0)
    month_end = datetime(next_month_year, next_month, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

    # Only consider tenants who joined on or before end of selected month
    tenants = (
        User.query
        .filter(User.created_at <= month_end)
        .order_by(User.name.asc())
        .all()
    )

    # Fetch payments for selected month/year
    payments_for_month = (
        Payment.query
        .filter(
            Payment.month == selected_month,
            Payment.payment_date.between(
                datetime(selected_year, selected_month_num, 1).date(),
                month_end.date()
            )
        )
        .order_by(Payment.created_at.desc())
        .all()
    )

    # Track latest approved and pending payments per tenant for the selected period
    latest_approved = {}
    latest_pending = {}
    for payment in payments_for_month:
        if payment.status == 'approved' and payment.tenant_id not in latest_approved:
            latest_approved[payment.tenant_id] = payment
        elif payment.status == 'pending' and payment.tenant_id not in latest_pending:
            latest_pending[payment.tenant_id] = payment

    paid_tenants = []
    pending_tenants = []

    for tenant in tenants:
        if tenant.id in latest_approved:
            paid_tenants.append({
                'tenant': tenant,
                'payment': latest_approved[tenant.id],
                'status_label': 'Paid'
            })
        else:
            pending_payment = latest_pending.get(tenant.id)
            status_label = 'Pending Approval' if pending_payment else 'Not Paid'
            pending_tenants.append({
                'tenant': tenant,
                'payment': pending_payment,
                'status_label': status_label
            })

    return render_template(
        'admin_monthly_status.html',
        month_options=month_options,
        year_options=year_options,
        selected_month=selected_month,
        selected_year=selected_year,
        paid_tenants=paid_tenants,
        pending_tenants=pending_tenants
    )

@app.route('/admin/approve_payment/<int:payment_id>', methods=['POST'])
@admin_required
def approve_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'approved'
    db.session.commit()
    flash('Payment approved successfully!', 'success')
    return redirect(url_for('view_payments', status='pending'))

# Tenant Routes
@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill all fields', 'error')
            return render_template('tenant_login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['tenant_id'] = user.id
            session['tenant_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('tenant_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('tenant_login.html')

@app.route('/tenant/logout')
def tenant_logout():
    session.pop('tenant_id', None)
    session.pop('tenant_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('tenant_login'))

@app.route('/tenant/dashboard')
@tenant_required
def tenant_dashboard():
    tenant_id = session['tenant_id']
    tenant = User.query.get(tenant_id)
    recent_payments = Payment.query.filter_by(tenant_id=tenant_id).order_by(Payment.created_at.desc()).limit(5).all()
    pending_count = Payment.query.filter_by(tenant_id=tenant_id, status='pending').count()
    pending_complaints = Complaint.query.filter_by(tenant_id=tenant_id, status='pending').count()
    
    return render_template('tenant_dashboard.html',
                         tenant=tenant,
                         recent_payments=recent_payments,
                         pending_count=pending_count,
                         pending_complaints=pending_complaints)

@app.route('/tenant/profile')
@tenant_required
def tenant_profile():
    tenant_id = session['tenant_id']
    tenant = User.query.get(tenant_id)
    return render_template('tenant_profile.html', tenant=tenant)

@app.route('/tenant/add_payment', methods=['GET', 'POST'])
@tenant_required
def add_payment():
    tenant_id = session['tenant_id']
    tenant = User.query.get(tenant_id)
    
    if request.method == 'POST':
        month = request.form.get('month')
        amount = request.form.get('amount')
        transaction_id = request.form.get('transaction_id')
        payment_date = request.form.get('payment_date')
        payment_proof_file = request.files.get('payment_proof')
        
        if not all([month, amount, transaction_id, payment_date]):
            flash('Please fill all required fields', 'error')
            return render_template('add_payment.html', tenant=tenant)
        
        # Validate payment proof file if provided
        payment_proof_path = None
        if payment_proof_file and payment_proof_file.filename:
            if not allowed_file(payment_proof_file.filename):
                flash('Payment proof must be a JPG, JPEG, or PNG file', 'error')
                return render_template('add_payment.html', tenant=tenant)
            
            # Save payment proof file
            payment_proof_path = save_uploaded_file(payment_proof_file, 'payment_proofs', 'payment')
            if not payment_proof_path:
                flash('Error saving payment proof image', 'error')
                return render_template('add_payment.html', tenant=tenant)
        
        try:
            amount = float(amount)
            payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
            
            payment = Payment(
                tenant_id=tenant_id,
                month=month,
                amount=amount,
                payment_date=payment_date_obj,
                transaction_id=transaction_id,
                payment_proof=payment_proof_path,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            flash('Payment submitted successfully! Waiting for approval.', 'success')
            return redirect(url_for('tenant_payment_history'))
        except ValueError:
            flash('Invalid amount or date format', 'error')
        except Exception as e:
            flash(f'Error submitting payment: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_payment.html', tenant=tenant)

@app.route('/tenant/payments')
@tenant_required
def tenant_payment_history():
    tenant_id = session['tenant_id']
    payments = Payment.query.filter_by(tenant_id=tenant_id).order_by(Payment.created_at.desc()).all()
    return render_template('tenant_payments.html', payments=payments)

# Tenant Complaint Routes
@app.route('/tenant/complaint/new', methods=['GET', 'POST'])
@tenant_required
def raise_complaint():
    tenant_id = session['tenant_id']
    tenant = User.query.get(tenant_id)
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        description = request.form.get('description')
        
        if not subject or not description:
            flash('Please fill all fields', 'error')
            return render_template('raise_complaint.html', tenant=tenant)
        
        if len(subject.strip()) == 0 or len(description.strip()) == 0:
            flash('Subject and description cannot be empty', 'error')
            return render_template('raise_complaint.html', tenant=tenant)
        
        try:
            complaint = Complaint(
                tenant_id=tenant_id,
                subject=subject.strip(),
                description=description.strip(),
                status='pending'
            )
            db.session.add(complaint)
            db.session.commit()
            flash('Complaint raised successfully!', 'success')
            return redirect(url_for('tenant_complaints'))
        except Exception as e:
            flash('Error raising complaint', 'error')
            db.session.rollback()
    
    return render_template('raise_complaint.html', tenant=tenant)

@app.route('/tenant/complaints')
@tenant_required
def tenant_complaints():
    tenant_id = session['tenant_id']
    complaints = Complaint.query.filter_by(tenant_id=tenant_id).order_by(Complaint.created_at.desc()).all()
    return render_template('tenant_complaints.html', complaints=complaints)

# Admin Complaint Routes
@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    status_filter = request.args.get('status', 'all')
    query = Complaint.query
    
    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'resolved':
        query = query.filter_by(status='resolved')
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    return render_template('admin_complaints.html', complaints=complaints, status_filter=status_filter)

@app.route('/admin/complaint/resolve/<int:complaint_id>', methods=['POST'])
@admin_required
def resolve_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.status == 'pending':
        complaint.status = 'resolved'
        complaint.resolved_at = datetime.utcnow()
        db.session.commit()
        flash('Complaint resolved successfully!', 'success')
    else:
        flash('Complaint is already resolved', 'error')
    
    return redirect(url_for('admin_complaints', status='pending'))

if __name__ == '__main__':
    app.run(debug=True)

