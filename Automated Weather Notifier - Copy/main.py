# This file will be called by Windows Task Scheduler every 30 minutes
from weather_api import WeatherService
from send_alert import AlertSender
import os
import json
from dotenv import load_dotenv

def load_users_data():
    try:
        with open('users.json') as user_info:
            data = json.load(user_info)
        return data
    except Exception as e:
        print(f"Error loading user data JSON: {e}")
        return {}

def run_scheduled_check():
    """Function to be called by task scheduler every 30 minutes"""
    load_dotenv()  # Load environment variables (API keys, sender creds)
    
    # Load recipient info from JSON
    try:    
        all_user_data = load_users_data()
        
        for user_data in all_user_data:
            CITY = user_data.get('city', 'YourCity')
            PHONE = user_data.get('phone', '+1234567890')
            EMAIL = user_data.get('email', 'your@email.com')
    except Exception as e:
        print(f"Error loading or processing user data: {e}")
    
    # call your weather and alert functions here for each user

     # Load API key and sender info from .env
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not API_KEY:
        print("API key missing. Please check your .env file.")
        return

    try:
        weather_service = WeatherService(API_KEY)
        alert_sender = AlertSender()


        lat, lon = weather_service.get_coordinates(CITY)
        if not lat or not lon:
            print(f"[ERROR] Could not retrieve coordinates for {CITY}")
            return

        raw_data = weather_service.fetch_weather_data(lat, lon)
        if not raw_data:
            print("[ERROR] Weather data fetch failed.")
            return

        relevant_data = weather_service.extract_relevant_data(raw_data)
        if not relevant_data:
            print("[ERROR] Weather data extraction failed.")
            return

        # Check current weather
        current = relevant_data['current']
        is_severe, category = weather_service.check_severity(current['id'])
        if is_severe:
            message = f"Severe weather alert for {CITY}!\nType: {category}\nCondition: {current['description']}"
            method, response = alert_sender.send_alert(PHONE, EMAIL, message)
            print(f"[ALERT SENT via {method}]: {response}")
            return

        # Check next 12 hours
        for hour in relevant_data['next_12_hours']:
            is_severe, category = weather_service.check_severity(hour['id'])
            if is_severe:
                message = (f"Severe weather expected in the next 12 hours for {CITY}!\nType:"
                           f"{category}\nCondition: {hour['description']}")
                method, response = alert_sender.send_alert(PHONE, EMAIL, message)
                print(f"[FUTURE ALERT SENT via {method}]: {response}")
                return

        print(f"[INFO] No severe weather detected for {CITY}")

    except Exception as e:
        print(f"[ERROR] Error in scheduled check: {str(e)}")


if __name__ == "__main__":
    run_scheduled_check()
