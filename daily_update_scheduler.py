#!/usr/bin/env python3
"""
Tamil Nadu Transport Optimizer - Daily Update Scheduler
Automatically updates passenger demand predictions based on real-world factors

Author: Enhanced Transport System
Date: August 30, 2025
"""

import requests
import sqlite3
import json
import schedule
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
import random
import math
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transport_optimizer.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class WeatherData:
    temperature: float
    condition: str
    humidity: float
    rainfall: float
    wind_speed: float
    weather_factor: float

@dataclass
class FestivalData:
    is_festival: bool
    name: str
    impact_multiplier: float
    type: str  # major, regional, national

class TransportDataUpdater:
    
    def __init__(self, db_path='transport_optimizer.db'):
        self.db_path = db_path
        self.api_base_url = 'http://localhost:5000/api'
        
        # Tamil Nadu Festival Calendar
        self.festivals = {
            '2025-09-01': {'name': 'Vinayaka Chaturthi', 'multiplier': 1.6, 'type': 'major'},
            '2025-09-17': {'name': 'Onam', 'multiplier': 1.4, 'type': 'regional'},
            '2025-10-02': {'name': 'Gandhi Jayanti', 'multiplier': 1.3, 'type': 'national'},
            '2025-10-12': {'name': 'Vijaya Dashami', 'multiplier': 1.7, 'type': 'major'},
            '2025-11-01': {'name': 'Diwali', 'multiplier': 1.8, 'type': 'major'},
            '2025-11-15': {'name': 'Karthikai Deepam', 'multiplier': 1.5, 'type': 'regional'},
            '2025-12-25': {'name': 'Christmas', 'multiplier': 1.4, 'type': 'national'},
            '2026-01-14': {'name': 'Thai Pusam', 'multiplier': 1.6, 'type': 'regional'},
            '2026-01-26': {'name': 'Republic Day', 'multiplier': 1.3, 'type': 'national'},
            '2026-02-16': {'name': 'Maha Shivratri', 'multiplier': 1.5, 'type': 'major'},
            '2026-03-14': {'name': 'Holi', 'multiplier': 1.4, 'type': 'national'},
            '2026-04-14': {'name': 'Tamil New Year', 'multiplier': 1.7, 'type': 'regional'},
        }
        
        # Market days for each route
        self.market_days = {
            'tp_pc': [1, 4],  # Tuesday, Friday
            'tp_cb': [0, 2, 5],  # Monday, Wednesday, Saturday
            'tp_sl': [2, 5]   # Wednesday, Saturday
        }
        
        # Base demand patterns
        self.base_patterns = {
            'tp_pc': {
                'weekday': [35, 25, 15, 10, 20, 60, 140, 380, 320, 180, 150, 130, 115, 100, 90, 75, 220, 450, 350, 240, 140, 90, 60, 45],
                'weekend': [25, 18, 12, 8, 15, 35, 85, 200, 180, 120, 100, 90, 80, 70, 65, 55, 130, 250, 200, 140, 85, 55, 35, 28]
            },
            'tp_cb': {
                'weekday': [50, 35, 25, 20, 30, 90, 200, 580, 460, 280, 220, 190, 165, 145, 125, 110, 320, 620, 520, 360, 220, 150, 90, 70],
                'weekend': [35, 25, 18, 15, 22, 55, 120, 350, 280, 180, 150, 130, 115, 105, 95, 80, 200, 380, 320, 220, 135, 90, 55, 42]
            },
            'tp_sl': {
                'weekday': [40, 30, 22, 18, 28, 75, 175, 440, 380, 240, 195, 165, 145, 125, 110, 95, 280, 500, 400, 290, 185, 125, 75, 55],
                'weekend': [28, 22, 16, 12, 20, 45, 105, 260, 220, 150, 125, 110, 95, 85, 75, 65, 170, 300, 240, 175, 110, 75, 45, 35]
            }
        }

    def get_weather_data_free_api(self) -> WeatherData:
        """Get weather data - currently simulated, can integrate with real APIs"""
        try:
            # For demo - simulate realistic weather for Tamil Nadu
            today = datetime.now()
            month = today.month
            hour = today.hour
            
            # Seasonal weather patterns
            if month in [12, 1, 2]:  # Winter
                temp = random.uniform(18, 28)
                rainfall = random.uniform(0, 5)
                humidity = random.uniform(60, 80)
                conditions = ['Clear', 'Partly Cloudy', 'Light Rain']
                
            elif month in [3, 4, 5]:  # Summer  
                temp = random.uniform(28, 38)
                rainfall = random.uniform(0, 15)
                humidity = random.uniform(40, 70)
                conditions = ['Clear', 'Hot', 'Partly Cloudy', 'Thunderstorm']
                
            elif month in [6, 7, 8, 9]:  # Monsoon
                temp = random.uniform(22, 32)
                rainfall = random.uniform(5, 50)
                humidity = random.uniform(70, 95)
                conditions = ['Rain', 'Heavy Rain', 'Cloudy', 'Thunderstorm']
                
            else:  # Post-monsoon
                temp = random.uniform(24, 30)
                rainfall = random.uniform(0, 10)
                humidity = random.uniform(60, 85)
                conditions = ['Clear', 'Partly Cloudy', 'Light Rain']
            
            condition = random.choice(conditions)
            wind_speed = random.uniform(5, 20)
            
            # Calculate weather impact factor
            weather_factor = self.calculate_weather_factor(condition, rainfall, temp)
            
            return WeatherData(
                temperature=temp,
                condition=condition,
                humidity=humidity,
                rainfall=rainfall,
                wind_speed=wind_speed,
                weather_factor=weather_factor
            )
            
        except Exception as e:
            logging.error(f"Error generating weather data: {e}")
            return WeatherData(28.0, 'Clear', 70.0, 0.0, 10.0, 1.0)

    def calculate_weather_factor(self, condition: str, rainfall: float, temperature: float) -> float:
        """Calculate weather impact on bus demand"""
        factor = 1.0
        
        # Rain increases bus usage
        if rainfall > 20:
            factor *= 1.5
        elif rainfall > 10:
            factor *= 1.3
        elif rainfall > 5:
            factor *= 1.15
        
        # Temperature effects
        if temperature > 35:
            factor *= 1.2
        elif temperature < 15:
            factor *= 0.9
        
        # Condition effects
        condition_multipliers = {
            'Heavy Rain': 1.6, 'Rain': 1.3, 'Thunderstorm': 1.4,
            'Light Rain': 1.15, 'Cloudy': 1.05, 'Partly Cloudy': 1.0,
            'Clear': 1.0, 'Hot': 1.15, 'Sunny': 1.0
        }
        
        factor *= condition_multipliers.get(condition, 1.0)
        return min(factor, 2.0)  # Cap at 2x increase

    def get_festival_data(self, target_date: date) -> FestivalData:
        """Check if target date is a festival"""
        date_str = target_date.strftime('%Y-%m-%d')
        
        if date_str in self.festivals:
            festival_info = self.festivals[date_str]
            return FestivalData(
                is_festival=True,
                name=festival_info['name'],
                impact_multiplier=festival_info['multiplier'],
                type=festival_info['type']
            )
        
        return FestivalData(False, '', 1.0, 'regular')

    def is_market_day(self, route_id: str, day_of_week: int) -> bool:
        """Check if it's a market day for the route"""
        return day_of_week in self.market_days.get(route_id, [])

    def calculate_base_demand(self, route_id: str, hour: int, day_of_week: int) -> int:
        """Get base demand for route, hour, and day"""
        pattern_key = 'weekday' if day_of_week < 5 else 'weekend'
        return self.base_patterns[route_id][pattern_key][hour]

    def update_current_day_actual(self):
        """Update actual passenger data for current day"""
        today = date.today()
        current_hour = datetime.now().hour
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        routes = ['tp_pc', 'tp_cb', 'tp_sl']
        
        for route_id in routes:
            for hour in range(min(current_hour + 1, 24)):
                base_demand = self.calculate_base_demand(route_id, hour, today.weekday())
                actual_demand = int(base_demand * random.uniform(0.7, 1.3))
                actual_demand = max(0, actual_demand)
                
                cursor.execute("""
                INSERT OR REPLACE INTO passenger_demand
                (route_id, hour, day_of_week, passenger_count, date_recorded, 
                 is_predicted, weather_factor, festival_factor, market_factor, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (route_id, hour, today.weekday(), actual_demand, today,
                      False, 1.0, 1.0, 1.0, 1.0))
        
        conn.commit()
        conn.close()
        logging.info(f"Updated actual data for {today}")

    def predict_tomorrow_demand(self):
        """Generate predictions for tomorrow"""
        tomorrow = date.today() + timedelta(days=1)
        tomorrow_weekday = tomorrow.weekday()
        
        weather_data = self.get_weather_data_free_api()
        festival_data = self.get_festival_data(tomorrow)
        
        logging.info(f"Weather forecast: {weather_data.condition}, {weather_data.temperature:.1f}°C")
        if festival_data.is_festival:
            logging.info(f"Festival tomorrow: {festival_data.name} (impact: {festival_data.impact_multiplier}x)")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store external factors
        cursor.execute("""
        INSERT OR REPLACE INTO external_factors 
        (date_recorded, weather_condition, temperature, rainfall, humidity, 
         is_festival, festival_name, festival_impact, day_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tomorrow, weather_data.condition, weather_data.temperature,
              weather_data.rainfall, weather_data.humidity, festival_data.is_festival,
              festival_data.name, festival_data.impact_multiplier,
              'festival' if festival_data.is_festival else ('weekend' if tomorrow_weekday >= 5 else 'weekday')))
        
        routes = ['tp_pc', 'tp_cb', 'tp_sl']
        
        for route_id in routes:
            is_market = self.is_market_day(route_id, tomorrow_weekday)
            market_factor = 1.3 if is_market else 1.0
            
            if is_market:
                logging.info(f"Market day tomorrow for {route_id}")
            
            for hour in range(24):
                base_demand = self.calculate_base_demand(route_id, hour, tomorrow_weekday)
                
                # Apply all factors
                predicted_demand = base_demand
                predicted_demand = int(predicted_demand * weather_data.weather_factor)
                predicted_demand = int(predicted_demand * festival_data.impact_multiplier)
                predicted_demand = int(predicted_demand * market_factor)
                
                # Add natural variation
                variation = random.uniform(0.85, 1.15)
                predicted_demand = int(predicted_demand * variation)
                predicted_demand = max(0, predicted_demand)
                
                # Calculate optimal schedule
                buses_needed, frequency = self.calculate_optimal_schedule(predicted_demand)
                cost_per_hour = self.calculate_hourly_cost(buses_needed, self.get_route_distance(route_id), frequency)
                utilization_rate = min(predicted_demand / (buses_needed * 45), 1.0) if buses_needed > 0 else 0
                
                # Store prediction
                cursor.execute("""
                INSERT OR REPLACE INTO daily_schedule_predictions
                (route_id, prediction_date, hour, predicted_passengers, recommended_buses, 
                 frequency_minutes, cost_per_hour, utilization_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (route_id, tomorrow, hour, predicted_demand, buses_needed,
                      frequency, cost_per_hour, utilization_rate))
                
                # Store in passenger_demand for tracking
                confidence = 0.8 if not festival_data.is_festival else 0.6
                
                cursor.execute("""
                INSERT OR REPLACE INTO passenger_demand
                (route_id, hour, day_of_week, passenger_count, date_recorded, 
                 is_predicted, weather_factor, festival_factor, market_factor, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (route_id, hour, tomorrow_weekday, predicted_demand, tomorrow, True,
                      weather_data.weather_factor, festival_data.impact_multiplier,
                      market_factor, confidence))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Generated predictions for {tomorrow}")
        return {
            'date': tomorrow.strftime('%Y-%m-%d'),
            'weather_factor': weather_data.weather_factor,
            'festival': festival_data.name if festival_data.is_festival else None,
            'festival_impact': festival_data.impact_multiplier
        }

    def calculate_optimal_schedule(self, demand: int) -> Tuple[int, int]:
        """Calculate optimal buses and frequency"""
        if demand == 0:
            return 0, 120
        elif demand <= 20:
            return 1, 90
        elif demand <= 45:
            return 1, 60
        elif demand <= 90:
            return 2, 45
        elif demand <= 135:
            return 2, 30
        elif demand <= 200:
            return 3, 25
        elif demand <= 300:
            return 4, 20
        elif demand <= 400:
            return 5, 15
        else:
            buses = max(3, min(8, (demand + 44) // 45))
            frequency = max(10, 60 // max(1, buses - 2))
            return buses, frequency

    def get_route_distance(self, route_id: str) -> int:
        """Get route distance"""
        distances = {'tp_pc': 85, 'tp_cb': 65, 'tp_sl': 113}
        return distances.get(route_id, 85)

    def calculate_hourly_cost(self, buses: int, distance: int, frequency: int) -> float:
        """Calculate operational cost per hour"""
        if buses == 0:
            return 0
        
        fuel_per_km = 8.5
        driver_per_hour = 120
        maintenance_per_km = 3.2
        
        trips_per_hour = 60 / frequency if frequency > 0 else 0
        fuel_cost = distance * fuel_per_km * trips_per_hour * buses
        driver_cost = driver_per_hour * buses
        maintenance_cost = distance * maintenance_per_km * trips_per_hour * buses
        
        return fuel_cost + driver_cost + maintenance_cost

    def run_daily_update(self):
        """Main daily update routine"""
        try:
            logging.info("Starting daily update process...")
            self.update_current_day_actual()
            prediction_data = self.predict_tomorrow_demand()
            logging.info("Daily update process completed successfully")
            return prediction_data
        except Exception as e:
            logging.error(f"Daily update failed: {e}")
            return None

def main():
    """Run a single update (for testing)"""
    print("🚌 Tamil Nadu Transport Optimizer - Daily Update Test")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 50)
    
    updater = TransportDataUpdater()
    result = updater.run_daily_update()
    
    if result:
        print("✅ Daily update completed successfully!")
        print(f"Predictions generated for: {result['date']}")
        print(f"Weather factor: {result['weather_factor']:.2f}")
        if result.get('festival'):
            print(f"Festival: {result['festival']} (impact: {result['festival_impact']:.1f}x)")
        print("\nCheck the database for updated predictions.")
    else:
        print("❌ Daily update failed. Check the logs for details.")

if __name__ == '__main__':
    main()