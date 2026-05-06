let probabilityChart = null;

async function sendData(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    closeError();
    
    const payload = {
        features: [
            parseFloat(document.getElementById('age').value),
            parseFloat(document.getElementById('height').value),
            parseFloat(document.getElementById('weight').value),
            parseFloat(document.getElementById('foot_size').value),
            parseInt(document.getElementById('sex').value)
        ]
    };
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayResults(data);
        } else {
            showError(data.message || 'Ошибка при обработке данных');
        }
    } catch (error) {
        showError('Не удалось выполнить запрос. Проверьте соединение.');
        console.error('Ошибка:', error);
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    const mainResult = document.getElementById('mainResult');
    const probContainer = document.getElementById('probabilityBars');
    const recList = document.getElementById('recommendationsList');

    // Проверка на наличие данных
    if (!data.prediction) return;

    resultSection.style.display = 'block';
    
    const results = data.prediction.top_results || [];
    const recommendations = data.prediction.recommendations || [];
    
    if (results.length > 0) {
        // Ставим только основной диагноз
        mainResult.textContent = results[0].group;

        // Рисуем полоски
        probContainer.innerHTML = ''; 
        results.forEach((res, index) => {
            const barWrapper = document.createElement('div');
            barWrapper.className = 'prob-item';
            barWrapper.innerHTML = `
                <div class="prob-info" style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                    <span>${escapeHtml(res.group)}</span>
                    <strong>${res.probability}%</strong>
                </div>
                <div class="progress-bg" style="background: #e2e8f0; border-radius: 8px; height: 12px; width: 100%; overflow: hidden; margin-bottom: 15px;">
                    <div class="progress-fill" style="width: ${res.probability}%; background-color: ${getColorByIndex(index)}; height: 100%;"></div>
                </div>
            `;
            probContainer.appendChild(barWrapper);
        });
    }

    // Рекомендации
    recList.innerHTML = '';
    recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.style.cssText = `
            position: relative;
            padding-left: 30px;
            margin-bottom: 12px;
            line-height: 1.5;
            color: #334155;
            list-style: none;
        `;
        li.innerHTML = `
            <span style="position: absolute; left: 0; top: 2px; color: #16a34a;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </span>
            ${rec}
        `;
        recList.appendChild(li);
    });

    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getColorByIndex(index) {
    const colors = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6'];
    return colors[index] || '#64748b';
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorAlert.style.display = 'block';
    setTimeout(closeError, 5000);
}

function closeError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

function resetForm() {
    const resultSection = document.getElementById('resultSection');
    if (resultSection) {
        resultSection.style.display = 'none';
    }
    
    const formSection = document.querySelector('.form-section');
    if (formSection) {
        formSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}