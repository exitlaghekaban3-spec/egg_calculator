from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'anime-astral-egg-calculator-secret-key'

# Extended suffixes to match your rank calculator
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

# English locations setup
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

# Generate location list with prices for the select menu
LOCATION_OPTIONS = [(loc, f"{loc} ({format_game_number(price)})") for loc, price in LOCATIONS.items()]

def format_time(seconds):
    if seconds <= 0:
        return "0s"
    minutes = seconds // 60
    remaining_seconds = int(seconds % 60)
    hours = minutes // 60
    remaining_minutes = int(minutes % 60)
    days = hours // 24
    remaining_hours = int(hours % 24)
    
    parts = []
    if days > 0: parts.append(f"{int(days)}d")
    if hours > 0: parts.append(f"{remaining_hours}h")
    if minutes > 0: parts.append(f"{remaining_minutes}m")
    if remaining_seconds > 0 or not parts: parts.append(f"{remaining_seconds}s")
    return " ".join(parts)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_loc = request.form.get("location")
        money_raw = request.form.get("money", "0").replace(',', '.')
        selected_suffix = request.form.get("money_suffix", "")
        hatch_mode = request.form.get("hatch_mode", "1") # 1 egg or 18 eggs
        
        try:
            base_money = float(money_raw)
        except ValueError:
            base_money = 0.0
            
        money_suffix_value = SUFFIXES.get(selected_suffix, 1)
        total_user_money = base_money * money_suffix_value
        
        # Base price for 1 single egg opening
        base_egg_cost = LOCATIONS.get(selected_loc, 0.0)
        
        if hatch_mode == "18":
            # 18 eggs hatch mode uses 1 SX per 30 mins (1800s) on the last location (75SX base)
            # This perfectly scales the speed across all locations
            eggs_per_second = 1.0  
            cost_per_second = (base_egg_cost / 75.0) * (1_000_000_000_000_000_000_000 / 1800.0)
        else:
            # Standard single hatch mode (1 egg)
            eggs_per_second = 1.0
            cost_per_second = base_egg_cost * eggs_per_second

        if cost_per_second > 0 and total_user_money > 0:
            time_seconds = total_user_money / cost_per_second
            time_formatted = format_time(time_seconds)
            total_eggs_can_hatch = int(time_seconds * eggs_per_second * (18 if hatch_mode == "18" else 1))
        else:
            time_formatted = "0s (No money or cost)"
            total_eggs_can_hatch = 0
            
        session["egg_calc_data"] = {
            "result": {
                "location": selected_loc,
                "money_spent": format_game_number(total_user_money),
                "time_duration": time_formatted,
                "total_eggs": f"{total_eggs_can_hatch:,}"
            },
            "inputs": {
                "money": money_raw,
                "money_suffix": selected_suffix,
                "location": selected_loc,
                "hatch_mode": hatch_mode
            }
        }
        return redirect(url_for("index"))
        
    data = session.pop("egg_calc_data", None)
    result = data.get("result") if data else None
    inputs = data.get("inputs") if data else {
        "money": "", "money_suffix": "", "location": "Fire City (Last)", "hatch_mode": "1"
    }
    
    return render_template("index.html", suffixes=SUFFIXES.keys(), locations_options=LOCATION_OPTIONS, result=result, inputs=inputs)

if __name__ == "__main__":
    app.run(debug=True)