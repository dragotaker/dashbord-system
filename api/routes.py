from flask import Blueprint, request, jsonify
import logging
# Импортируем наш процессор, который считает ИМТ и клеит пол
from ml_core.processor import processor

# СНАЧАЛА СОЗДАЕМ ОБЪЕКТ
api_bp = Blueprint('api', __name__)

# ТЕПЕРЬ ОН ОПРЕДЕЛЕН И ЕГО МОЖНО ИСПОЛЬЗОВАТЬ
@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    file: ../docs/predict.yaml
    """
    try:
        data = request.get_json()
        # 1. Получаем данные и считаем ИМТ
        X_final, bmi, foot_size, age = processor.process_input(data)
        
        # 2. Делаем прогноз
        prediction_data = processor.get_detailed_prediction(X_final, bmi, foot_size, age)

        # 3. ЛОГИРОВАНИЕ: Сохраняем данные для мониторинга
        processor.log_prediction(data['features'], bmi, prediction_data)

        return jsonify({
            "status": "success",
            "prediction": prediction_data, # Тут внутри лежат top_results и recommendations
            "bmi_calculated": round(bmi, 2)
        })
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400