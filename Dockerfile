# Указываем базовый образ с Python
FROM python:3.11-slim

# Ставим рабочую директорию внутри контейнера
WORKDIR /app

# Копируем список библиотек
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта (коды, модели .pkl, статику)
COPY . .

# Пробрасываем порт Flask
EXPOSE 5000

# Запускаем сервер
CMD ["python", "app.py"]