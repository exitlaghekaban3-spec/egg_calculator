from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'anime-astral-egg-calculator-secret-key'

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
    if not val_str:
        return 0.0
    val_str = str(val_str).strip().upper().replace(',', '.')
    sorted_suffixes = sorted(SUFFIXES.items(), key=lambda x: len(x[0]), reverse=True)
    for suffix, multiplier in sorted_suffixes:
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
    if num == 0:
        return "0"
    abs_num = abs(num)
    for suffix, multiplier in sorted(SUFFIXES.items(), key=lambda x: x[1], reverse=True):
        if abs_num >= multiplier:
            formatted = f"{num / multiplier:.2f}".rstrip('0').rstrip('.')
            return f"{formatted}{suffix}"
    return f"{num:.2f}".rstrip('0').rstrip('.')

LOCATIONS = {
    "Ninja Village": parse_game_number("50"),
    "Namek City": parse_game_number("3.5K"),
    "Wano Island": parse_game_number("285K"),
    "Titan Wall": parse_game_number("21.5M"),
    "Solo City": parse_game_number("2B"),
    "Slayer Village": parse_game_number("250B"),
    "Clover Island": parse_game_number("175T"),
    "Summer Art Online": parse_game_number("25QA"),
    "Fire City (Last)": parse_game_number("75SX")
}

LOCATION_OPTIONS = [(loc, f"{loc} ({format_game_number(price)})") for loc, price in LOCATIONS.items()]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_loc = request.form.get("location")
        hours_raw = request.form.get("hours", "1").replace(',', '.')
        pets_per_open_raw = request.form.get("pets_per_open", "1")
        has_fast_open = request.form.get("fast_open") == "yes"
        
        try:
            hours = float(hours_raw)
        except ValueError:
            hours = 1.0
            
        try:
            pets_per_open = int(pets_per_open_raw)
        except ValueError:
            pets_per_open = 1
            
        # Переводим часы в секунды
        total_seconds = hours * 3600
        
        # Базовая цена одного яйца в выбранной локации
        single_egg_cost = LOCATIONS.get(selected_loc, 0.0)
        
        # Скорость открытий в секунду (Базовая vs Геймпас Fast Open)
        hatches_per_second = 1.25 if has_fast_open else 0.65
        
        # Считаем полную стоимость за одну секунду фарма
        cost_per_second = single_egg_cost * pets_per_open * hatches_per_second
        
        # Итоговый нужный бюджет
        required_money = cost_per_second * total_seconds
        total_eggs_to_open = int(hatches_per_second * pets_per_open * total_seconds)
        
        session["egg_calc_data"] = {
            "result": {
                "location": selected_loc,
                "hours": hours,
                "pets_per_open": pets_per_open,
                "fast_open": "Enabled" if has_fast_open else "Disabled",
                "total_eggs": f"{total_eggs_to_open:,}",
                "required_money": format_game_number(required_money)
            },
            "inputs": {
                "hours": hours_raw,
                "pets_per_open": pets_per_open_raw,
                "location": selected_loc,
                "fast_open": "yes" if has_fast_open else "no"
            }
        }
        return redirect(url_for("index"))
        
    data = session.pop("egg_calc_data", None)
    result = data.get("result") if data else None
    inputs = data.get("inputs") if data else {
        "hours": "1", "pets_per_open": "18", "location": "Fire City (Last)", "fast_open": "yes"
    }
    
    return render_template("index.html", locations_options=LOCATION_OPTIONS, result=result, inputs=inputs)

if __name__ == "__main__":
    app.run(debug=True)