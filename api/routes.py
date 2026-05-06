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
    Эндпоинт для предсказания патологий стопы
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: PredictionData
          required:
            - features
          properties:
            features:
              type: array
              items:
                type: number
              example: [22, 180, 80, 43, 1]
              description: "[Возраст, Рост, Вес, Размер стопы, Пол(1-м, 0-ж)]"
    responses:
      200:
        description: Успешный прогноз
        schema:
          properties:
            status:
              type: string
              example: "success"
            bmi_calculated:
              type: number
              example: 24.69
            prediction:
              type: object
              properties:
                top_results:
                  type: array
                  items:
                    type: object
                recommendations:
                  type: array
                  items:
                    type: string
      400:
        description: Ошибка валидации данных
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