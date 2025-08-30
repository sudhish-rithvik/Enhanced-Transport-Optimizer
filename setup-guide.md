# Tamil Nadu Transport Optimizer - Complete Setup Guide

## Overview
This is a comprehensive bus transport optimization system designed for government employees in Tamil Nadu. The system helps optimize bus schedules based on passenger demand patterns for three key routes:
1. Tiruppur to Pollachi
2. Tiruppur to Coimbatore  
3. Tiruppur to Salem

## System Architecture
- **Frontend**: HTML, CSS, JavaScript with Chart.js for data visualization
- **Backend**: Python Flask REST API
- **Database**: SQLite for development (easily upgradeable to PostgreSQL for production)
- **Deployment**: Can be deployed on any web server or cloud platform

## Prerequisites
- Python 3.8 or higher
- Node.js (optional, for advanced development)
- A web browser (Chrome, Firefox, Safari, Edge)
- Basic knowledge of command line operations

## Step 1: Project Setup

### 1.1 Create Project Directory
```bash
mkdir transport-optimizer
cd transport-optimizer
```

### 1.2 Download Files
Download and save the following files in your project directory:
- `frontend/index.html` (from the generated application)
- `frontend/style.css` (from the generated application)
- `frontend/app.js` (from the generated application)
- `backend_server.py` (backend API server)
- `database_schema.sql` (database schema)
- `requirements.txt` (Python dependencies)

## Step 2: Backend Setup

### 2.1 Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Initialize Database
The database will be automatically created when you first run the backend server. The system uses SQLite for simplicity.

### 2.3 Run Backend Server
```bash
python backend_server.py
```

The server will start on `http://localhost:5000`

## Step 3: Frontend Setup

### 3.1 Create Frontend Directory Structure
```
transport-optimizer/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend_server.py
├── requirements.txt
└── database_schema.sql
```

### 3.2 Serve Frontend Files
You have several options:

**Option A: Simple Python Server**
```bash
cd frontend
python -m http.server 8000
```
Then visit `http://localhost:8000`

**Option B: Node.js Live Server (if you have Node.js)**
```bash
npm install -g live-server
cd frontend
live-server
```

**Option C: Use any web server (Apache, Nginx, etc.)**

## Step 4: Configuration

### 4.1 Update API Endpoints
If your backend runs on a different port, update the API base URL in `app.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### 4.2 Database Configuration
The system uses SQLite by default. For production, you may want to upgrade to PostgreSQL:

1. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

2. Update database connection in `backend_server.py`:
```python
import psycopg2
# Replace sqlite3.connect() with PostgreSQL connection
```

## Step 5: Testing the System

### 5.1 Verify Backend API
Test the API endpoints:
```bash
# Test routes endpoint
curl http://localhost:5000/api/routes

# Test passenger demand
curl http://localhost:5000/api/passenger-demand/tp_pc

# Test dashboard stats
curl http://localhost:5000/api/dashboard-stats
```

### 5.2 Test Frontend
1. Open your browser and navigate to the frontend URL
2. Check that all sections load properly:
   - Dashboard with overview cards
   - Route Analytics with charts
   - Schedule Optimizer with recommendations
   - Reports section

## Step 6: System Features

### 6.1 Dashboard Features
- **Overview Cards**: Show total routes, buses, passengers, and savings
- **Route Selection**: Dropdown to select between three routes
- **Real-time Data**: Simulated real-time updates

### 6.2 Route Analytics Features
- **Passenger Demand Charts**: Hourly demand patterns
- **Peak Hour Analysis**: Morning (7-9 AM) and Evening (5-7 PM) peaks
- **Historical Trends**: 30-day historical data analysis

### 6.3 Schedule Optimizer Features
- **AI Recommendations**: Optimized bus frequencies based on demand
- **Cost Analysis**: Current vs optimized operational costs
- **Savings Calculator**: Fuel and operational cost savings

### 6.4 Reports Features
- **Efficiency Metrics**: Performance indicators
- **Cost-Benefit Analysis**: Financial impact of optimizations
- **Export Functionality**: Download reports as CSV/PDF

## Step 7: Data Management

### 7.1 Sample Data
The system comes with 30 days of sample passenger demand data for all three routes. This includes realistic peak hour patterns.

### 7.2 Adding Real Data
To integrate real passenger data:

1. **Manual Data Entry**: Use the database directly
```sql
INSERT INTO passenger_demand (route_id, hour, day_of_week, passenger_count, date_recorded)
VALUES ('tp_pc', 8, 1, 450, '2025-08-30');
```

2. **Batch Import**: Create a data import script
3. **API Integration**: Connect to existing ticketing systems

### 7.3 Data Backup
Regular database backups:
```bash
# SQLite backup
cp transport_optimizer.db backup_$(date +%Y%m%d).db
```

## Step 8: Deployment

### 8.1 Local Development
- Backend: `python backend_server.py`
- Frontend: `python -m http.server 8000`

### 8.2 Production Deployment

**Option A: Cloud Deployment (Heroku, AWS, Google Cloud)**
1. Create requirements.txt with all dependencies
2. Add Procfile for web process
3. Configure environment variables
4. Deploy using platform-specific tools

**Option B: VPS Deployment**
1. Set up Ubuntu/CentOS server
2. Install Python, Nginx
3. Configure reverse proxy
4. Set up SSL certificates

**Option C: Docker Deployment**
Create Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend_server.py"]
```

## Step 9: Customization

### 9.1 Adding New Routes
1. Update route data in `backend_server.py`
2. Add route to database
3. Update frontend dropdown options

### 9.2 Modifying Cost Parameters
Update cost parameters in the database:
```sql
UPDATE cost_parameters SET 
fuel_cost_per_km = 9.0,
driver_salary_per_hour = 130.0
WHERE id = 1;
```

### 9.3 Customizing UI
- Colors: Modify CSS variables in `style.css`
- Branding: Update logos and text
- Charts: Modify Chart.js configurations in `app.js`

## Step 10: Troubleshooting

### 10.1 Common Issues

**Backend won't start**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check port availability (5000)

**Frontend shows no data**
- Verify backend is running
- Check browser console for errors
- Confirm API endpoints are correct

**Database errors**
- Check database file permissions
- Verify SQLite is properly installed
- Check for disk space

### 10.2 Logs and Debugging
- Backend logs: Check Flask console output
- Frontend logs: Check browser developer console
- Database logs: Check SQLite error messages

## Step 11: Security Considerations

### 11.1 For Production
- Enable HTTPS
- Add authentication/authorization
- Input validation and sanitization
- Rate limiting
- Database security

### 11.2 Basic Security Measures
```python
# Add to Flask app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Step 12: Maintenance

### 12.1 Regular Tasks
- Database cleanup (old records)
- Log rotation
- Performance monitoring
- Security updates

### 12.2 Monitoring
- System uptime
- API response times
- Database performance
- User activity

## Support and Documentation

### API Documentation
- `/api/routes` - Get all routes
- `/api/passenger-demand/<route_id>` - Get demand data
- `/api/optimize-schedule` - POST optimization request
- `/api/dashboard-stats` - Get dashboard statistics

### Database Schema
- `routes` - Route master data
- `passenger_demand` - Hourly passenger counts
- `bus_schedules` - Current bus schedules
- `optimization_results` - Optimization history

## College Project Submission

### What to Submit
1. Complete source code (frontend + backend)
2. Database file with sample data
3. Setup instructions (this document)
4. Project report explaining the optimization algorithm
5. Screenshots of the working application
6. Video demonstration (optional)

### Project Report Structure
1. **Introduction** - Problem statement and objectives
2. **Literature Review** - Research on transport optimization
3. **System Design** - Architecture and technology stack
4. **Implementation** - Code structure and algorithms
5. **Results** - Performance analysis and cost savings
6. **Conclusion** - Achievements and future enhancements

### Demonstration Points
- Show all three routes working
- Demonstrate peak hour optimization
- Explain cost savings calculations
- Show real-time data updates
- Discuss scalability and future enhancements

## Future Enhancements

1. **Mobile App**: React Native or Flutter mobile application
2. **Real-time GPS**: Integration with bus GPS tracking
3. **Passenger App**: Mobile app for passengers to check schedules
4. **Advanced Analytics**: Machine learning for demand prediction
5. **Multi-city Support**: Expand beyond Tamil Nadu routes
6. **Integration**: Connect with existing transport management systems

This system provides a solid foundation for your college project and can be extended for real-world deployment in government transport departments.