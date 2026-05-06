/* ===== Ghost Practice - Client-Side JS ===== */

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash-message').forEach(msg => {
        setTimeout(() => { msg.style.opacity = '0'; msg.style.transform = 'translateY(-10px)'; setTimeout(() => msg.remove(), 300); }, 4000);
    });
});

// Simulate Activities (AJAX)
function simulateActivities(count = 1) {
    const btn = document.getElementById('simulate-btn') || event.target.closest('.btn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...'; }
    
    fetch('/api/simulate-activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: count })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) { alert(data.error); }
        else { showNotification(data.message, 'success'); setTimeout(() => location.reload(), 1000); }
    })
    .catch(() => showNotification('Failed to simulate activities', 'error'))
    .finally(() => { if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-radar"></i> Auto-Detect Activities'; } });
}

// Notification toast
function showNotification(message, type = 'info') {
    const n = document.createElement('div');
    n.className = `flash-message flash-${type}`;
    n.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;min-width:300px;';
    n.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i> ${message}`;
    document.body.appendChild(n);
    setTimeout(() => { n.style.opacity = '0'; setTimeout(() => n.remove(), 300); }, 3000);
}

// Weekly Chart
function initWeeklyChart(labels, data) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hours',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.1)' }, ticks: { color: '#94a3b8', font: { family: 'Inter' } } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { family: 'Inter' } } }
            }
        }
    });
}
