from tkinter import *
from tkinter import messagebox
# import requests
import json
import re
from weather_api import WeatherService
from send_alert import AlertSender
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WeatherNotifierGUI:
    def __init__(self):
        """
        Initializes the Weather Notifier GUI, sets up the main window, and initializes
        weather and alert services.
        """
        # Create and configure main window
        self.window = Tk()
        self.window.title("Automated severe weather condition notifier")
        self.window.config(padx=20, pady=20)  # the padding around the sides
        self.window.geometry("700x200")  #how big the screen will be
        
        # Initialize services for weather data and alerts
        self.weather_service = WeatherService(os.getenv('OPENWEATHER_API_KEY'))
        self.alert_sender = AlertSender()
        
        # Make the window responsive
        self.window.columnconfigure(1, weight=1)
        

        
        # Initialize GUI elements
        self.create_labels()
        self.create_entries()
        self.create_button()
        
    def create_labels(self):
        """Create and position all labels in the GUI"""
        # Create and position city label
        self.city_label = Label(self.window, text="City name:")
        self.city_label.grid(column=0, row=0, sticky=W, padx=10, pady=10)
        
        # Create and position phone number label
        self.phone_number_label = Label(self.window, text="Phone number:")
        self.phone_number_label.grid(column=0, row=1, sticky=W, padx=10, pady=10)
        
        # Create and position email label
        self.email_label = Label(self.window, text="Email:")
        self.email_label.grid(column=0, row=2, sticky=W, padx=10, pady=10)
        
    def create_entries(self):
        """Create and position all input fields in the GUI"""
        # Create and position city input field
        self.city_entry = Entry(self.window, width=80)
        self.city_entry.grid(column=1, row=0, sticky="ew", padx=10, pady=10)
        self.city_entry.focus()  # Set focus to city entry by default
        
        # Create and position phone number input field
        self.phone_number_entry = Entry(self.window, width=80)
        self.phone_number_entry.grid(column=1, row=1, sticky="ew", padx=10, pady=10)
        
        # Create and position email input field
        self.email_entry = Entry(self.window, width=80)
        self.email_entry.grid(column=1, row=2, sticky="ew", padx=10, pady=10)
        
    def create_button(self):
     #Create and place the buttons for testing notification and saving user data.
        # Test Notification Button
        self.testing_button = Button(
            self.window, 
            text="Test notification", 
            bg="light green", 
            command=self.test_notification
        )
        self.testing_button.grid(column=0, row=4, sticky="ew", padx=10, pady=10)

        # Save user data button
        self.save_button = Button(
            self.window,
            text="Save user data",
            bg="light blue",
            command=self.save_button_clicked
        )
        self.save_button.grid(column=1, row=4, sticky="ew", padx=10, pady=10)

    def validate_input(self, city, phone, email):
        """
        Validate the user input for city, phone number, and email.
        Returns:
            tuple: (True, "") if valid; (False, error_message) if invalid.
        """
        # Check if all fields are filled
        if not all([city, phone, email]):
            return False, "Please fill in all fields"
        
        # Basic phone number validation (international)
        if not re.match(r"^\+?\d{10,15}$", phone):
            return False, "Invalid phone number format"

        # Basic email format validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format"

        return True, ""
    
    def save_user_data(self, city, phone, email):
        """
        Save the user input data to a JSON file.

        Args:
            city (str): City name.
            phone (str): Phone number.
            email (str): Email address.
        """
        # Create user data dictionary
        user_info = {"city": city, "phone": phone, "email": email}
        
        try:
            # Read existing data if file exists
            if os.path.exists("users.json"):
                with open("users.json", "r") as user_data:
                    data = json.load(user_data)
            else:
                data = []

            # Append new user data and save to file
            data.append(user_info)
            with open("users.json", "w") as  user_data:
                json.dump(data,  user_data, indent=4)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def save_button_clicked(self):
        """
        Callback for "Save user data" button. Validates inputs and saves user data.
        """
        city = self.city_entry.get().strip()
        phone = self.phone_number_entry.get()
        email = self.email_entry.get()

        valid, msg = self.validate_input(city, phone, email)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        self.save_user_data(city, phone, email)
        messagebox.showinfo("Success", "User data saved successfully.")


    def test_notification(self):
        """
        This function is used to test the notification system.
        It will send a test notification to the phone and email of the user.
        """
        # Get values from entries
        city = self.city_entry.get()
        phone = self.phone_number_entry.get()
        email = self.email_entry.get()
        
        valid, msg = self.validate_input(city, phone, email)
        # Check if all fields are filled
        if not all([city, phone, email]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            # Get weather data using city name
            # The * operator unpacks the (lat, lon) tuple returned by get_coordinates into separate arguments
            # So fetch_weather_data(*get_coordinates(city)) is equivalent to:
            # lat, lon = get_coordinates(city)
            # fetch_weather_data(lat, lon)
            raw_data = self.weather_service.fetch_weather_data(*self.weather_service.get_coordinates(city))
            if not raw_data:
                messagebox.showerror("Error", "Could not fetch weather data")
                return
                
            relevant_data = self.weather_service.extract_relevant_data(raw_data)
            if not relevant_data:
                messagebox.showerror("Error", "Could not extract weather data")
                return
            
            # Get current weather information
            current = relevant_data['current']
            temperature = raw_data['current']['temp']
            weather_description = current['description']
            
            # Create detailed message for GUI display
            gui_message = f"Location Details:\n" \
                         f"City: {city}\n" \
                         f"Notification will be sent to:\n" \
                         f"Phone: {phone}\n" \
                         f"Email: {email}\n\n" \
                         f"Current Weather:\n" \
                         f"Temperature: {temperature}°C\n" \
                         f"Weather: {weather_description}"
            
            # Create simplified message for SMS and email
            notification_message = f"Weather Alert for {city}:\n" \
                                 f"Temperature: {temperature}°C\n" \
                                 f"Weather: {weather_description}"
            
            # Show detailed information in GUI
            messagebox.showinfo("Weather Test", gui_message)
            
            # Send notification
            alert_type, response = self.alert_sender.send_alert(phone, email, notification_message)
            
            # Show notification status
            status_message = f"Notification Status:\nType: {alert_type}\nResponse: {response}"
            messagebox.showinfo("Notification Status", status_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def run(self):
        """Start the GUI application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = WeatherNotifierGUI()
    app.run()