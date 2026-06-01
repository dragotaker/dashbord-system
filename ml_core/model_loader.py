import joblib
import os
import logging
from config import Config 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        try:
            self.model = joblib.load(Config.MODEL_PATH)
            
            self.scaler = joblib.load(Config.SCALER_PATH)
            
            self.encoder = joblib.load(Config.ENCODER_PATH)
            
            logger.info("Все компоненты успешно загружены из Config.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке компонентов: {e}")
            raise

ml_assets = ModelLoader()

model = ml_assets.model
scaler = ml_assets.scaler
encoder = ml_assets.encoder