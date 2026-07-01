from flask import Flask, render_template, request

# =====================================================================
# 1. ИНСТРУМЕНТЫ (ПОДДЕРЖКА ВСЕХ БУКВ ДО NO)
# =====================================================================
def parse_game_number(text_value):
    text_value = str(text_value).strip().upper()
    multipliers = {
        'K': 10**3, 'M': 10**6, 'B': 10**9, 'T': 10**12, 
        'QA': 10**15, 'QI': 10**18, 'SX': 10**21, 'SP': 10**24, 
        'OC': 10**27, 'NO': 10**30
    }
    for letter, multiplier in multipliers.items():
        if text_value.endswith(letter):
            number_part = text_value.replace(letter, '')
            return int(float(number_part) * multiplier)
    return int(float(text_value))

def format_game_number(number):
    # Исправили строку 20: перенесли return на новую строчку
    if number < 1000:
        return str(number)
    
    suffixes = [
        ('NO', 10**30), ('OC', 10**27), ('SP', 10**24), ('SX', 10**21),
        ('QI', 10**18), ('QA', 10**15), ('T', 10**12), ('B', 10**9), 
        ('M', 10**6), ('K', 10**3)
    ]
    
    for suffix, value in suffixes:
        if number >= value:
            short_num = round(number / value, 2)
            # Исправили строку 29 (или около неё): тоже перенесли на новую строку
            if short_num.is_integer():
                return f"{int(short_num)}{suffix}"
            return f"{short_num}{suffix}"

# =====================================================================
# 2. ТВОИ ЛОКАЦИИ
# =====================================================================
LOCATIONS = {
    "Ninja Village": parse_game_number("50"),
    "Namek City": parse_game_number("3.5K"),
    "Wano Island": parse_game_number("285K"),
    "Titan Wall": parse_game_number("21.5M"),
    "Solo City": parse_game_number("2B"),
    "Slayer Village": parse_game_number("250B"),
    "Clover Island": parse_game_number("175T"),
    "Summer Art Online": parse_game_number("25QA")
}

app = Flask(__name__)

# =====================================================================
# 3. ЛОГИКА САЙТА
# =====================================================================
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        location_name = request.form.get("location")
        eggs_at_once_text = request.form.get("eggs_at_once", "1")
        has_gamepass = "gamepass" in request.form
        hours_text = request.form.get("hours", "1")
        
        egg_price = LOCATIONS.get(location_name, 0)
        eggs_at_once = parse_game_number(eggs_at_once_text)
        hours = parse_game_number(hours_text)
        
        # Скорость по image_1ae931.png
        open_speed_per_minute = 36 if has_gamepass else 18
        
        total_eggs = (hours * 60 * open_speed_per_minute) * eggs_at_once
        total_cost = total_eggs * egg_price
        
        result = {
            "location": location_name,
            "egg_price": format_game_number(egg_price),
            "total_eggs": format_game_number(total_eggs),
            "total_cost": format_game_number(total_cost),
            # Передаем введенные игроком данные обратно для сохранения в полях:
            "user_eggs_at_once": eggs_at_once_text,
            "user_hours": hours_text,
            "has_gamepass": has_gamepass
        }
        
    return render_template("index.html", locations=LOCATIONS.keys(), result=result)

if __name__ == "__main__":
    app.run(debug=True)