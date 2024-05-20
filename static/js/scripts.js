// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const logsSection = document.querySelector('.logs-section');
    const reportSection = document.querySelector('.report-section');

    logsSection.addEventListener('click', function() {
        window.location.href = '/logs';
    });

    reportSection.addEventListener('click', function() {
        window.location.href = '/report';
    });
});
