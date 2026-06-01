from flask import Blueprint, request, jsonify
import logging
from ml_core.processor import processor

api_bp = Blueprint('api', __name__)

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    file: ../docs/predict.yaml
    """
    try:
        data = request.get_json()
        X_final, bmi, foot_size, age = processor.process_input(data)
        
        prediction_data = processor.get_detailed_prediction(X_final, bmi, foot_size, age)

        processor.log_prediction(data['features'], bmi, prediction_data)

        return jsonify({
            "status": "success",
            "prediction": prediction_data,
            "bmi_calculated": round(bmi, 2)
        })
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400