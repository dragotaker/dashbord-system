let mainChart, ageChart, bmiChart, detailsChart;

async function init() {
    try {
        await loadStats();
        await loadMainChart();
        await loadAgeChart();
        await loadBMIChart();
    } catch (error) {
        console.error('Ошибка инициализации:', error);
    }
}

async function loadStats() {
    const response = await fetch('/analytics/stats');
    const stats = await response.json();

    document.getElementById('statTotal').textContent = stats.total_patients || 0;
    document.getElementById('statAge').textContent = stats.avg_age || 0;
    document.getElementById('statBMI').textContent = stats.avg_bmi || 0;
    document.getElementById('statTop').textContent = stats.most_common || '—';
}

async function loadMainChart() {
    const response = await fetch('/analytics/categories');
    const data = await response.json();

    const ctx = document.getElementById('mainChart').getContext('2d');

    const categories = Object.keys(data);
    const values = Object.values(data);

    mainChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#2563eb',
                    '#16a34a',
                    '#f59e0b',
                    '#dc2626',
                    '#8b5cf6',
                    '#06b6d4'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percent = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percent}%)`;
                        }
                    }
                }
            },
            onClick: async (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const categoryName = mainChart.data.labels[index];
                    await loadDetails(categoryName);
                }
            }
        }
    });
}

async function loadAgeChart() {
    const response = await fetch('/analytics/age-dist');
    const data = await response.json();

    const ctx = document.getElementById('ageChart').getContext('2d');

    ageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Количество пациентов',
                data: data.values,
                backgroundColor: [
                    '#2563eb',
                    '#16a34a',
                    '#f59e0b',
                    '#dc2626'
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

async function loadBMIChart() {
    const response = await fetch('/analytics/bmi-dist');
    const data = await response.json();

    const ctx = document.getElementById('bmiChart').getContext('2d');

    const colors = data.labels.map(label => {
        const colorMap = {
            'Дефицит': '#06b6d4',
            'Норма': '#16a34a',
            'Избыток': '#f59e0b',
            'Ожирение I': '#dc2626',
            'Ожирение II+': '#991b1b'
        };
        return colorMap[label] || '#64748b';
    });

    bmiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Количество пациентов',
                data: data.values,
                backgroundColor: colors,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

async function loadDetails(categoryName) {
    const response = await fetch(`/analytics/categories?name=${encodeURIComponent(categoryName)}`);
    const data = await response.json();

    const section = document.getElementById('detailsSection');
    section.style.display = 'block';
    document.getElementById('detailsTitle').textContent = `Топ диагнозов: ${categoryName}`;

    const ctx = document.getElementById('detailsChart').getContext('2d');

    if (detailsChart) {
        detailsChart.destroy();
    }

    detailsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Количество случаев',
                data: data.values,
                backgroundColor: data.values.map((_, i) => {
                    const colors = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6', '#06b6d4', '#64748b'];
                    return colors[i % colors.length];
                }),
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });

    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function closeDetails() {
    const section = document.getElementById('detailsSection');
    section.style.display = 'none';

    if (detailsChart) {
        detailsChart.destroy();
        detailsChart = null;
    }
}

window.addEventListener('resize', () => {
    mainChart?.resize();
    ageChart?.resize();
    bmiChart?.resize();
    detailsChart?.resize();
});

function closeDetails() {
    const section = document.getElementById('detailsSection');
    section.style.display = 'none';

    if (detailsChart) {
        detailsChart.destroy();
        detailsChart = null;
    }
}

window.addEventListener('resize', () => {
    mainChart?.resize();
    ageChart?.resize();
    bmiChart?.resize();
    detailsChart?.resize();
});

// Правильная инициализация
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

document.addEventListener('DOMContentLoaded', init);