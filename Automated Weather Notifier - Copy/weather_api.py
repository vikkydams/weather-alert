import requests
import datetime
import time
# Imported the request module/library which allows us to send HTTP requests to get data from the internet
# Imported the datetime module that handles date and time-related operations
# Handles time-related functions, delays and system time

class WeatherService:
    """Weather service class to monitor severe weather conditions and run continuous checks"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.geo_api_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.onecall_api_url = "https://api.openweathermap.org/data/3.0/onecall"

    def _make_api_request(self, url, params):
        """Private method to make API requests with error handling, exceptions like httpError, ConnectionError etc."""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except ValueError as e:
            print(f"JSON decode error: {e}")
            return None

    def get_coordinates(self, city_name):
        """This method takes city name and returns the latitude and longitude using the geocoding API"""
        params = {
            "q": city_name,  # This is the query string, so it automatically passes in the city name
            # such as after the geo url an equal sign is passed like this ={city_name}&limit
            "limit": 1,
            "appid": self.api_key
        }
        data = self._make_api_request(self.geo_api_url, params)
        return (data[0]["lat"], data[0]["lon"]) if data else (None, None)

    def fetch_weather_data(self, latitude, longitude):
        """This is a method that takes the data lat and lon as arguments and passes it into latitude and longitude and uses this to
        fetch raw weather data from the One call API for the given coordinates."""
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric",
            "exclude": "minutely"
        }
        return self._make_api_request(self.onecall_api_url, params)
    

    # TO EXTRACT DATA FOR CHECKS AND ANALYSIS
    def extract_relevant_data(self, raw_data):
        """Extracts the relevant weather details for current weather and for the next 12 hours.
        It returns a dictionary with the weather condition IDs and descriptions."""
        try:
            current = raw_data['current']['weather'][0]
            next_12_hours = [hour['weather'][0] for hour in raw_data['hourly'][:12]]
            return {
                'current': current,
                'next_12_hours': next_12_hours
            }
        except (KeyError, IndexError) as e:
            print(f"Error extracting weather data: {e}")
            return None

    def check_severity(self, weather_id):
        """Check if weather condition is severe"""
                # Severe weather categories samples
                # self.severe_weather_categories = {
                #     (200 - 232): "Thunderstorm",
                #     (500 - 531): "Heavy Rain",
                #     (600 - 622): "Snow",
                #     (700 - 781): "Atmospheric Hazard",
                #     (900 - 906): "Extreme Weather",  # Additional extreme conditions
                #     (957 - 962): "Strong Winds"  # High wind conditions
                # }
        try:
            id_code = int(weather_id)
            if 200 <= id_code <= 232: return True, "Thunderstorm"
            elif 500 <= id_code <= 531: return True, "Rain"
            elif 600 <= id_code <= 622: return True, "Snow"
            elif 700 <= id_code <= 781: return True, "Atmospheric Condition"
            elif 900 <= id_code <= 906: return True, "Extreme Weather"
            return False, "Clear or Mild"
        except (ValueError, TypeError):
            return False, "Unknown"

    def check_weather(self, city_name, check_future=True):
        """Check current and future weather conditions, now using all the methods created so far"""
        lat, lon = self.get_coordinates(city_name)
        if not lat or not lon:
            print("Could not get coordinates")
            return

        raw_data = self.fetch_weather_data(lat, lon)
        if not raw_data:
            print("Could not fetch weather data")
            return

        relevant_data = self.extract_relevant_data(raw_data)
        if not relevant_data:
            print("Could not extract weather data")
            return

        # Check current weather
        current = relevant_data['current']
        is_severe, category = self.check_severity(current['id'])
        if is_severe:
            print(f"Severe weather alert for {city_name}! ({category} - {current['description']})")
            return

        # Check future weather if requested
        if check_future:
            for hour in relevant_data['next_12_hours']:
                is_severe, category = self.check_severity(hour['id'])
                if is_severe:
                    print(f"Severe weather expected in next 12 hours for {city_name}! ({category} - {hour['description']})")
                    return

        print(f"No severe weather detected for {city_name} at {datetime.datetime.now()}")

    def run_continuous_monitoring(self, city_name):
        """Run continuous weather monitoring every 30 minutes"""
        print(f"Starting continuous weather monitoring for {city_name}")
        print("Checking every 30 minutes...")

        while True:
            try:
                now = datetime.datetime.now()
                print(f"\n--- Weather Check at {now} ---")
                 
                if now.hour == 5 and now.minute < 30:#depending on when the program starts it may never hit exactly 5:00
                    self.check_weather(city_name, check_future=True)  # 5 AM: check future 12 hours
                else:
                    self.check_weather(city_name, check_future=False)  # Otherwise: just current weather
                    # Calculate sleep time until the next 30-minute mark
                minutes = now.minute
                if minutes < 30:
                    minutes_to_sleep = 30 - minutes
                else:
                    minutes_to_sleep = 60 - minutes
                sleep_seconds = minutes_to_sleep * 60 - now.second

                print(f"Next check in {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user.")
                break

# Example usage
#Only run the code inside this block if this file is executed directly.
if __name__ == "__main__":
    API_KEY = "a144d5975f92d6c6159157ffd02f10bb"
    CITY_NAME = "Abuja"

    weather_service = WeatherService(API_KEY)
    weather_service.run_continuous_monitoring(CITY_NAME) 