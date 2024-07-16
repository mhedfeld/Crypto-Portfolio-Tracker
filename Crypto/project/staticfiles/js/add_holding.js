// add_holding.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.add-holding-form');
    const inputs = form.querySelectorAll('input, select');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // Add loading state to button
        const submitBtn = this.querySelector('.submit-btn');
        submitBtn.textContent = 'Adding...';
        submitBtn.disabled = true;
        // Submit the form
        this.submit();
    });
});