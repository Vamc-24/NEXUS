const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('feedback-form');
    const formContainer = document.getElementById('form-container');
    const successScreen = document.getElementById('success-screen');
    const submitAnotherBtn = document.getElementById('submit-another');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            const formData = new FormData(form);
            const data = {
                category: formData.get('category'),
                text: formData.get('feedback'),
                timestamp: new Date().toISOString()
            };

            try {
                const response = await fetch(`${API_URL}/feedback`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                if (response.ok) {
                    formContainer.classList.add('hidden');
                    successScreen.classList.remove('hidden');
                    form.reset();
                } else {
                    alert('Error submitting feedback. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error. Is the backend running?');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Feedback';
            }
        });
    }

    if (submitAnotherBtn) {
        submitAnotherBtn.addEventListener('click', () => {
            successScreen.classList.add('hidden');
            formContainer.classList.remove('hidden');
        });
    }
});
