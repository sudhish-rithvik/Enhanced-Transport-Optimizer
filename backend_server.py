
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Routes table
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

    # Passenger demand data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passenger_demand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        hour INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,
        passenger_count INTEGER NOT NULL,
        date_recorded DATE NOT NULL,
        FOREIGN KEY (route_id) REFERENCES routes (id)
    )
    """)

    # Bus schedules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bus_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        departure_time TIME NOT NULL,
        frequency_minutes INTEGER NOT NULL,
        is_peak_hour BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (route_id) REFERENCES routes (id)
    )
    """)

    # Optimization results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS optimization_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT NOT NULL,
        optimization_date DATE NOT NULL,
        current_cost REAL NOT NULL,
        optimized_cost REAL NOT NULL,
        cost_savings REAL NOT NULL,
        fuel_savings REAL NOT NULL,
        recommendations TEXT NOT NULL,
        FOREIGN KEY (route_id) REFERENCES routes (id)
    )
    """)

    # Insert initial route data
    routes = [
        ('tp_pc', 'Tiruppur to Pollachi', 85, 120, 12, 2800),
        ('tp_cb', 'Tiruppur to Coimbatore', 65, 90, 18, 4200),
        ('tp_sl', 'Tiruppur to Salem', 113, 150, 15, 3500)
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO routes (id, name, distance, travel_time, current_buses, daily_passengers)
    VALUES (?, ?, ?, ?, ?, ?)
    """, routes)

    # Insert sample passenger demand data
    import random
    hourly_patterns = {
        'tp_pc': [45, 35, 25, 20, 30, 85, 180, 450, 380, 220, 180, 160, 140, 120, 110, 95, 280, 520, 420, 290, 180, 120, 80, 60],
        'tp_cb': [60, 45, 30, 25, 40, 120, 250, 680, 540, 320, 260, 220, 190, 170, 150, 130, 380, 720, 600, 420, 260, 180, 110, 85],
        'tp_sl': [50, 40, 28, 22, 35, 100, 210, 520, 450, 280, 230, 190, 170, 150, 130, 115, 340, 580, 480, 350, 220, 150, 95, 70]
    }

    # Generate 30 days of sample data
    for route_id, pattern in hourly_patterns.items():
        for day in range(30):
            date = datetime.now() - timedelta(days=day)
            for hour, base_passengers in enumerate(pattern):
                # Add some random variation
                passengers = max(0, int(base_passengers + random.randint(-20, 20)))
                cursor.execute("""
                INSERT OR REPLACE INTO passenger_demand (route_id, hour, day_of_week, passenger_count, date_recorded)
                VALUES (?, ?, ?, ?, ?)
                """, (route_id, hour, date.weekday(), passengers, date.date()))

    conn.commit()
    conn.close()

# API Routes
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

    # Get hourly demand for the route
    cursor.execute("""
    SELECT hour, AVG(passenger_count) as avg_passengers
    FROM passenger_demand 
    WHERE route_id = ? AND date_recorded >= date('now', '-7 days')
    GROUP BY hour
    ORDER BY hour
    """, (route_id,))

    demand_data = cursor.fetchall()
    conn.close()

    hourly_demand = [0] * 24
    for hour, avg_passengers in demand_data:
        hourly_demand[hour] = int(avg_passengers)

    return jsonify({
        'route_id': route_id,
        'hourly_demand': hourly_demand
    })

@app.route('/api/optimize-schedule', methods=['POST'])
def optimize_schedule():
    data = request.json
    route_id = data.get('route_id')

    if not route_id:
        return jsonify({'error': 'Route ID is required'}), 400

    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Get route information
    cursor.execute("SELECT * FROM routes WHERE id = ?", (route_id,))
    route = cursor.fetchone()

    if not route:
        return jsonify({'error': 'Route not found'}), 404

    # Get passenger demand data
    cursor.execute("""
    SELECT hour, AVG(passenger_count) as avg_passengers
    FROM passenger_demand 
    WHERE route_id = ? AND date_recorded >= date('now', '-7 days')
    GROUP BY hour
    ORDER BY hour
    """, (route_id,))

    demand_data = cursor.fetchall()

    # Calculate optimal schedule
    hourly_demand = {}
    for hour, avg_passengers in demand_data:
        hourly_demand[hour] = int(avg_passengers)

    # Optimization algorithm
    bus_capacity = 45
    recommendations = []
    current_cost = 0
    optimized_cost = 0

    for hour in range(24):
        passengers = hourly_demand.get(hour, 0)

        # Determine optimal frequency based on demand
        if passengers > 400:  # Peak hours
            optimal_frequency = 15  # Every 15 minutes
            buses_needed = max(2, (passengers + bus_capacity - 1) // bus_capacity)
        elif passengers > 200:  # Moderate demand
            optimal_frequency = 30  # Every 30 minutes
            buses_needed = max(1, (passengers + bus_capacity - 1) // bus_capacity)
        elif passengers > 50:   # Low demand
            optimal_frequency = 60  # Every hour
            buses_needed = 1
        else:  # Very low demand
            optimal_frequency = 120  # Every 2 hours
            buses_needed = 1 if passengers > 0 else 0

        # Calculate costs
        distance = route[2]  # distance from route table
        fuel_cost_per_trip = distance * 8.5  # 8.5 rupees per km
        driver_cost_per_hour = 120
        maintenance_cost_per_trip = distance * 3.2

        trips_per_hour = 60 // optimal_frequency if optimal_frequency > 0 else 0
        hour_cost = (fuel_cost_per_trip + maintenance_cost_per_trip) * trips_per_hour + driver_cost_per_hour * buses_needed

        optimized_cost += hour_cost

        # Current schedule cost (assume fixed frequency)
        current_trips_per_hour = 3 if 7 <= hour <= 19 else 1  # Simple current schedule
        current_cost += (fuel_cost_per_trip + maintenance_cost_per_trip) * current_trips_per_hour + driver_cost_per_hour * 2

        recommendations.append({
            'hour': f"{hour:02d}:00",
            'passengers': passengers,
            'optimal_frequency': optimal_frequency,
            'buses_needed': buses_needed,
            'cost_per_hour': hour_cost
        })

    cost_savings = current_cost - optimized_cost
    fuel_savings = (current_cost - optimized_cost) * 0.4  # Assume 40% of savings from fuel

    # Store optimization result
    cursor.execute("""
    INSERT INTO optimization_results (route_id, optimization_date, current_cost, optimized_cost, cost_savings, fuel_savings, recommendations)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (route_id, datetime.now().date(), current_cost, optimized_cost, cost_savings, fuel_savings, json.dumps(recommendations)))

    conn.commit()
    conn.close()

    return jsonify({
        'route_id': route_id,
        'current_cost': round(current_cost, 2),
        'optimized_cost': round(optimized_cost, 2),
        'cost_savings': round(cost_savings, 2),
        'fuel_savings': round(fuel_savings, 2),
        'percentage_savings': round((cost_savings / current_cost) * 100, 2) if current_cost > 0 else 0,
        'recommendations': recommendations
    })

@app.route('/api/schedule-history/<route_id>', methods=['GET'])
def get_schedule_history(route_id):
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT optimization_date, current_cost, optimized_cost, cost_savings, fuel_savings
    FROM optimization_results 
    WHERE route_id = ?
    ORDER BY optimization_date DESC
    LIMIT 30
    """, (route_id,))

    history = cursor.fetchall()
    conn.close()

    history_data = []
    for record in history:
        history_data.append({
            'date': record[0],
            'current_cost': record[1],
            'optimized_cost': record[2],
            'cost_savings': record[3],
            'fuel_savings': record[4]
        })

    return jsonify(history_data)

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Total routes
    cursor.execute("SELECT COUNT(*) FROM routes")
    total_routes = cursor.fetchone()[0]

    # Total buses
    cursor.execute("SELECT SUM(current_buses) FROM routes")
    total_buses = cursor.fetchone()[0] or 0

    # Total daily passengers
    cursor.execute("SELECT SUM(daily_passengers) FROM routes")
    total_passengers = cursor.fetchone()[0] or 0

    # Recent cost savings
    cursor.execute("""
    SELECT SUM(cost_savings) FROM optimization_results 
    WHERE optimization_date >= date('now', '-7 days')
    """)
    weekly_savings = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        'total_routes': total_routes,
        'total_buses': total_buses,
        'total_passengers': total_passengers,
        'weekly_savings': round(weekly_savings, 2)
    })

if __name__ == '__main__':
    # Initialize database on startup
    if not os.path.exists('transport_optimizer.db'):
        init_db()

    app.run(debug=True, host='0.0.0.0', port=5000)
