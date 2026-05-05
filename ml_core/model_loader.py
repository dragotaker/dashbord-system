import joblib
import os
import logging
from config import Config 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        # все аргументы берутся из congif
        try:
            # Загружаем модель
            self.model = joblib.load(Config.MODEL_PATH)
            
            # Загружаем скалер для нормализации чисел
            self.scaler = joblib.load(Config.SCALER_PATH)
            
            # Загружаем энкодер для расшифровки текста[cite: 4]
            self.encoder = joblib.load(Config.ENCODER_PATH)
            
            logger.info("Все компоненты успешно загружены из Config.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке компонентов: {e}")
            raise

# Создаем экземпляр без передачи аргументов
ml_assets = ModelLoader()

# Экспортируем объекты для использования в других файлах
model = ml_assets.model
scaler = ml_assets.scaler
encoder = ml_assets.encoder