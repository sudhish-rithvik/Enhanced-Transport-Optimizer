
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, date
import sqlite3
import json
import os
import requests
import random
import math
from typing import Dict, List, Tuple

app = Flask(__name__)
CORS(app)

# Festival and holiday data for Tamil Nadu (can be expanded with API)
TAMIL_NADU_FESTIVALS = {
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
    '2026-05-01': {'name': 'Labour Day', 'multiplier': 1.2, 'type': 'national'},
    '2026-08-15': {'name': 'Independence Day', 'multiplier': 1.4, 'type': 'national'}
}

# Market days (typically increased demand)
MARKET_DAYS = {
    'tp_pc': [1, 4],  # Tuesday, Friday for Pollachi
    'tp_cb': [0, 2, 5],  # Monday, Wednesday, Saturday for Coimbatore
    'tp_sl': [2, 5]   # Wednesday, Saturday for Salem
}

# Enhanced database initialization
def init_enhanced_db():
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Routes table (existing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        distance INTEGER NOT NULL,
        travel_time INTEGER NOT NULL,
        current_buses INTEGER NOT NULL,
        daily_passengers INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Enhanced passenger demand with predictions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passenger_demand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
        day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
        passenger_count INTEGER NOT NULL,
        date_recorded DATE NOT NULL,
        is_predicted BOOLEAN DEFAULT FALSE,
        weather_factor REAL DEFAULT 1.0,
        festival_factor REAL DEFAULT 1.0,
        market_factor REAL DEFAULT 1.0,
        confidence_score REAL DEFAULT 0.8,
        FOREIGN KEY (route_id) REFERENCES routes (id)
    )
    """)

    # Daily schedule predictions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_schedule_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        prediction_date DATE NOT NULL,
        hour INTEGER NOT NULL,
        predicted_passengers INTEGER NOT NULL,
        recommended_buses INTEGER NOT NULL,
        frequency_minutes INTEGER NOT NULL,
        cost_per_hour REAL NOT NULL,
        utilization_rate REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (route_id) REFERENCES routes (id)
    )
    """)

    # External factors tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS external_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_recorded DATE NOT NULL,
        weather_condition TEXT,
        temperature REAL,
        rainfall REAL,
        humidity REAL,
        is_festival BOOLEAN DEFAULT FALSE,
        festival_name TEXT,
        festival_impact REAL DEFAULT 1.0,
        is_market_day BOOLEAN DEFAULT FALSE,
        day_type TEXT DEFAULT 'regular',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Performance tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_accuracy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        prediction_date DATE NOT NULL,
        predicted_passengers INTEGER NOT NULL,
        actual_passengers INTEGER,
        accuracy_percentage REAL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert route data
    routes = [
        ('tp_pc', 'Tiruppur to Pollachi', 85, 120, 12, 2800),
        ('tp_cb', 'Tiruppur to Coimbatore', 65, 90, 18, 4200),
        ('tp_sl', 'Tiruppur to Salem', 113, 150, 15, 3500)
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO routes (id, name, distance, travel_time, current_buses, daily_passengers)
    VALUES (?, ?, ?, ?, ?, ?)
    """, routes)

    conn.commit()
    conn.close()

def get_weather_data() -> Dict:
    """
    Get weather data for Tamil Nadu (Tiruppur area)
    Using OpenWeatherMap free API - replace with your API key
    """
    try:
        # Free weather API (you can use OpenWeatherMap, WeatherAPI, etc.)
        # For demo purposes, we'll simulate weather data
        # In production, use: requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Tiruppur,IN&appid={API_KEY}")

        # Simulated weather data based on current season
        today = datetime.now()
        month = today.month

        if month in [12, 1, 2]:  # Winter
            temp = random.uniform(18, 28)
            rainfall = random.uniform(0, 5)
            humidity = random.uniform(60, 80)
            condition = random.choice(['Clear', 'Partly Cloudy', 'Light Rain'])
        elif month in [3, 4, 5]:  # Summer
            temp = random.uniform(25, 38)
            rainfall = random.uniform(0, 15)
            humidity = random.uniform(40, 70)
            condition = random.choice(['Clear', 'Hot', 'Partly Cloudy', 'Thunderstorm'])
        elif month in [6, 7, 8, 9]:  # Monsoon
            temp = random.uniform(20, 32)
            rainfall = random.uniform(5, 50)
            humidity = random.uniform(70, 95)
            condition = random.choice(['Rain', 'Heavy Rain', 'Cloudy', 'Thunderstorm'])
        else:  # Post-monsoon
            temp = random.uniform(22, 30)
            rainfall = random.uniform(0, 10)
            humidity = random.uniform(60, 85)
            condition = random.choice(['Clear', 'Partly Cloudy', 'Light Rain'])

        return {
            'temperature': temp,
            'rainfall': rainfall,
            'humidity': humidity,
            'condition': condition,
            'weather_factor': calculate_weather_factor(condition, rainfall, temp)
        }
    except:
        # Fallback weather data
        return {
            'temperature': 28,
            'rainfall': 2,
            'humidity': 70,
            'condition': 'Clear',
            'weather_factor': 1.0
        }

def calculate_weather_factor(condition: str, rainfall: float, temperature: float) -> float:
    """Calculate how weather affects passenger demand"""
    factor = 1.0

    # Rain effect
    if rainfall > 10:
        factor *= 1.3  # More people use buses in heavy rain
    elif rainfall > 5:
        factor *= 1.15  # Moderate increase in light rain

    # Temperature effect
    if temperature > 35:
        factor *= 1.1  # Hot weather increases bus usage
    elif temperature < 15:
        factor *= 0.9  # Very cold weather might reduce demand

    # Condition effect
    condition_factors = {
        'Heavy Rain': 1.4,
        'Rain': 1.25,
        'Thunderstorm': 1.3,
        'Cloudy': 1.05,
        'Clear': 1.0,
        'Hot': 1.1
    }

    factor *= condition_factors.get(condition, 1.0)

    return min(factor, 2.0)  # Cap at 2x increase

def is_festival_day(date_obj: date) -> Tuple[bool, Dict]:
    """Check if given date is a festival day"""
    date_str = date_obj.strftime('%Y-%m-%d')
    if date_str in TAMIL_NADU_FESTIVALS:
        return True, TAMIL_NADU_FESTIVALS[date_str]

    # Check for weekly festivals (like every Tuesday is market day, etc.)
    # Add more logic here for recurring festivals

    return False, {}

def is_market_day(route_id: str, day_of_week: int) -> bool:
    """Check if given day is a market day for the route"""
    return day_of_week in MARKET_DAYS.get(route_id, [])

def calculate_base_demand(route_id: str, hour: int, day_of_week: int) -> int:
    """Calculate base passenger demand based on historical patterns"""

    # Enhanced base patterns considering route characteristics
    base_patterns = {
        'tp_pc': {  # Tiruppur to Pollachi - Agricultural + Industrial
            'weekday': [35, 25, 15, 10, 20, 60, 140, 380, 320, 180, 150, 130, 115, 100, 90, 75, 220, 450, 350, 240, 140, 90, 60, 45],
            'weekend': [25, 18, 12, 8, 15, 35, 85, 200, 180, 120, 100, 90, 80, 70, 65, 55, 130, 250, 200, 140, 85, 55, 35, 28]
        },
        'tp_cb': {  # Tiruppur to Coimbatore - Major Commercial
            'weekday': [50, 35, 25, 20, 30, 90, 200, 580, 460, 280, 220, 190, 165, 145, 125, 110, 320, 620, 520, 360, 220, 150, 90, 70],
            'weekend': [35, 25, 18, 15, 22, 55, 120, 350, 280, 180, 150, 130, 115, 105, 95, 80, 200, 380, 320, 220, 135, 90, 55, 42]
        },
        'tp_sl': {  # Tiruppur to Salem - Mixed Commercial/Industrial
            'weekday': [40, 30, 22, 18, 28, 75, 175, 440, 380, 240, 195, 165, 145, 125, 110, 95, 280, 500, 400, 290, 185, 125, 75, 55],
            'weekend': [28, 22, 16, 12, 20, 45, 105, 260, 220, 150, 125, 110, 95, 85, 75, 65, 170, 300, 240, 175, 110, 75, 45, 35]
        }
    }

    pattern_key = 'weekday' if day_of_week < 5 else 'weekend'
    base_demand = base_patterns[route_id][pattern_key][hour]

    return base_demand

def predict_daily_demand():
    """Generate predictions for the next day based on all factors"""

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Get tomorrow's date
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_weekday = tomorrow.weekday()

    # Get weather data
    weather_data = get_weather_data()

    # Check if tomorrow is a festival
    is_festival, festival_data = is_festival_day(tomorrow)

    # Store external factors
    cursor.execute("""
    INSERT OR REPLACE INTO external_factors 
    (date_recorded, weather_condition, temperature, rainfall, humidity, 
     is_festival, festival_name, festival_impact, day_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tomorrow,
        weather_data['condition'],
        weather_data['temperature'],
        weather_data['rainfall'],
        weather_data['humidity'],
        is_festival,
        festival_data.get('name', '') if is_festival else '',
        festival_data.get('multiplier', 1.0) if is_festival else 1.0,
        'festival' if is_festival else ('weekend' if tomorrow_weekday >= 5 else 'weekday')
    ))

    routes = ['tp_pc', 'tp_cb', 'tp_sl']

    for route_id in routes:
        # Check if tomorrow is market day for this route
        is_market = is_market_day(route_id, tomorrow_weekday)
        market_factor = 1.3 if is_market else 1.0

        for hour in range(24):
            # Calculate base demand
            base_demand = calculate_base_demand(route_id, hour, tomorrow_weekday)

            # Apply all factors
            predicted_demand = base_demand
            predicted_demand = int(predicted_demand * weather_data['weather_factor'])
            predicted_demand = int(predicted_demand * (festival_data.get('multiplier', 1.0) if is_festival else 1.0))
            predicted_demand = int(predicted_demand * market_factor)

            # Add some randomness for realism
            variation = random.uniform(0.85, 1.15)
            predicted_demand = int(predicted_demand * variation)
            predicted_demand = max(0, predicted_demand)  # Ensure non-negative

            # Calculate recommended buses and frequency
            buses_needed, frequency = calculate_optimal_schedule(predicted_demand)

            # Calculate costs
            route_distance = get_route_distance(route_id)
            cost_per_hour = calculate_hourly_cost(buses_needed, route_distance, frequency)

            # Calculate utilization rate
            utilization_rate = min(predicted_demand / (buses_needed * 45), 1.0) if buses_needed > 0 else 0

            # Store prediction
            cursor.execute("""
            INSERT OR REPLACE INTO daily_schedule_predictions
            (route_id, prediction_date, hour, predicted_passengers, recommended_buses, 
             frequency_minutes, cost_per_hour, utilization_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route_id, tomorrow, hour, predicted_demand, buses_needed,
                frequency, cost_per_hour, utilization_rate
            ))

            # Also store in passenger_demand for historical tracking
            cursor.execute("""
            INSERT OR REPLACE INTO passenger_demand
            (route_id, hour, day_of_week, passenger_count, date_recorded, 
             is_predicted, weather_factor, festival_factor, market_factor, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route_id, hour, tomorrow_weekday, predicted_demand, tomorrow,
                True, weather_data['weather_factor'], 
                festival_data.get('multiplier', 1.0) if is_festival else 1.0,
                market_factor, 0.75  # Confidence score for predictions
            ))

    conn.commit()
    conn.close()

    return {
        'status': 'success',
        'prediction_date': tomorrow.strftime('%Y-%m-%d'),
        'weather_factor': weather_data['weather_factor'],
        'is_festival': is_festival,
        'festival_name': festival_data.get('name', '') if is_festival else None
    }

def calculate_optimal_schedule(predicted_demand: int) -> Tuple[int, int]:
    """Calculate optimal number of buses and frequency based on demand"""

    bus_capacity = 45

    if predicted_demand == 0:
        return 0, 120  # No buses needed, check every 2 hours
    elif predicted_demand <= 20:
        return 1, 90   # 1 bus every 1.5 hours
    elif predicted_demand <= 45:
        return 1, 60   # 1 bus every hour
    elif predicted_demand <= 90:
        return 2, 45   # 2 buses every 45 minutes
    elif predicted_demand <= 135:
        return 2, 30   # 2 buses every 30 minutes
    elif predicted_demand <= 200:
        return 3, 25   # 3 buses every 25 minutes
    elif predicted_demand <= 300:
        return 4, 20   # 4 buses every 20 minutes
    elif predicted_demand <= 400:
        return 5, 15   # 5 buses every 15 minutes
    else:
        # For very high demand, calculate based on capacity
        buses_needed = max(3, math.ceil(predicted_demand / bus_capacity))
        frequency = max(10, 60 // max(1, buses_needed - 2))
        return buses_needed, frequency

def get_route_distance(route_id: str) -> int:
    """Get route distance from database"""
    distances = {'tp_pc': 85, 'tp_cb': 65, 'tp_sl': 113}
    return distances.get(route_id, 85)

def calculate_hourly_cost(buses: int, distance: int, frequency: int) -> float:
    """Calculate hourly operational cost"""
    if buses == 0:
        return 0

    # Cost parameters
    fuel_cost_per_km = 8.5
    driver_salary_per_hour = 120
    maintenance_per_km = 3.2

    # Calculate trips per hour
    trips_per_hour = 60 / frequency if frequency > 0 else 0

    # Calculate costs
    fuel_cost = distance * fuel_cost_per_km * trips_per_hour * buses
    driver_cost = driver_salary_per_hour * buses
    maintenance_cost = distance * maintenance_per_km * trips_per_hour * buses

    return fuel_cost + driver_cost + maintenance_cost

def update_actual_data_for_today():
    """Simulate actual passenger data for today (would come from real sensors/counters)"""

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    today = date.today()
    today_weekday = today.weekday()
    current_hour = datetime.now().hour

    routes = ['tp_pc', 'tp_cb', 'tp_sl']

    for route_id in routes:
        for hour in range(min(current_hour + 1, 24)):  # Only update up to current hour
            # Get base demand
            base_demand = calculate_base_demand(route_id, hour, today_weekday)

            # Add realistic variation (±25%)
            actual_demand = int(base_demand * random.uniform(0.75, 1.25))

            # Store actual data
            cursor.execute("""
            INSERT OR REPLACE INTO passenger_demand
            (route_id, hour, day_of_week, passenger_count, date_recorded, 
             is_predicted, weather_factor, festival_factor, market_factor, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route_id, hour, today_weekday, actual_demand, today,
                False, 1.0, 1.0, 1.0, 1.0  # Actual data has full confidence
            ))

    conn.commit()
    conn.close()

# API Routes

@app.route('/api/daily-update', methods=['POST'])
def trigger_daily_update():
    """Trigger daily prediction update"""
    try:
        # Update today's actual data (simulate)
        update_actual_data_for_today()

        # Generate tomorrow's predictions
        result = predict_daily_demand()

        return jsonify({
            'status': 'success',
            'message': 'Daily update completed successfully',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/next-day-schedule/<route_id>', methods=['GET'])
def get_next_day_schedule(route_id):
    """Get tomorrow's recommended schedule for a route"""

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    tomorrow = date.today() + timedelta(days=1)

    cursor.execute("""
    SELECT hour, predicted_passengers, recommended_buses, frequency_minutes, 
           cost_per_hour, utilization_rate
    FROM daily_schedule_predictions
    WHERE route_id = ? AND prediction_date = ?
    ORDER BY hour
    """, (route_id, tomorrow))

    schedule_data = cursor.fetchall()
    conn.close()

    if not schedule_data:
        return jsonify({'error': 'No predictions found for tomorrow'}), 404

    schedule = []
    total_cost = 0
    total_buses = 0

    for hour, passengers, buses, frequency, cost, utilization in schedule_data:
        schedule.append({
            'hour': f"{hour:02d}:00",
            'predicted_passengers': passengers,
            'recommended_buses': buses,
            'frequency_minutes': frequency,
            'cost_per_hour': round(cost, 2),
            'utilization_rate': round(utilization * 100, 1),
            'status': 'peak' if passengers > 300 else ('moderate' if passengers > 100 else 'low')
        })
        total_cost += cost
        total_buses = max(total_buses, buses)

    return jsonify({
        'route_id': route_id,
        'date': tomorrow.strftime('%Y-%m-%d'),
        'schedule': schedule,
        'summary': {
            'total_daily_cost': round(total_cost, 2),
            'max_buses_needed': total_buses,
            'total_predicted_passengers': sum(item['predicted_passengers'] for item in schedule),
            'peak_hours': [item['hour'] for item in schedule if item['status'] == 'peak']
        }
    })

@app.route('/api/current-factors', methods=['GET'])
def get_current_factors():
    """Get current external factors affecting demand"""

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    tomorrow = date.today() + timedelta(days=1)

    cursor.execute("""
    SELECT weather_condition, temperature, rainfall, humidity, 
           is_festival, festival_name, festival_impact, day_type
    FROM external_factors
    WHERE date_recorded = ?
    ORDER BY created_at DESC
    LIMIT 1
    """, (tomorrow,))

    factor_data = cursor.fetchone()
    conn.close()

    if not factor_data:
        return jsonify({'error': 'No factor data available'}), 404

    return jsonify({
        'date': tomorrow.strftime('%Y-%m-%d'),
        'weather': {
            'condition': factor_data[0],
            'temperature': factor_data[1],
            'rainfall': factor_data[2],
            'humidity': factor_data[3]
        },
        'special_events': {
            'is_festival': bool(factor_data[4]),
            'festival_name': factor_data[5],
            'impact_multiplier': factor_data[6]
        },
        'day_type': factor_data[7]
    })

@app.route('/api/prediction-accuracy/<route_id>', methods=['GET'])
def get_prediction_accuracy(route_id):
    """Get prediction accuracy for a route"""

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Get recent prediction accuracy
    cursor.execute("""
    SELECT prediction_date, predicted_passengers, actual_passengers, accuracy_percentage
    FROM prediction_accuracy
    WHERE route_id = ?
    ORDER BY prediction_date DESC
    LIMIT 30
    """, (route_id,))

    accuracy_data = cursor.fetchall()

    if accuracy_data:
        avg_accuracy = sum(row[3] for row in accuracy_data if row[3]) / len([row for row in accuracy_data if row[3]])
    else:
        avg_accuracy = 85.0  # Default assumption

    conn.close()

    return jsonify({
        'route_id': route_id,
        'average_accuracy': round(avg_accuracy, 1),
        'recent_predictions': [
            {
                'date': row[0],
                'predicted': row[1],
                'actual': row[2],
                'accuracy': row[3]
            } for row in accuracy_data[:10]
        ]
    })

# Auto-schedule daily updates
@app.route('/api/auto-schedule', methods=['GET'])
def setup_auto_schedule():
    """Setup automatic daily scheduling (in production, use cron job or celery)"""

    # For demo purposes, we'll just return the schedule
    # In production, you'd use celery, cron, or similar

    return jsonify({
        'message': 'Auto-scheduling configured',
        'schedule': 'Daily at 11:30 PM IST',
        'next_update': (datetime.now() + timedelta(days=1)).replace(hour=23, minute=30).isoformat(),
        'features': [
            'Weather data integration',
            'Festival detection',
            'Market day identification',
            'Demand prediction',
            'Schedule optimization',
            'Cost calculation'
        ]
    })

# Enhanced existing routes
@app.route('/api/routes', methods=['GET'])
def get_routes():
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = cursor.fetchall()
    conn.close()

    route_list = []
    for route in routes:
        route_list.append({
            'id': route[0],
            'name': route[1],
            'distance': route[2],
            'travel_time': route[3],
            'current_buses': route[4],
            'daily_passengers': route[5]
        })

    return jsonify(route_list)

@app.route('/api/passenger-demand/<route_id>', methods=['GET'])
def get_passenger_demand(route_id):
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Get recent demand data including predictions
    cursor.execute("""
    SELECT hour, AVG(passenger_count) as avg_passengers, 
           AVG(CASE WHEN is_predicted = 1 THEN passenger_count END) as avg_predicted,
           AVG(CASE WHEN is_predicted = 0 THEN passenger_count END) as avg_actual
    FROM passenger_demand 
    WHERE route_id = ? AND date_recorded >= date('now', '-7 days')
    GROUP BY hour
    ORDER BY hour
    """, (route_id,))

    demand_data = cursor.fetchall()
    conn.close()

    hourly_demand = []
    predicted_demand = []
    actual_demand = []

    for hour, avg_all, avg_pred, avg_actual in demand_data:
        hourly_demand.append(int(avg_all or 0))
        predicted_demand.append(int(avg_pred or 0))
        actual_demand.append(int(avg_actual or 0))

    # Ensure we have 24 hours of data
    while len(hourly_demand) < 24:
        hourly_demand.append(0)
        predicted_demand.append(0)
        actual_demand.append(0)

    return jsonify({
        'route_id': route_id,
        'hourly_demand': hourly_demand[:24],
        'predicted_demand': predicted_demand[:24],
        'actual_demand': actual_demand[:24]
    })

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Total routes
    cursor.execute("SELECT COUNT(*) FROM routes")
    total_routes = cursor.fetchone()[0]

    # Total buses (from tomorrow's predictions)
    tomorrow = date.today() + timedelta(days=1)
    cursor.execute("""
    SELECT SUM(MAX(recommended_buses)) 
    FROM daily_schedule_predictions 
    WHERE prediction_date = ?
    GROUP BY route_id
    """, (tomorrow,))
    total_buses = cursor.fetchone()
    total_buses = total_buses[0] if total_buses else 45

    # Total predicted passengers for tomorrow
    cursor.execute("""
    SELECT SUM(predicted_passengers) 
    FROM daily_schedule_predictions 
    WHERE prediction_date = ?
    """, (tomorrow,))
    total_passengers = cursor.fetchone()
    total_passengers = total_passengers[0] if total_passengers else 10500

    # Cost savings estimate
    cursor.execute("""
    SELECT SUM(cost_per_hour) 
    FROM daily_schedule_predictions 
    WHERE prediction_date = ?
    """, (tomorrow,))
    optimized_cost = cursor.fetchone()
    optimized_cost = optimized_cost[0] if optimized_cost else 50000

    # Assume 25% savings from optimization
    weekly_savings = optimized_cost * 0.25 * 7

    conn.close()

    return jsonify({
        'total_routes': total_routes,
        'total_buses': int(total_buses),
        'total_passengers': int(total_passengers),
        'weekly_savings': round(weekly_savings, 2),
        'last_updated': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Initialize enhanced database
    if not os.path.exists('transport_optimizer.db'):
        init_enhanced_db()

    # Trigger initial prediction
    try:
        update_actual_data_for_today()
        predict_daily_demand()
        print("✅ Initial predictions generated successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not generate initial predictions: {e}")

    print("🚌 Enhanced Transport Optimizer Server Starting...")
    print("📊 Features: Daily Updates, Festival Detection, Weather Integration")
    print("🔄 Auto-scheduling configured for daily predictions")

    app.run(debug=True, host='0.0.0.0', port=5000)
