(function() {

let mainChart, ageChart, bmiChart, detailsChart;
const colorPalette = ['#2563eb', '#059669', '#f59e0b', '#dc2626', '#8b5cf6', '#06b6d4'];

if (typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
}


const globalDatalabelsOptions = {
    display: true, 
    color: '#475569', 
    font: { weight: 'bold', size: 12 },
    align: 'top',
    anchor: 'end',
    offset: 4 
};

async function updateDashboard() {
    const query = getParams();
    try {
        await loadStats(query);
        await loadMainChart(query);
        await loadAgeChart(query);
        await loadBMIChart(query);
        closeDetails(); 
    } catch (error) {
        console.error('Ошибка при обновлении дашборда:', error);
    }
}

function getParams() {
    const start = document.getElementById('dateStart').value;
    const end = document.getElementById('dateEnd').value;
    return `?start=${start}&end=${end}`;
}

async function loadStats(query = '') {
    const response = await fetch(`/analytics/stats${query}`);
    const stats = await response.json();
    document.getElementById('statTotal').textContent = stats.total_patients || 0;
    document.getElementById('statAge').textContent = stats.avg_age || 0;
    document.getElementById('statBMI').textContent = stats.avg_bmi || 0;
    document.getElementById('statTop').textContent = stats.most_common || '—';
}

async function loadMainChart(query = '') {
    const response = await fetch(`/analytics/categories${query}`);
    const data = await response.json();
    const ctx = document.getElementById('mainChart').getContext('2d');
    if (mainChart) mainChart.destroy();

    mainChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: colorPalette,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' },
                datalabels: {
                    display: true, // Явное включение
                    color: '#fff', // На круге лучше белый
                    font: { weight: 'bold' },
                    formatter: (value, ctx) => {
                        let sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        let percentage = (value * 100 / sum).toFixed(1) + "%";
                        return value > (sum * 0.04) ? `${value}\n(${percentage})` : null;
                    }
                }
            },
            onClick: async (event, elements) => {
                if (elements.length > 0) {
                    await loadDetails(mainChart.data.labels[elements[0].index], query);
                }
            }
        }
    });
}

async function loadAgeChart(query = '') {
    const response = await fetch(`/analytics/age-dist${query}`);
    const data = await response.json();
    const ctx = document.getElementById('ageChart').getContext('2d');
    if (ageChart) ageChart.destroy();

    ageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{ label: 'Пациенты', data: data.values, backgroundColor: '#2563eb', borderRadius: 6 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 30 } }, 
            plugins: {
                legend: { display: false },
                datalabels: {
                    display: true,
                    anchor: 'end',
                    align: 'top',
                    color: '#475569',
                    font: { weight: '600' }
                }
            },
            scales: { y: { beginAtZero: true, grid: { display: false } } }
        }
    });
}

async function loadBMIChart(query = '') {
    const response = await fetch(`/analytics/bmi-dist${query}`);
    const data = await response.json();
    const ctx = document.getElementById('bmiChart').getContext('2d');
    if (bmiChart) bmiChart.destroy();

    bmiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{ data: data.values, backgroundColor: ['#06b6d4', '#16a34a', '#f59e0b', '#dc2626', '#991b1b'], borderRadius: 6 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 30 } },
            plugins: {
                legend: { display: false },
                datalabels: {
                    display: true,
                    anchor: 'end',
                    align: 'top',
                    color: '#475569',
                    font: { weight: '600' }
                }
            },
            scales: { y: { beginAtZero: true, grid: { display: false } } }
        }
    });
}

async function loadDetails(categoryName, query = '') {
    const fullQuery = query ? `${query}&name=${encodeURIComponent(categoryName)}` : `?name=${encodeURIComponent(categoryName)}`;
    const response = await fetch(`/analytics/categories${fullQuery}`);
    const data = await response.json();
    const section = document.getElementById('detailsSection');
    section.style.display = 'block';
    document.getElementById('detailsTitle').textContent = `Топ диагнозов: ${categoryName}`;
    const ctx = document.getElementById('detailsChart').getContext('2d');
    if (detailsChart) detailsChart.destroy();

    detailsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{ data: data.values, backgroundColor: data.labels.map((_, i) => colorPalette[i % colorPalette.length]), borderRadius: 6 }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                datalabels: {
                    display: true,
                    anchor: 'end',
                    align: 'right', 
                    color: '#475569',
                    offset: 8
                }
            },
            scales: { x: { beginAtZero: true, grid: { display: false } } }
        }
    });
    section.scrollIntoView({ behavior: 'smooth' });
}

function closeDetails() {
    const section = document.getElementById('detailsSection');
    if (section) section.style.display = 'none';
    if (detailsChart) detailsChart.destroy();
}

function resetFilters() {
    document.getElementById('dateStart').value = '';
    document.getElementById('dateEnd').value = '';
    updateDashboard();
}

document.addEventListener('DOMContentLoaded', () => updateDashboard());
window.updateDashboard = updateDashboard;
window.resetFilters = resetFilters;
window.closeDetails = closeDetails;})(); 