// Main JavaScript file for the telemedicine platform

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Processing...';
            }
        });
    });

    // Handle alert dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'alert-close';
        closeButton.onclick = function() {
            alert.remove();
        };
        alert.appendChild(closeButton);
    });
});
