from flask import Flask, render_template, request, redirect, url_for, session

# =====================================================================
# 1. НАСТРОЙКА ПРИЛОЖЕНИЯ И СЕКРЕТНОГО КЛЮЧА
# =====================================================================
app = Flask(__name__)
# Секретный ключ нужен Flask, чтобы безопасно хранить результаты расчетов в памяти
app.secret_key = 'anime-astral-egg-calculator-secret-key'

# Словарь с суффиксами для перевода игровых значений в числа
SUFFIXES = {
    'K': 1_000,
    'M': 1_000_000,
    'B': 1_000_000_000,
    'T': 1_000_000_000_000,
    'QA': 1_000_000_000_000_000,
    'QI': 1_000_000_000_000_000_000,
    'SX': 1_000_000_000_000_000_000_000,
    'SP': 1_000_000_000_000_000_000_000_000,
}

def parse_game_number(val_str):
    """Превращает строковое значение из игры (например, '3.5K') в число."""
    if not val_str:
        return 0.0
    val_str = str(val_str).strip().upper()
    
    # Ищем, заканчивается ли строка на известный суффикс (например, QA или K)
    for suffix, multiplier in SUFFIXES.items():
        if val_str.endswith(suffix):
            num_part = val_str[:-len(suffix)].strip()
            try:
                return float(num_part) * multiplier
            except ValueError:
                return 0.0
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def format_game_number(num):
    """Превращает большое число обратно в красивый игровой формат."""
    if num == 0:
        return "0"
    abs_num = abs(num)
    
    # Сортируем суффиксы от самых больших к меньшим
    for suffix, multiplier in sorted(SUFFIXES.items(), key=lambda x: x[1], reverse=True):
        if abs_num >= multiplier:
            formatted = f"{num / multiplier:.2f}".rstrip('0').rstrip('.')
            return f"{formatted}{suffix}"
            
    return f"{num:.2f}".rstrip('0').rstrip('.')

# =====================================================================
# 2. ТВОИ ЛОКАЦИИ (СЮДА ДОБАВЛЯЙ НОВЫЕ)
# =====================================================================
LOCATIONS = {
    "Ninja Village": parse_game_number("50"),
    "Namek City": parse_game_number("3.5K"),
    "Wano Island": parse_game_number("285K"),
    "Titan Wall": parse_game_number("21.5M"),
    "Solo City": parse_game_number("2B"),
    "Slayer Village": parse_game_number("250B"),
    "Clover Island": parse_game_number("175T"),
    "Summer Art Online": parse_game_number("25QA"),
    "Fire City": parse_game_number("75SX")
}

# =====================================================================
# 3. ЛОГИКА САЙТА (БЕЗ ПОВТОРНОЙ ОТПРАВКИ ФОРМЫ)
# =====================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1. Собираем данные из формы
        selected_loc = request.form.get("location")
        user_money_str = request.form.get("money", "0")
        
        user_money = parse_game_number(user_money_str)
        egg_cost = LOCATIONS.get(selected_loc, 0.0)
        
        # 2. Считаем математику
        if egg_cost > 0:
            total_eggs = int(user_money // egg_cost)
            leftover = user_money % egg_cost
        else:
            total_eggs = 0
            leftover = user_money
            
        # 3. Формируем результат расчетов
        result_data = {
            "selected_location": selected_loc,
            "user_money": format_game_number(user_money),
            "egg_cost": format_game_number(egg_cost),
            "total_eggs": f"{total_eggs:,}",  # Разделение разрядов запятыми для красоты
            "leftover": format_game_number(leftover)
        }
        
        # 🌟 ХИТРЫЙ ТРЮК: сохраняем результат в сессию и делаем перенаправление!
        session["calc_result"] = result_data
        return redirect(url_for("index"))
        
    # Сюда пользователь попадает при обычном GET-запросе (или после редиректа)
    # Забираем результат из памяти, если он там есть, и сразу удаляем
    result = session.pop("calc_result", None)
    
    return render_template("index.html", locations=LOCATIONS.keys(), result=result)

if __name__ == "__main__":
    app.run(debug=True)