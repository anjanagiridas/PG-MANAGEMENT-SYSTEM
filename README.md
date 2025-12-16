# PG Management System

A comprehensive Paying Guest (PG) Management System built with Flask, SQLite, and modern web technologies. This system allows administrators to manage tenants and payments, while tenants can view their profile and submit monthly payments.

## 🚀 Features

### Admin Features
- **Dashboard** with statistics overview
- **Add New Tenant** with auto-generated credentials
- **View All Tenants** with detailed information
- **Approve Payments** from pending queue
- **View Payment History** with filtering options
- **View Pending Payments** for quick approval

### Tenant Features
- **Dashboard** with personal statistics
- **View Profile** with all personal details
- **Submit Monthly Payments** with transaction details
- **View Payment History** with status tracking

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Session-based (Flask sessions)
- **Security**: Werkzeug password hashing

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## 🔧 Installation

1. **Clone or download the project**
   ```bash
   cd pg_management
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5000`
   - You'll be redirected to the admin login page

## 🔐 Default Credentials

### Admin Login
- **Username**: `admin`
- **Password**: `admin123`

> **Note**: Please change the admin password after first login for security purposes.

### Tenant Login
- Tenants are created by the admin
- Each tenant receives their email and password set by admin during tenant creation

## 📁 Project Structure

```
pg_management/
│
├── app.py                 # Main Flask application
├── models.py              # Database models (User, Admin, Payment)
├── database.db            # SQLite database (created automatically)
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── admin_login.html
│   ├── tenant_login.html
│   ├── admin_dashboard.html
│   ├── tenant_dashboard.html
│   ├── add_tenant.html
│   ├── add_payment.html
│   ├── tenants.html
│   ├── tenant_detail.html
│   ├── tenant_profile.html
│   ├── tenant_payments.html
│   └── admin_payments.html
│
└── static/               # Static files
    ├── css/
    │   └── style.css    # Main stylesheet
    └── js/
        └── script.js     # JavaScript for validation and interactivity
```

## 🗄️ Database Schema

### Users Table (Tenants)
- `id` - Primary Key
- `name` - Tenant full name
- `email` - Unique email address
- `phone` - Contact number
- `room_number` - Assigned room
- `monthly_rent` - Monthly rent amount
- `password_hash` - Hashed password
- `created_at` - Registration timestamp

### Admin Table
- `id` - Primary Key
- `username` - Admin username
- `password_hash` - Hashed password

### Payments Table
- `id` - Primary Key
- `tenant_id` - Foreign Key to users.id
- `month` - Payment month
- `amount` - Payment amount
- `payment_date` - Date of payment
- `transaction_id` - UPI/Transaction reference
- `status` - Payment status (pending/approved)
- `created_at` - Submission timestamp

## 🎯 Usage Guide

### For Administrators

1. **Login** using admin credentials
2. **Add Tenants**:
   - Go to "Add New Tenant"
   - Fill in tenant details
   - Set a password for tenant login
   - Save the credentials to share with tenant

3. **Manage Payments**:
   - View pending payments from dashboard
   - Review payment details
   - Approve payments after verification

4. **View Reports**:
   - Check tenant details and payment history
   - Filter payments by status

### For Tenants

1. **Login** using email and password provided by admin
2. **View Profile** to see personal details
3. **Submit Payments**:
   - Go to "Add Payment"
   - Select month and enter amount
   - Provide transaction ID
   - Submit for admin approval

4. **Track Payments**:
   - View payment history
   - Check approval status

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- Protected routes with decorators
- Input validation on both client and server side

## 🎨 UI Features

- Modern, responsive design
- Gradient backgrounds and card-based layout
- Flash messages for user feedback
- Form validation
- Mobile-friendly interface

## 🐛 Troubleshooting

### Database Issues
- If you encounter database errors, delete `database.db` and restart the application
- The database will be recreated automatically

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using the correct Python version

## 📝 Notes

- The application runs in debug mode by default (for development)
- Change `SECRET_KEY` in `app.py` for production use
- Database file (`database.db`) is created automatically on first run
- Default admin account is created automatically if it doesn't exist

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements.

## 📄 License

This project is open source and available for educational purposes.

---

**Built with ❤️ using Flask**

