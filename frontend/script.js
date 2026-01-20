// script.js - Updated for New Landing Page & Auth Flow

document.addEventListener('DOMContentLoaded', () => {

    // --- Elements ---
    const landingPage = document.getElementById('landing-page');
    const roleSelection = document.getElementById('role-selection');
    const navLoginBtn = document.getElementById('nav-login-btn');
    const heroLoginBtn = document.getElementById('hero-login-btn');
    const navRegisterBtn = document.getElementById('nav-register-btn');
    const heroRegisterBtn = document.getElementById('hero-register-btn');

    // Modals
    const loginModal = document.getElementById('institute-login-modal');
    const registerModal = document.getElementById('register-modal');
    const closeLogin = document.getElementById('close-login');
    const closeRegister = document.getElementById('close-register');

    // Auth Actions
    const verifyBtn = document.getElementById('verify-institute-btn');
    const registerSubmitBtn = document.getElementById('submit-registration-btn');
    const exitBtn = document.getElementById('exit-institute-btn');

    // --- State Check ---
    checkInstituteAccess();

    // --- Event Listeners ---

    // Open Login Modal
    const openLogin = () => loginModal.classList.remove('hidden');
    navLoginBtn.addEventListener('click', openLogin);
    heroLoginBtn.addEventListener('click', openLogin);

    // Open Register Modal
    const openRegister = () => registerModal.classList.remove('hidden');
    navRegisterBtn.addEventListener('click', openRegister);
    heroRegisterBtn.addEventListener('click', openRegister);

    // Close Modals
    closeLogin.addEventListener('click', () => loginModal.classList.add('hidden'));
    closeRegister.addEventListener('click', () => registerModal.classList.add('hidden'));

    // Close on outside click
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) loginModal.classList.add('hidden');
        if (e.target === registerModal) registerModal.classList.add('hidden');
    });


    // --- Core Logic ---

    // 1. Institute Login
    // 1. Institute Login
    verifyBtn.addEventListener('click', async () => {
        const accessIdInput = document.getElementById('institute-access-id');
        const accessId = accessIdInput.value.trim();

        if (!accessId) {
            showError('login-error-msg', 'Please enter an Access ID', [accessIdInput]);
            return;
        }

        try {
            const response = await fetch('/api/institute/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: accessId })
            });

            const data = await response.json();
            if (data.valid) {
                sessionStorage.setItem('institute_id', accessId);
                sessionStorage.setItem('institute_name', data.name);
                loginModal.classList.add('hidden');
                showRoleSelection(data.name);
            } else {
                showError('login-error-msg', 'Invalid Access ID', [accessIdInput]);
            }
        } catch (error) {
            console.error('Error:', error);
            showError('login-error-msg', 'Server Connection Error', [accessIdInput]);
        }
    });

    // Helper Function for Errors
    function showError(elementId, message, inputs = []) {
        const errorDiv = document.getElementById(elementId);
        if (!errorDiv) return alert(message); // Fallback

        errorDiv.textContent = message;
        errorDiv.classList.add('visible');

        inputs.forEach(input => input.classList.add('input-error'));

        // Vanish after 3 seconds
        setTimeout(() => {
            errorDiv.classList.remove('visible');
            inputs.forEach(input => input.classList.remove('input-error'));
        }, 3000);
    }

    // 2. Institute Registration
    registerSubmitBtn.addEventListener('click', async () => {
        const name = document.getElementById('reg-inst-name').value;
        const email = document.getElementById('reg-inst-email').value;
        const address = document.getElementById('reg-inst-address').value;
        const code = document.getElementById('reg-inst-code').value;

        if (!name || !code) return alert('Name and Code are required!');

        try {
            const response = await fetch('/api/institute/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, email, address, code: code,
                    admin_id: document.getElementById('reg-admin-id').value,
                    password: document.getElementById('reg-admin-password').value
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                alert('Registration Successful! Your Access ID is: ' + data.id);
                document.getElementById('institute-access-id').value = data.id;
                registerModal.classList.add('hidden');
                loginModal.classList.remove('hidden'); // Auto redirect to login
            } else {
                alert('Error: ' + (data.error || data.message));
            }
        } catch (error) {
            alert('Registration failed due to network error.');
        }
    });

    // 3. Exit Portal
    exitBtn.addEventListener('click', () => {
        // Smooth Fade Out
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '0';

        setTimeout(() => {
            sessionStorage.removeItem('institute_id');
            sessionStorage.removeItem('institute_name');
            // Reload to reset state fully or showLandingPage
            window.location.reload();
        }, 500);
    });

    // 4. Role Redirects
    document.querySelectorAll('.premium-role-card').forEach(card => {
        card.addEventListener('click', (e) => {
            const role = card.getAttribute('data-role');
            const instituteId = sessionStorage.getItem('institute_id');

            if (instituteId) {
                // Smooth Fade Out Effect
                document.body.style.transition = 'opacity 0.5s ease';
                document.body.style.opacity = '0';

                setTimeout(() => {
                    if (role === 'Student' || role === 'Faculty' || role === 'Staff') {
                        // Feedback Givers
                        window.location.href = `feedback.html?role=${role}`;
                    } else if (role === 'Admin') {
                        // Admin Security Layer
                        window.location.href = `admin_login.html`; // Redirect to Secure Admin Login
                    }
                }, 500); // Wait for transition
            }
        });
    });


    // --- View Controllers ---

    function checkInstituteAccess() {
        const existingId = sessionStorage.getItem('institute_id');
        const existingName = sessionStorage.getItem('institute_name');

        if (existingId) {
            showRoleSelection(existingName);
        } else {
            showLandingPage();
        }
    }

    function showLandingPage() {
        landingPage.style.display = 'block';
        roleSelection.classList.add('hidden');
        document.body.style.overflow = 'auto'; // Enable scroll
        document.querySelector('.navbar').style.display = 'flex'; // Show Main Nav
    }

    function showRoleSelection(name) {
        landingPage.style.display = 'none';
        roleSelection.classList.remove('hidden');
        document.getElementById('display-institute-name').innerText = name || '';
        document.querySelector('.navbar').style.display = 'none'; // Hide Main Nav
    }



});
