# restart server command: sudo systemctl restart flask.service

import os
import csv
from datetime import datetime, date
import requests
import random
import google.generativeai as genai
from flask import Flask, request, jsonify
from io import StringIO

# Try to import config, but make it optional for startup
try:
    from config import GEMINI_API_KEY
except ImportError:
    print("Warning: config.py not found. GEMINI_API_KEY will need to be set via environment variable.")
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

try:
    from emailSeizureLogs import send_seizure_email
except ImportError:
    print("Warning: emailSeizureLogs.py not found. Email functionality will be disabled.")
    def send_seizure_email(file_path):
        print(f"Email disabled - would have sent file: {file_path}")

app = Flask(__name__)

# Resolve CSV file paths: check server absolute path first, then local Data folder
SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine which base path to use
if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
    BASE_DATA_DIR = os.path.join(SERVER_BASE_PATH, "Data")
else:
    BASE_DATA_DIR = os.path.join(APP_DIR, "Data")

# Ensure Data directory exists
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# Set file paths
SEIZURE_FILE = os.path.join(BASE_DATA_DIR, "seizures.csv")
PAIN_FILE = os.path.join(BASE_DATA_DIR, "pain.csv")
APPLE_WATCH_FILE = os.path.join(BASE_DATA_DIR, "appleWatchData.csv")
PREDICTION_FILE = os.path.join(BASE_DATA_DIR, "prediction.txt")

def getGoodMorningString():
    messages = [
        "Good morning! Rise and shine! ",
        "Top of the morning to you! ",
        "Hello sunshine! Wishing you a bright day ahead! ",
        "Wakey wakey, eggs and bakey! ",
        "Good morning! Today is a fresh start. ",
        "Rise and grind—it’s a brand-new day! ",
        "Morning! Let’s make today amazing. ",
        "Good morning! Hope you slept like a baby. ",
        "Greetings! The world missed you today. ",
        "Good morning! Don’t forget to smile. ",
        "Hello there! Today’s goals: Be awesome. ",
        "Wake up and be awesome! You’ve got this. ",
        "Good morning! Sending you positive vibes. ",
        "Rise and shine, it’s coffee time! ",
        "Morning! Let’s conquer the day. ",
        "Good morning! Today’s forecast: 100% chance of greatness. ",
        "Hello, early bird! Catch that worm! ",
        "Good morning! The best is yet to come. ",
        "Wake up and inspire someone today. ",
        "Morning vibes only. Let’s go! ",
        "Good morning! Today is your canvas—paint it well. ",
        "Rise, shine, and repeat! ",
        "Hello! Today’s mantra: Stay positive. ",
        "Good morning! Smile—it’s contagious. ",
        "Wake up and slay the day! "
    ]
    return random.choice(messages)

def getWeatherString(lat, lon):
    try:
        # Get all URLs in one call
        pointsResponse = requests.get(
            f"https://api.weather.gov/points/{lat},{lon}",
            headers={"User-Agent": "WeatherApp/1.0"},
            timeout=10
        )
        pointsResponse.raise_for_status()
        urls = pointsResponse.json()["properties"]

        currentTemp = requests.get(urls["forecastHourly"]).json()["properties"]["periods"][0]
        dailyForecast = requests.get(urls["forecast"]).json()["properties"]["periods"]

        highTemp = next((p["temperature"] for p in dailyForecast if p["isDaytime"]), None)

        if highTemp:
            return f"Currently it is {currentTemp['temperature']} degrees with a high of {highTemp} degrees. "

    except Exception:
        return "Error: Unable to retrieve weather data. Error: {str(e)}"

def getFunFact():
   #"""
   #Fetches a fun fact using the Gemini API.
   #
   #Returns:
   #    str: A fun fact (or error message if the API fails).
   #"""

   #topics = [
   #    "space", "animals", "technology", "history", "geography",
   #    "food", "movies", "music", "sports", "science",
   #    "oceans", "plants", "art", "literature", "physics",
   #    "math", "weather", "architecture", "inventions", "human body",
   #    "dinosaurs", "programming", "robots", "philosophy", "travel"
   #]
   #
   #topic = random.choice(topics)

   #try:
   #    genai.configure(api_key=GEMINI_API_KEY)
   #    model = genai.GenerativeModel("gemini-2.5-flash")

   #    prompt = f"Tell me a very short, interesting fun fact about {topic}. Keep it under 20 words."
   #    response = model.generate_content(prompt)

   #    return "Did you know that " + response.text.strip()

   #except Exception as e:
   #    return f"Failed to fetch a fun fact. Error: {str(e)}"

    messages = [
        "Honey never spoils; edible honey has been found in ancient Egyptian tombs.",
        "Octopuses have three hearts.",
        "You are actually slightly taller in the morning than at night.",
        "Bananas are berries, but strawberries aren't.",
        "A day on Venus is longer than a year on Venus.",
        "Cows have best friends and get stressed when they are separated.",
        "The Eiffel Tower can grow 15 cm taller during the summer due to thermal expansion.",
        "A group of flamingos is called a 'flamboyance'.",
        "Sea otters hold hands when they sleep to keep from drifting apart.",
        "It is physically impossible for pigs to look up into the sky.",
        "Australia is wider than the moon.",
        "The unicorn is the national animal of Scotland.",
        "Humans share 60% of their DNA with bananas.",
        "There are more stars in the universe than grains of sand on all the Earth's beaches.",
        "A cloud can weigh more than a million pounds.",
        "Wombat poop is cube-shaped.",
        "The shortest war in history lasted only 38 minutes.",
        "Sloths can hold their breath longer than dolphins can.",
        "Butterflies taste with their feet.",
        "The total weight of all ants on Earth is about the same as the weight of all humans.",
        "An ostrich's eye is bigger than its brain.",
        "Venus consists of no moons.",
        "Elephants are the only mammals that cannot jump.",
        "Hot water turns into ice faster than cold water (the Mpemba effect).",
        "A snail can sleep for three years.",
        "The word 'stewardesses' is the longest word typed with only the left hand.",
        "The moon has moonquakes.",
        "A blue whale's heart is the size of a small car.",
        "Goats have rectangular pupils.",
        "The longest wedding veil was longer than 63 football fields.",
        "Tigers have striped skin, not just striped fur.",
        "A 'jiffy' is an actual unit of time: 1/100th of a second.",
        "Some cats are allergic to humans.",
        "Your nose and ears never stop growing.",
        "Space smells like seared steak.",
        "There is a species of jellyfish that is biologically immortal.",
        "The inventor of the Pringles can is buried in one.",
        "High heels were originally invented for men.",
        "It takes 8 minutes and 20 seconds for light to travel from the Sun to Earth.",
        "Sharks have been around longer than trees.",
        "Peanuts are not nuts; they are legumes.",
        "The wood frog can hold its pee for up to eight months.",
        "The letter 'Q' is the only letter that doesn't appear in any US state name.",
        "Armadillos are bulletproof.",
        "Most toilets flush in E flat.",
        "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
        "Apples float because they are 25% air.",
        "Firefighters use wetting agents to make water wetter.",
        "Kangaroos cannot walk backward.",
        "A rhinoceros' horn is made of hair (keratin).",
        "The Spanish national anthem has no words.",
        "Human teeth are the only part of the body that cannot heal themselves.",
        "There are more fake flamingos in the world than real ones.",
        "A shrimp's heart is in its head.",
        "Cap'n Crunch's full name is Horatio Magellan Crunch.",
        "The world's smallest reptile fits on a fingertip.",
        "In Switzerland, it is illegal to own just one guinea pig.",
        "Ketchup was once sold as medicine.",
        "The dot over the letter 'i' is called a tittle.",
        "It is impossible to hum while holding your nose.",
        "Oxford University is older than the Aztec Empire.",
        "Bubble wrap was originally invented as wallpaper.",
        "A crocodile cannot stick its tongue out.",
        "There are 293 ways to make change for a dollar.",
        "The average person walks the equivalent of five times around the world in a lifetime.",
        "Owls don't have eyeballs; they have eye tubes.",
        "The hashtag symbol is technically called an octothorpe.",
        "Polar bear skin is black, and their fur is clear.",
        "A bolt of lightning is five times hotter than the surface of the sun.",
        "Chewing gum is banned in Singapore.",
        "Koala fingerprints are so similar to humans they have confused crime scene investigators.",
        "Russia has a larger surface area than Pluto.",
        "You can't tickle yourself.",
        "A baby octopus is about the size of a flea when it is born.",
        "France covers the most time zones of any country (12).",
        "Hippopotamus milk is pink.",
        "The Komodo dragon is the largest lizard.",
        "There is a town in Norway called 'Hell'.",
        "The smell of freshly cut grass is actually a plant distress call.",
        "Lobsters taste with their feet.",
        "A hummingbird weighs less than a penny.",
        "The longest English word is 189,819 letters long.",
        "New York City drifts about one inch farther away from Europe every year.",
        "Your tongue print is as unique as your fingerprint.",
        "Alaska is the only state that can be typed on one row of a keyboard.",
        "The electric chair was invented by a dentist.",
        "Birds don't urinate.",
        "Only 5% of the ocean has been explored.",
        "Before erasers were invented, people used bread crumbs to erase graphite.",
        "A day on Mercury lasts approximately 1,408 hours.",
        "The heart of a shrimp is located in its head.",
        "All odd numbers have the letter 'e' in them.",
        "Sea lions have rhythm and can clap to a beat.",
        "The tiny pocket in jeans was designed for pocket watches.",
        "Astronauts can grow up to two inches in space.",
        "A group of pugs is called a grumble.",
        "Cotton candy was invented by a dentist.",
        "The average cloud moves at 30 mph.",
        "There is a planet made of diamonds called 55 Cancri e.",
        "Bananas are curved because they grow towards the sun."
    ]

    return random.choice(messages)

def concatMessages(lat, lon):
    goodMorning = getGoodMorningString()
    weather = getWeatherString(lat, lon)
    funFact = getFunFact()

    return goodMorning + weather + funFact

def trackSeizure(duration, period, eaten, foodEaten = ""):
    period = period == "Yes"
    eaten = eaten == "Yes"

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    # Ensure directory exists (already created at startup, but double-check)
    os.makedirs(BASE_DATA_DIR, exist_ok=True)
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(SEIZURE_FILE):
        with open(SEIZURE_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Time', 'Duration', 'Period', 'Eaten', 'FoodEaten'])
    
    with open(SEIZURE_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, time, duration, period, eaten, foodEaten])

    print(f"[LOG] Seizure logged to {SEIZURE_FILE}")
    return f"Seizure for {duration} seconds has been logged"

def trackPain(pain):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    # Ensure directory exists (already created at startup, but double-check)
    os.makedirs(BASE_DATA_DIR, exist_ok=True)
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(PAIN_FILE):
        with open(PAIN_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Time', 'Pain'])
    
    with open(PAIN_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, time, pain])

    print(f"[LOG] Pain logged to {PAIN_FILE}")
    return f"Pain has been logged"

def trackAppleWatchData(uploaded_file):
    """
    Appends data from uploaded Apple Watch CSV export to appleWatchData.csv
    
    Args:
        uploaded_file: Flask file upload object containing the CSV file
        
    Returns:
        str: Success message with number of rows appended
    """
    # Ensure directory exists (already created at startup, but double-check)
    os.makedirs(BASE_DATA_DIR, exist_ok=True)
    
    # Read the uploaded CSV file content
    file_content = uploaded_file.read().decode('utf-8')
    uploaded_csv = csv.reader(file_content.splitlines())
    rows = list(uploaded_csv)
    
    if not rows:
        return "Error: Uploaded file is empty"
    
    # Get header row from uploaded file
    header_row = rows[0]
    
    # Check if appleWatchData.csv exists, create with header if not
    file_exists = os.path.exists(APPLE_WATCH_FILE)
    
    if not file_exists:
        with open(APPLE_WATCH_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header_row)
    
    # Append data rows (skip header row from uploaded file)
    data_rows = rows[1:]
    rows_appended = 0
    
    with open(APPLE_WATCH_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        for row in data_rows:
            writer.writerow(row)
            rows_appended += 1
    
    print(f"[LOG] Apple Watch data logged to {APPLE_WATCH_FILE} - {rows_appended} rows appended")
    return f"Apple Watch data has been logged - {rows_appended} rows appended"

def main(lat, lon):
    return concatMessages(lat, lon)

@app.route("/goodmorning", methods=["GET"])
def goodmorning():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Please provide 'lat' and 'lon' query parameters."}), 400

    message = main(lat, lon)
    return jsonify({"message": message})

@app.route("/seizure", methods=["GET"])
def trackseizure():
    duration = request.args.get("duration", type=int)
    period = request.args.get("period", type=str)
    eaten = request.args.get("eaten", type=str)
    foodEaten = request.args.get("foodEaten", type=str)

    if duration is None or not isinstance(duration, int):
        return jsonify({"error": "Please provide duration as a number in seconds"}), 400

    if period is None or not isinstance(period, str):
        return jsonify({"error": "Please provide period as 'Yes' or 'No'."}), 400

    if eaten is None or not isinstance(eaten, str):
        return jsonify({"error": "Please provide eaten as 'Yes' or 'No'."}), 400

    if eaten == "No":
        message = trackSeizure(duration, period, eaten)
    else:
        message = trackSeizure(duration, period, eaten, foodEaten)

    send_seizure_email(file_path=SEIZURE_FILE)

    return jsonify({"message": message})

@app.route("/pain", methods=["GET"])
def trackpain():
    pain = request.args.get("pain", type=float)

    if pain is None:
        return jsonify({"error": "Please provide pain as a number (float) on a scale from 1.0 - 10.0"}), 400

    if not (1.0 <= pain <= 10.0):
        return jsonify({"error": "Please provide pain in the range 1.0 - 10.0"}), 400

    message = trackPain(pain)

    return jsonify({"message": message})

def append_csv_data(csv_content):
    """
    Appends CSV data to appleWatchData.csv
    
    Args:
        csv_content (str): Raw CSV content as string
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Parse the CSV content
        csv_file = StringIO(csv_content)
        reader = csv.reader(csv_file)
        rows = list(reader)
        
        if not rows:
            return {"success": False, "message": "CSV file is empty"}
        
        # First row is the header
        header_row = rows[0]
        data_rows = rows[1:]
        
        if not data_rows:
            return {"success": False, "message": "No data rows found (only header)"}
        
        # Check if target file exists
        file_exists = os.path.exists(APPLE_WATCH_FILE)
        
        # If file doesn't exist, create it with the header
        if not file_exists:
            with open(APPLE_WATCH_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header_row)
        
        # Append data rows
        with open(APPLE_WATCH_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data_rows)
        
        rows_appended = len(data_rows)
        print(f"[LOG] Appended {rows_appended} rows to {APPLE_WATCH_FILE}")
        
        return {
            "success": True,
            "message": f"Successfully appended {rows_appended} rows",
            "rows_appended": rows_appended
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to process CSV: {str(e)}")
        return {"success": False, "message": f"Error processing CSV: {str(e)}"}


@app.route("/applewatch", methods=["POST"])
def track_apple_watch():
    """
    Endpoint to receive Apple Watch health data CSV from iOS Shortcuts
    Accepts raw CSV content in request body OR multipart file upload
    """
    try:
        # Check if it's a file upload (multipart form data)
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename == '' or not uploaded_file.filename.endswith('.csv'):
                return jsonify({
                    "success": False,
                    "error": "Invalid CSV file"
                }), 400
            csv_content = uploaded_file.read().decode('utf-8')
        
        # Otherwise, get raw body content
        else:
            csv_content = request.get_data(as_text=True)
            
            if not csv_content or not csv_content.strip():
                return jsonify({
                    "success": False,
                    "error": "Request body is empty. Please send CSV content in the request body or as a file upload."
                }), 400
        
        # Process the CSV data
        result = append_csv_data(csv_content)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify({"success": False, "error": result["message"]}), 400
            
    except Exception as e:
        print(f"[ERROR] Endpoint error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/nextseizure", methods=["GET"])
def getnextseizure():
    try:
        with open(SEIZURE_FILE, 'r') as file:
            lines = file.readlines()
            if not lines:
                return jsonify({"error": "No seizure data found"}), 404

            lastDateStr = lines[-1].strip().split(",")[0]
            lastDate = datetime.strptime(lastDateStr, "%Y-%m-%d").date()

        nextSeizure = 14 - (date.today() - lastDate).days

        if nextSeizure < 0:
            return jsonify({"message": f"Next seizure should have been {abs(nextSeizure)} days ago."})
        elif nextSeizure > 0:
            return jsonify({"message": f"Next seizure should be in {nextSeizure} days."})
        else:
            return jsonify({"message": "Next seizure should be today."})

    except FileNotFoundError:
        return jsonify({"error": f"File not found: {SEIZURE_FILE}"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to read file. Error: {str(e)}"}), 500

@app.route("/prediction", methods=["GET"])
def getprediction():
    """
    Returns the current seizure prediction from prediction.txt
    """
    try:
        if not os.path.exists(PREDICTION_FILE):
            return jsonify({"error": "Prediction file not found"}), 404
        
        with open(PREDICTION_FILE, 'r', encoding='utf-8') as file:
            prediction_text = file.read().strip()
        
        if not prediction_text:
            return jsonify({"error": "Prediction file is empty"}), 404
        
        return jsonify({"prediction": prediction_text}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to read prediction file. Error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": f"Internal server error. {str(error)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
