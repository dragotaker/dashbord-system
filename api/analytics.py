from flask import Blueprint, jsonify, request
import pandas as pd

analytics_bp = Blueprint("analytics", __name__)

# Твой словарь (вынеси его в отдельный конфиг или оставь тут)
KEYWORD_TO_CATEGORY = {
    # 1. Деформации стопы (самая большая группа)
    "вальгус": "Деформации стопы",
    "плоскостоп": "Деформации стопы",
    "халюс": "Деформации стопы",
    "халлюс": "Деформации стопы",
    "пяточн": "Деформации стопы",
    "шпор": "Деформации стопы",
    "натоптыш": "Деформации стопы",
    "деформац": "Деформации стопы",
    "укорочен": "Деформации стопы",
    "косточк": "Деформации стопы",
    "полый": "Деформации стопы",
    "эквинус": "Деформации стопы",
    "когтеобраз": "Деформации стопы",
    "косолап": "Деформации стопы",
    "варус": "Деформации стопы",
    "молоткообраз": "Деформации стопы",
    "метатарзалг": "Деформации стопы",
    "невром": "Деформации стопы",
    "лангунд": "Деформации стопы",
    "шинец": "Деформации стопы",
    "кейер": "Деформации стопы",
    # 2. Суставные и позвоночные патологии
    "остеохондроз": "Суставные и позвоночные патологии",
    "артроз": "Суставные и позвоночные патологии",
    "артрит": "Суставные и позвоночные патологии",
    "сколиоз": "Суставные и позвоночные патологии",
    "кифоз": "Суставные и позвоночные патологии",
    "осанк": "Суставные и позвоночные патологии",
    "грыж": "Суставные и позвоночные патологии",
    "спондил": "Суставные и позвоночные патологии",
    "контрактур": "Суставные и позвоночные патологии",
    "трохантерит": "Суставные и позвоночные патологии",
    "гофф": "Суставные и позвоночные патологии",
    "остеофит": "Суставные и позвоночные патологии",
    "бехтерев": "Суставные и позвоночные патологии",
    "дефартроз": "Суставные и позвоночные патологии",
    # 3. Травматология и реабилитация
    "перелом": "Травматология и реабилитация",
    "остеосинтез": "Травматология и реабилитация",
    "травм": "Травматология и реабилитация",
    "операц": "Травматология и реабилитация",
    "разрыв": "Травматология и реабилитация",
    "эндопротез": "Травматология и реабилитация",
    "артроскоп": "Травматология и реабилитация",
    "мениск": "Травматология и реабилитация",
    "винт": "Травматология и реабилитация",
    "пластин": "Травматология и реабилитация",
    "спиц": "Травматология и реабилитация",
    "штифт": "Травматология и реабилитация",
    "аппарат": "Травматология и реабилитация",
    "илизаров": "Травматология и реабилитация",
    "реконструкц": "Травматология и реабилитация",
    "резекция": "Травматология и реабилитация",
    # 4. Системные нарушения
    "парапарез": "Системные нарушения",
    "невропат": "Системные нарушения",
    "диабет": "Системные нарушения",
    "варикоз": "Системные нарушения",
    "сосуд": "Системные нарушения",
    "лимфостаз": "Системные нарушения",
    "псориаз": "Системные нарушения",
    "хвн": "Системные нарушения",
    "дцп": "Системные нарушения",
    "спастик": "Системные нарушения",
    "язва": "Системные нарушения",
    "атрофия": "Системные нарушения",
    "hallux": "Деформации стопы",
    "палец": "Деформации стопы",
    "мозоль": "Деформации стопы",
    "синовит": "Суставные и позвоночные патологии",
    "бурсит": "Суставные и позвоночные патологии",
    "люмбаго": "Суставные и позвоночные патологии",
    "эпикондилит": "Суставные и позвоночные патологии",
    "киста": "Суставные и позвоночные патологии",
    "разрыв": "Травматология и реабилитация",
    "растяжен": "Травматология и реабилитация",
    "ушиб": "Травматология и реабилитация",
    "гематом": "Травматология и реабилитация",
    "удален": "Травматология и реабилитация",
    "шов": "Травматология и реабилитация",
}


def get_data(start_date=None, end_date=None):
    df_s = pd.read_csv('structured_data.csv', sep=';')
    df_o = pd.read_csv('orders.csv', sep=',')

    df_s.columns = df_s.columns.str.strip().str.lower()
    df_o.columns = df_o.columns.str.strip().str.lower()

    # ПРИНУДИТЕЛЬНОЕ ПРИВЕДЕНИЕ ТИПОВ ID
    # Убираем .0 и переводим в числа, чтобы 1076.0 превратилось в 1076
    df_s['id'] = pd.to_numeric(df_s['id'], errors='coerce').fillna(0).astype(int)
    df_o['id_users'] = pd.to_numeric(df_o['id_users'], errors='coerce').fillna(0).astype(int)

    # Объединяем
    df = pd.merge(
        df_s, 
        df_o[['id_users', 'date']], 
        left_on='id', 
        right_on='id_users', 
        how='left'
    )

    # Категоризация
    def categorize(diagnosis):
        if pd.isna(diagnosis) or not isinstance(diagnosis, str):
            return "Не указано"
        diag_lower = diagnosis.lower()
        for keyword, category in KEYWORD_TO_CATEGORY.items():
            if keyword in diag_lower:
                return category
        return "Другое"

    df['category'] = df['diagnosis_rus'].apply(categorize)

    # Типы данных
    if 'имт' in df.columns:
        df['имт'] = df['имт'].astype(str).str.replace(',', '.').astype(float)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # ФИЛЬТРАЦИЯ
    if start_date and start_date not in ['null', '']:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date and end_date not in ['null', '']:
        df = df[df['date'] <= pd.to_datetime(end_date)]

    # ТЕХНИЧЕСКИЙ ВЫВОД (увидишь в терминале Flask)
    print(f"DEBUG: После фильтрации осталось {len(df)} строк. Категорий 'Не указано': {len(df[df['category'] == 'Не указано'])}")

    return df

@analytics_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    file: ../docs/categories.yaml
    """
    start = request.args.get("start")
    end = request.args.get("end")
    df = get_data(start, end)
    category_name = request.args.get("name")

    # Если запрошена конкретная категория для детализации
    if category_name:
        sub_df = df[df["category"] == category_name]
        # Берем топ-10 конкретных диагнозов в этой группе
        detail_counts = sub_df["diagnosis_rus"].value_counts().head(10)
        return jsonify(
            {
                "labels": detail_counts.index.tolist(),
                "values": detail_counts.values.tolist(),
            }
        )

    # Если это запрос для главного кругового графика
    counts = df.groupby("category").size()
    # Возвращаем просто числа (если применил правку во фронте выше)
    return jsonify(counts.to_dict())


@analytics_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    file: ../docs/stats.yaml
    """
    start = request.args.get("start")
    end = request.args.get("end")
    df = get_data(start, end) # И передай их сюда
    if df.empty:
        return jsonify({
            "total_patients": 0,
            "avg_age": 0,
            "avg_bmi": 0,
            "most_common": "—"
        })

    # Считаем показатели
    total = int(len(df))
    avg_age = round(df["age"].mean(), 1) if not df["age"].empty else 0
    avg_bmi = round(df["имт"].mean(), 1) if not df["имт"].empty else 0
    
    # Безопасное получение самой частой категории
    category_counts = df["category"].value_counts()
    most_common = category_counts.idxmax() if not category_counts.empty else "—"

    stats = {
        "total_patients": total,
        "avg_age": avg_age,
        "avg_bmi": avg_bmi,
        "most_common": most_common,
    }
    return jsonify(stats)


@analytics_bp.route("/age-dist", methods=["GET"])
def get_age_dist():
    """
    file: ../docs/distributions.yaml
    """
    start = request.args.get("start")
    end = request.args.get("end")
    df = get_data(start, end) # Здесь тоже передаем фильтры
    if df.empty:
        return jsonify({})

    # Разбиваем на понятные группы
    bins = [0, 18, 35, 60, 100]
    labels = ["Дети (0-18)", "Молодежь (19-35)", "Взрослые (36-60)", "Пожилые (60+)"]

    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)
    age_counts = df["age_group"].value_counts().sort_index()

    return jsonify(
        {"labels": age_counts.index.tolist(), "values": age_counts.values.tolist()}
    )


@analytics_bp.route("/bmi-dist", methods=["GET"])
def get_bmi_dist():
    """
    file: ../docs/distributions.yaml
    """
    start = request.args.get("start")
    end = request.args.get("end")
    df = get_data(start, end) # Здесь тоже передаем фильтры
    if df.empty:
        return jsonify({})

    # Группируем ИМТ по классике ВОЗ
    bins = [0, 18.5, 25, 30, 35, 100]
    labels = ["Дефицит", "Норма", "Избыток", "Ожирение I", "Ожирение II+"]

    df["bmi_group"] = pd.cut(df["имт"], bins=bins, labels=labels, right=False)
    bmi_counts = df["bmi_group"].value_counts().sort_index()

    return jsonify(
        {"labels": bmi_counts.index.tolist(), "values": bmi_counts.values.tolist()}
    )
