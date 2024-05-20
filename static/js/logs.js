document.addEventListener('DOMContentLoaded', function() {
    const logsDiv = document.getElementById('logs');
    const refreshInterval = 5000; // 5 seconds

    function fetchLogs() {
        fetch('/logs_data')
            .then(response => response.json())
            .then(data => {
                logsDiv.innerHTML = '';
                data.forEach(log => {
                    const logElement = document.createElement('div');
                    logElement.className = 'log-entry';
                    logElement.innerHTML = `
                        <strong>Timestamp:</strong> ${log.timestamp}<br>
                        <strong>Source IP:</strong> ${log.source_ip}<br>
                        <strong>Destination URL:</strong> ${log.destination_url}<br>
                        <strong>Request Size:</strong> ${log.request_size}<br>
                        <strong>Response Size:</strong> ${log.response_size}<br>
                        <hr>
                    `;
                    logsDiv.appendChild(logElement);
                });
            })
            .catch(error => console.error('Error fetching logs:', error));
    }

    if (logsDiv) {
        fetchLogs();
        setInterval(fetchLogs, refreshInterval);
    }
});
