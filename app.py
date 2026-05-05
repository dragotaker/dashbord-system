from flask import Flask, render_template
from flasgger import Swagger
from api.routes import api_bp
from api.analytics import analytics_bp

app = Flask(__name__)

# 1. Сначала регистрируем Blueprint
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

# 2. Настраиваем Swagger с явным указанием путей
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # собираем все маршруты
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/" # Документация будет строго здесь
}

swagger = Swagger(app, config=swagger_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Страница с твоими графиками
    return render_template('dashboard.html')

if __name__ == '__main__':
    print("--- Сервер запускается ---")
    print("Фронтенд: http://127.0.0.1:5000/")
    print("Swagger (Документация): http://127.0.0.1:5000/apidocs/")
    app.run(debug=True, port=5000)