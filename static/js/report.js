// static/js/report.js

document.addEventListener('DOMContentLoaded', function() {
    const reportDiv = document.getElementById('report');

    function fetchReport() {
        fetch('/report_data')
            .then(response => response.json())
            .then(data => {
                reportDiv.textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => console.error('Error fetching report:', error));
    }

    fetchReport();
});
