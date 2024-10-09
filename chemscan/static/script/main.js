document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form');
    const username = form.querySelector('input[name="username"]');
    const email = form.querySelector('input[name="email"]');
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    const termsCheckbox = form.querySelector('input[type="checkbox"]');

    // Form submission validation
    form.addEventListener('submit', function(event) {
        let valid = true;

        // Validate username
        if (username && username.value.trim() === '') {
            alert('First Name is required');
            valid = false;
        }

        // Validate email
        if (email && !validateEmail(email.value)) {
            alert('Please enter a valid email address');
            valid = false;
        }

        // Validate password
        if (password && password.value.length < 8) {
            alert('Password must be at least 8 characters long');
            valid = false;
        }

        // Check if passwords match
        if (password && confirmPassword && password.value !== confirmPassword.value) {
            alert('Passwords do not match');
            valid = false;
        }

        // Validate terms and conditions checkbox
        if (termsCheckbox && !termsCheckbox.checked) {
            alert('You must agree to the terms and conditions');
            valid = false;
        }

    // Email validation function
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    // Toggle password visibility function
    document.querySelectorAll('.toggle-password').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-target'));
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = '👁️‍🗨️'; // Eye icon
            } else {
                passwordInput.type = 'password';
                this.textContent = '👁️'; // Closed eye icon
            }
        });
    });

    // Barcode scanning functionality
    document.getElementById('scan-button').addEventListener('click', function() {
        document.getElementById('scanner-container').style.display = 'block';
        startScanner();
    });

    function startScanner() {
        const scannerContainer = document.getElementById('scanner-container');
        const videoElement = document.getElementById('video');
        const barcodeInput = document.getElementById('barcode-input');
        const loadingSpinner = document.querySelector('.loading-spinner');

        // Initialize QuaggaJS
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: videoElement,
                constraints: {
                    facingMode: "environment" // Use the rear camera
                }
            },
            decoder: {
                readers: ["ean_reader", "ean_8_reader", "code_128_reader"]
            }
        }, function(err) {
            if (err) {
                console.error("QuaggaJS initialization error: ", err);
                return;
            }
            Quagga.start();
            loadingSpinner.style.display = 'block';
        });

        Quagga.onDetected(function(result) {
            var barcode = result.codeResult.code;
            barcodeInput.value = barcode;
            Quagga.stop();
            scannerContainer.style.display = 'none';
            loadingSpinner.style.display = 'none';
            form.submit(); // Submit the form
        });

        Quagga.onStop(function() {
            loadingSpinner.style.display = 'none';
        });
    }
});
