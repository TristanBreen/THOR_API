# restart server command: sudo systemctl restart flask.service

import os
import csv
from datetime import datetime, date
import requests
import random
import google.generativeai as genai
from config import GEMINI_API_KEY
from flask import Flask, request, jsonify
from emailSeizureLogs import send_seizure_email

app = Flask(__name__)

# Resolve CSV file paths: check server absolute path first, then local Data folder
SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for server path first
if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data", "seizures.csv")):
    SEIZURE_FILE = os.path.join(SERVER_BASE_PATH, "Data", "seizures.csv")
else:
    SEIZURE_FILE = os.path.join(APP_DIR, "Data", "seizures.csv")

if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data", "pain.csv")):
    PAIN_FILE = os.path.join(SERVER_BASE_PATH, "Data", "pain.csv")
else:
    PAIN_FILE = os.path.join(APP_DIR, "Data", "pain.csv")

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
    """
    Fetches a fun fact using the Gemini API.
    
    Returns:
        str: A fun fact (or error message if the API fails).
    """

    topics = [
        "space", "animals", "technology", "history", "geography",
        "food", "movies", "music", "sports", "science",
        "oceans", "plants", "art", "literature", "physics",
        "math", "weather", "architecture", "inventions", "human body",
        "dinosaurs", "programming", "robots", "philosophy", "travel"
    ]
    
    topic = random.choice(topics)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"Tell me a very short, interesting fun fact about {topic}. Keep it under 20 words."
        response = model.generate_content(prompt)

        return "Did you know that " + response.text.strip()

    except Exception as e:
        return f"Failed to fetch a fun fact. Error: {str(e)}"

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
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(SEIZURE_FILE), exist_ok=True)
    
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
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(PAIN_FILE), exist_ok=True)
    
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
    pain = request.args.get("pain", type=int)

    if pain is None or not isinstance(pain, int):
        return jsonify({"error": "Please provide pain number of scale from 1 - 10"}), 400

    message = trackPain(pain)

    return jsonify({"message": message})

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": f"Internal server error. {str(error)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
