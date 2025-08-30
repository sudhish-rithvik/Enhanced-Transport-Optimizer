
import sqlite3
import random
from datetime import datetime, timedelta
import json

def generate_realistic_data():
    """
    Generate realistic passenger demand data for the Tamil Nadu transport routes
    """
    conn = sqlite3.connect('transport_optimizer.db')
    cursor = conn.cursor()

    # Route patterns based on real-world observations
    # Peak patterns: morning rush (7-9 AM), evening rush (5-7 PM)
    route_patterns = {
        'tp_pc': {  # Tiruppur to Pollachi - Industrial + Agricultural route
            'base_pattern': [45, 35, 25, 20, 30, 85, 180, 450, 380, 220, 180, 160, 140, 120, 110, 95, 280, 520, 420, 290, 180, 120, 80, 60],
            'weekend_factor': 0.6,  # 60% of weekday demand on weekends
            'seasonal_variation': 0.15,  # 15% seasonal variation
            'special_events': {
                'festival_days': 1.5,  # 50% increase on festival days
                'market_days': 1.3     # 30% increase on market days
            }
        },
        'tp_cb': {  # Tiruppur to Coimbatore - Major commercial route
            'base_pattern': [60, 45, 30, 25, 40, 120, 250, 680, 540, 320, 260, 220, 190, 170, 150, 130, 380, 720, 600, 420, 260, 180, 110, 85],
            'weekend_factor': 0.7,  # 70% of weekday demand
            'seasonal_variation': 0.12,
            'special_events': {
                'festival_days': 1.6,
                'market_days': 1.4
            }
        },
        'tp_sl': {  # Tiruppur to Salem - Mixed commercial/industrial route
            'base_pattern': [50, 40, 28, 22, 35, 100, 210, 520, 450, 280, 230, 190, 170, 150, 130, 115, 340, 580, 480, 350, 220, 150, 95, 70],
            'weekend_factor': 0.65,
            'seasonal_variation': 0.18,
            'special_events': {
                'festival_days': 1.4,
                'market_days': 1.25
            }
        }
    }

    # Generate data for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Clear existing data
    cursor.execute("DELETE FROM passenger_demand")

    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
        is_weekend = day_of_week >= 5  # Saturday and Sunday

        for route_id, pattern_data in route_patterns.items():
            base_pattern = pattern_data['base_pattern']
            weekend_factor = pattern_data['weekend_factor']
            seasonal_variation = pattern_data['seasonal_variation']

            for hour, base_passengers in enumerate(base_pattern):
                # Apply weekend reduction
                passengers = base_passengers
                if is_weekend:
                    passengers = int(passengers * weekend_factor)

                # Add seasonal variation
                seasonal_factor = 1 + (random.random() - 0.5) * seasonal_variation
                passengers = int(passengers * seasonal_factor)

                # Add daily random variation (±20%)
                daily_variation = 1 + (random.random() - 0.5) * 0.4
                passengers = int(passengers * daily_variation)

                # Special event handling (random 5% chance)
                if random.random() < 0.05:  # 5% chance of special event
                    if random.random() < 0.3:  # Festival day
                        passengers = int(passengers * pattern_data['special_events']['festival_days'])
                    else:  # Market day
                        passengers = int(passengers * pattern_data['special_events']['market_days'])

                # Ensure non-negative
                passengers = max(0, passengers)

                # Insert into database
                cursor.execute("""
                INSERT INTO passenger_demand (route_id, hour, day_of_week, passenger_count, date_recorded)
                VALUES (?, ?, ?, ?, ?)
                """, (route_id, hour, day_of_week, passengers, current_date.date()))

        current_date += timedelta(days=1)

    conn.commit()

    # Generate some sample optimization results
    generate_sample_optimization_results(cursor)
    conn.commit()
    conn.close()

    print(f"✅ Generated realistic passenger data for {(end_date - start_date).days + 1} days")

def generate_sample_optimization_results(cursor):
    """Generate sample optimization results for demonstration"""

    routes = ['tp_pc', 'tp_cb', 'tp_sl']

    # Generate results for last 30 days
    for days_back in range(30):
        date = datetime.now() - timedelta(days=days_back)

        for route_id in routes:
            # Simulate optimization results
            base_cost = random.uniform(15000, 25000)  # Base daily cost
            optimization_efficiency = random.uniform(0.08, 0.25)  # 8-25% savings

            optimized_cost = base_cost * (1 - optimization_efficiency)
            cost_savings = base_cost - optimized_cost
            fuel_savings = cost_savings * 0.4  # 40% of savings from fuel

            # Generate sample recommendations
            recommendations = []
            for hour in range(24):
                if 7 <= hour <= 8 or 17 <= hour <= 18:  # Peak hours
                    freq = 15
                    buses = 3
                elif 9 <= hour <= 16:  # Day time
                    freq = 30
                    buses = 2
                elif 19 <= hour <= 22:  # Evening
                    freq = 45
                    buses = 1
                else:  # Night/early morning
                    freq = 90
                    buses = 1

                recommendations.append({
                    'hour': f"{hour:02d}:00",
                    'frequency': freq,
                    'buses_needed': buses
                })

            cursor.execute("""
            INSERT INTO optimization_results 
            (route_id, optimization_date, current_cost, optimized_cost, cost_savings, fuel_savings, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (route_id, date.date(), base_cost, optimized_cost, cost_savings, fuel_savings, json.dumps(recommendations)))

if __name__ == '__main__':
    print("🚌 Generating realistic transport data...")
    generate_realistic_data()
    print("✅ Data generation complete!")
    print("📊 Database now contains:")
    print("  - 90 days of hourly passenger demand data")
    print("  - Realistic peak hour patterns")
    print("  - Weekend vs weekday variations")
    print("  - Seasonal and special event adjustments")
    print("  - Sample optimization results")
