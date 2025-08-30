#!/usr/bin/env python3
"""
System Test Script for Enhanced Transport Optimizer
Tests all major system components
"""

import requests
import sqlite3
import sys
import os
from datetime import datetime, date
import json

class SystemTester:
    def __init__(self):
        self.api_base = 'http://localhost:5000/api'
        self.db_path = 'transport_optimizer.db'
        self.test_results = []
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            if not os.path.exists(self.db_path):
                self.log_error(f"Database file {self.db_path} not found. Run enhanced_backend_server.py first.")
                return False
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM routes")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count >= 3:
                self.log_success(f"Database connection successful, found {count} routes")
                return True
            else:
                self.log_error(f"Database has insufficient routes: {count}")
                return False
                
        except Exception as e:
            self.log_error(f"Database connection failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test main API endpoints"""
        endpoints = [
            '/routes',
            '/dashboard-stats',
            '/passenger-demand/tp_pc'
        ]
        
        success = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_success(f"API endpoint {endpoint} working")
                else:
                    self.log_error(f"API endpoint {endpoint} returned status {response.status_code}")
                    success = False
                    
            except requests.exceptions.ConnectionError:
                self.log_error("Cannot connect to API server. Is enhanced_backend_server.py running?")
                return False
            except Exception as e:
                self.log_error(f"API test failed for {endpoint}: {e}")
                success = False
        
        return success
    
    def test_prediction_system(self):
        """Test prediction generation"""
        try:
            response = requests.post(f"{self.api_base}/daily-update", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_success("Prediction system working")
                    return True
                else:
                    self.log_error("Prediction system returned error")
                    return False
            else:
                self.log_error(f"Prediction system test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Prediction system test failed: {e}")
            return False
    
    def test_weather_simulation(self):
        """Test weather data simulation"""
        try:
            # Import weather function from scheduler
            from daily_update_scheduler import TransportDataUpdater
            
            updater = TransportDataUpdater()
            weather_data = updater.get_weather_data_free_api()
            
            if weather_data.temperature > 0 and weather_data.weather_factor > 0:
                self.log_success(f"Weather simulation working: {weather_data.condition}, {weather_data.temperature:.1f}°C")
                return True
            else:
                self.log_error("Weather simulation returned invalid data")
                return False
                
        except Exception as e:
            self.log_error(f"Weather simulation test failed: {e}")
            return False
    
    def test_festival_detection(self):
        """Test festival detection"""
        try:
            from daily_update_scheduler import TransportDataUpdater
            
            updater = TransportDataUpdater()
            festival_data = updater.get_festival_data(date.today())
            
            self.log_success(f"Festival detection working: {festival_data.name or 'No festival today'}")
            return True
            
        except Exception as e:
            self.log_error(f"Festival detection test failed: {e}")
            return False
    
    def test_schedule_optimization(self):
        """Test schedule optimization algorithm"""
        try:
            from daily_update_scheduler import TransportDataUpdater
            
            updater = TransportDataUpdater()
            
            # Test various demand levels
            test_cases = [0, 50, 150, 300, 500]
            for demand in test_cases:
                buses, frequency = updater.calculate_optimal_schedule(demand)
                if buses >= 0 and frequency > 0:
                    continue
                else:
                    self.log_error(f"Schedule optimization failed for demand {demand}")
                    return False
            
            self.log_success("Schedule optimization algorithm working")
            return True
            
        except Exception as e:
            self.log_error(f"Schedule optimization test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all system tests"""
        print("🧪 Starting Enhanced Transport Optimizer System Tests")
        print("=" * 60)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("API Endpoints", self.test_api_endpoints),
            ("Weather Simulation", self.test_weather_simulation),
            ("Festival Detection", self.test_festival_detection),
            ("Schedule Optimization", self.test_schedule_optimization),
            ("Prediction System", self.test_prediction_system),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            if test_func():
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("✅ All tests passed! System is ready for use.")
            self.log_system_info()
        else:
            print("❌ Some tests failed. Please check the error messages above.")
            
        return failed == 0
    
    def log_system_info(self):
        """Log system information"""
        print("\n📋 System Information:")
        print(f"   • Database: {self.db_path}")
        print(f"   • API Server: {self.api_base}")
        print(f"   • Test Time: {datetime.now()}")
        print(f"   • Routes: Tiruppur-Pollachi, Tiruppur-Coimbatore, Tiruppur-Salem")
        print(f"   • Features: Weather integration, Festival detection, Auto-scheduling")
    
    def log_success(self, message):
        print(f"   ✅ {message}")
        self.test_results.append(("PASS", message))
    
    def log_error(self, message):
        print(f"   ❌ {message}")
        self.test_results.append(("FAIL", message))

def main():
    """Main test function"""
    tester = SystemTester()
    
    print("Enhanced Tamil Nadu Transport Optimizer - System Test")
    print(f"Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"Time: {datetime.now().strftime('%I:%M %p IST')}")
    print()
    
    # Check if backend server is running
    try:
        response = requests.get("http://localhost:5000/api/routes", timeout=5)
        print("🚀 Backend server detected and responding")
    except:
        print("⚠️  Backend server not running. Please start enhanced_backend_server.py first")
        print("   Command: python enhanced_backend_server.py")
        return False
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 System is fully operational and ready for your college project!")
        print("\n📝 Next Steps:")
        print("   1. Start the daily scheduler: python daily_update_scheduler.py")
        print("   2. Open the frontend: http://localhost:8080")
        print("   3. Configure weather APIs in config.env (optional)")
        print("   4. Review the project documentation")
    else:
        print("\n🔧 Troubleshooting Tips:")
        print("   1. Ensure enhanced_backend_server.py is running")
        print("   2. Check if database file exists")
        print("   3. Verify all required packages are installed")
        print("   4. Check for port conflicts (5000, 8080)")
    
    return success

if __name__ == '__main__':
    main()