import numpy as np
import pandas as pd
from ml_core.model_loader import scaler, encoder, model
from config import Config
import logging
import csv
import datetime
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self):
        """начинаем запись лога"""
        self.log_file = 'prediction_monitoring.csv'
        self._init_csv_log()


    def _init_csv_log(self):
        """Создает CSV файл с заголовками, если его еще нет"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Age', 'Height', 'Weight', 'FootSize', 'Sex', 'BMI', 'ResultGroup', 'Probability'])

    def log_prediction(self, features, bmi, prediction):
        """Записывает данные запроса и ответ модели в CSV"""
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                features[0], features[1], features[2], features[3], features[4],
                round(bmi, 2),
                prediction['top_results'][0]['group'], 
                prediction['top_results'][0]['probability'] 
            ])
        logging.info(f"Результат записан в мониторинг: {prediction['top_results'][0]['group']}")

    def process_input(self, data):
        f = data.get('features', [])
        
        if not isinstance(f, list) or len(f) != 5:
            raise ValueError("Некорректный формат данных. Ожидается список из 5 чисел.")
        
        age, height, weight, foot_size, sex = f
        
        if not (5 <= age <= 100):
            raise ValueError(f"Недопустимый возраст: {age}. Доступный диапазон 5-100 лет.")
        if not (100 <= height <= 250):
            raise ValueError(f"Проверьте рост: {height} см выглядит нереалистично.")
        if not (30 <= weight <= 250):
            raise ValueError(f"Проверьте вес: {weight} кг вне допустимого диапазона.")
        if sex not in [0, 1]:
            raise ValueError("Пол должен быть 1 (муж) или 0 (жен).")

        bmi = weight / ((height / 100) ** 2)
        
        num_data = pd.DataFrame(
            [[age, height, weight, foot_size, bmi]],
            columns=["Age", "Height", "weight", "foot_size", "имт"],
        )

        X_numeric = scaler.transform(num_data)
        X_final = np.hstack((X_numeric, [[sex]]))
        
        return X_final, bmi, foot_size, age

    def get_detailed_prediction(self, X_final, bmi, foot_size, age):
        probs = model.predict_proba(X_final)[0]
        
        all_results = []
        for i, cat_name in enumerate(encoder.classes_):
            all_results.append({
                "group": cat_name, 
                "probability": round(float(probs[i] * 100), 1)
            })

        all_results.sort(key=lambda x: x["probability"], reverse=True)
        top_3 = all_results[:3]

        for item in top_3:
            group = item["group"]
            if group == "Деформации стопы" and (foot_size > 44 or foot_size < 35):
                item["trigger"] = "Размер стопы"
            elif group == "Суставные и позвоночные патологии" and age > 50:
                item["trigger"] = "Возраст"
            elif bmi > 28:
                item["trigger"] = "ИМТ"
            else:
                item["trigger"] = "Биометрия"

        main_group = top_3[0]["group"]
        recs = Config.ADVICE_MAP.get(main_group, ["Плановый осмотр врача."]).copy()
        
        if bmi > 25:
            recs.append(f"Внимание: ИМТ ({round(bmi, 1)}) выше нормы, что создает лишнюю нагрузку.")

        return {
            "top_results": top_3,
            "recommendations": recs
        }

processor = DataProcessor()