/** @odoo-module **/
/**
 * Job Application Form — Frontend JS
 * Handles submit button animation and basic UX
 */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('job-apply-form');
    const btn = document.getElementById('submit-btn');
    const spinner = document.getElementById('btn-spinner');

    if (!form || !btn) return;

    form.addEventListener('submit', function (e) {
        // Basic client-side validation
        const name = document.getElementById('partner_name');
        const email = document.getElementById('email_from');
        const phone = document.getElementById('partner_phone');
        const jobId = document.getElementById('job_id');

        if (!name.value.trim() || !email.value.trim() ||
            !phone.value.trim() || !jobId.value) {
            e.preventDefault();
            // Highlight empty fields
            [name, email, phone, jobId].forEach(function (el) {
                if (!el.value.trim()) {
                    el.style.borderColor = '#ef4444';
                    el.style.boxShadow = '0 0 0 3px rgba(239,68,68,.12)';
                }
            });
            return;
        }

        // Show spinner
        if (spinner) spinner.style.display = 'inline-block';
        btn.disabled = true;
        btn.style.opacity = '0.85';
        btn.innerHTML = spinner.outerHTML + ' Submitting your application...';
    });

    // Remove red borders on input
    document.querySelectorAll('.form-control, .form-select').forEach(function (el) {
        el.addEventListener('input', function () {
            el.style.borderColor = '';
            el.style.boxShadow = '';
        });
    });
});
