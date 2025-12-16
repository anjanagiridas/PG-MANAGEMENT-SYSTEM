// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as max for payment date input
    const paymentDateInput = document.getElementById('payment_date');
    if (paymentDateInput) {
        const today = new Date().toISOString().split('T')[0];
        paymentDateInput.setAttribute('max', today);
    }

    // Admin Login Form Validation
    const adminLoginForm = document.getElementById('adminLoginForm');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!username || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }
        });
    }

    // Tenant Login Form Validation
    const tenantLoginForm = document.getElementById('tenantLoginForm');
    if (tenantLoginForm) {
        tenantLoginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }

            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return false;
            }
        });
    }

    // Add Tenant Form Validation
    const addTenantForm = document.getElementById('addTenantForm');
    if (addTenantForm) {
        addTenantForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const roomNumber = document.getElementById('room_number').value.trim();
            const monthlyRent = document.getElementById('monthly_rent').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!name || !email || !phone || !roomNumber || !monthlyRent || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return false;
            }

            // Phone validation (basic)
            const phoneRegex = /^[0-9]{10}$/;
            if (!phoneRegex.test(phone.replace(/\D/g, ''))) {
                e.preventDefault();
                alert('Please enter a valid phone number');
                return false;
            }

            // Rent validation
            if (parseFloat(monthlyRent) <= 0) {
                e.preventDefault();
                alert('Monthly rent must be greater than 0');
                return false;
            }

            // Password validation
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long');
                return false;
            }
        });
    }

    // Add Payment Form Validation
    const addPaymentForm = document.getElementById('addPaymentForm');
    if (addPaymentForm) {
        const paymentProofInput = document.getElementById('payment_proof');
        const maxFileSize = 2 * 1024 * 1024; // 2MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];

        // File validation function
        function validatePaymentProofFile(file) {
            if (!file) return true; // File is optional
            
            // Check file type
            if (!allowedTypes.includes(file.type)) {
                alert('Payment proof must be a JPG, JPEG, or PNG file');
                return false;
            }

            // Check file size
            if (file.size > maxFileSize) {
                alert('Payment proof must be less than 2MB');
                return false;
            }

            return true;
        }

        // Validate file on change
        if (paymentProofInput) {
            paymentProofInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    if (!validatePaymentProofFile(e.target.files[0])) {
                        e.target.value = ''; // Clear the input
                    }
                }
            });
        }

        addPaymentForm.addEventListener('submit', function(e) {
            const month = document.getElementById('month').value.trim();
            const amount = document.getElementById('amount').value.trim();
            const paymentDate = document.getElementById('payment_date').value.trim();
            const transactionId = document.getElementById('transaction_id').value.trim();

            if (!month || !amount || !paymentDate || !transactionId) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return false;
            }

            // Amount validation
            if (parseFloat(amount) <= 0) {
                e.preventDefault();
                alert('Amount must be greater than 0');
                return false;
            }

            // Date validation
            const selectedDate = new Date(paymentDate);
            const today = new Date();
            if (selectedDate > today) {
                e.preventDefault();
                alert('Payment date cannot be in the future');
                return false;
            }

            // Validate payment proof file if provided
            if (paymentProofInput && paymentProofInput.files.length > 0) {
                if (!validatePaymentProofFile(paymentProofInput.files[0])) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // File Upload Validation for Add Tenant Form
    addTenantForm = document.getElementById('addTenantForm');
    if (addTenantForm) {
        const profilePhotoInput = document.getElementById('profile_photo');
        const idProofPhotoInput = document.getElementById('id_proof_photo');
        const maxFileSize = 2 * 1024 * 1024; // 2MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];

        function validateFile(file, inputName) {
            if (!file) return true; // File is optional
            
            // Check file type
            if (!allowedTypes.includes(file.type)) {
                alert(`${inputName} must be a JPG, JPEG, or PNG file`);
                return false;
            }

            // Check file size
            if (file.size > maxFileSize) {
                alert(`${inputName} must be less than 2MB`);
                return false;
            }

            return true;
        }

        if (profilePhotoInput) {
            profilePhotoInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    if (!validateFile(e.target.files[0], 'Profile photo')) {
                        e.target.value = ''; // Clear the input
                    }
                }
            });
        }

        if (idProofPhotoInput) {
            idProofPhotoInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    if (!validateFile(e.target.files[0], 'ID proof photo')) {
                        e.target.value = ''; // Clear the input
                    }
                }
            });
        }

        addTenantForm.addEventListener('submit', function(e) {
            // Validate files on form submit
            if (profilePhotoInput && profilePhotoInput.files.length > 0) {
                if (!validateFile(profilePhotoInput.files[0], 'Profile photo')) {
                    e.preventDefault();
                    return false;
                }
            }

            if (idProofPhotoInput && idProofPhotoInput.files.length > 0) {
                if (!validateFile(idProofPhotoInput.files[0], 'ID proof photo')) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // Raise Complaint Form Validation
    const raiseComplaintForm = document.getElementById('raiseComplaintForm');
    if (raiseComplaintForm) {
        raiseComplaintForm.addEventListener('submit', function(e) {
            const subject = document.getElementById('subject').value.trim();
            const description = document.getElementById('description').value.trim();

            if (!subject || !description) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }

            // Subject length validation
            if (subject.length < 5) {
                e.preventDefault();
                alert('Subject must be at least 5 characters long');
                return false;
            }

            // Description length validation
            if (description.length < 10) {
                e.preventDefault();
                alert('Description must be at least 10 characters long');
                return false;
            }

            if (description.length > 2000) {
                e.preventDefault();
                alert('Description is too long (maximum 2000 characters)');
                return false;
            }
        });
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Confirm delete/approve actions
    const confirmButtons = document.querySelectorAll('[onclick*="confirm"]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure?')) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// Format phone number input
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Remove all non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            // Limit to 10 digits
            if (value.length > 10) {
                value = value.slice(0, 10);
            }
            e.target.value = value;
        });
    }
});

// Format amount input
document.addEventListener('DOMContentLoaded', function() {
    const amountInputs = document.querySelectorAll('input[type="number"][name="amount"], input[type="number"][name="monthly_rent"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            let value = parseFloat(e.target.value);
            if (!isNaN(value) && value >= 0) {
                e.target.value = value.toFixed(2);
            }
        });
    });
});

