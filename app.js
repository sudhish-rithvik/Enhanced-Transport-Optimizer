// Advanced Transport Optimization System JavaScript

// Application Data with Enhanced Predictions
const appData = {
  current_date: "2025-08-30",
  current_time: "16:34",
  timezone: "IST",
  routes: [
    {
      id: "tp_pc",
      name: "Tiruppur to Pollachi",
      distance: 85,
      travel_time: 120,
      current_buses: 12,
      daily_passengers: 2800,
      market_days: [1, 4],
      route_type: "Industrial/Agricultural"
    },
    {
      id: "tp_cb",
      name: "Tiruppur to Coimbatore", 
      distance: 65,
      travel_time: 90,
      current_buses: 18,
      daily_passengers: 4200,
      market_days: [0, 2, 5],
      route_type: "Commercial"
    },
    {
      id: "tp_sl",
      name: "Tiruppur to Salem",
      distance: 113,
      travel_time: 150,
      current_buses: 15,
      daily_passengers: 3500,
      market_days: [2, 5],
      route_type: "Mixed Commercial/Industrial"
    }
  ],
  weather_data: {
    current_temp: 32,
    condition: "Partly Cloudy",
    humidity: 68,
    rainfall: 0,
    weather_factor: 1.0,
    forecast_tomorrow: {
      temp: 29,
      condition: "Light Rain",
      humidity: 78,
      rainfall: 8,
      weather_factor: 1.15
    }
  },
  festivals: {
    today: {
      is_festival: false,
      name: null,
      impact: 1.0
    },
    tomorrow: {
      is_festival: false,
      name: null,
      impact: 1.0
    },
    upcoming: [
      {"date": "2025-09-01", "name": "Vinayaka Chaturthi", "impact": 1.6, "days_away": 2},
      {"date": "2025-09-17", "name": "Onam", "impact": 1.4, "days_away": 18},
      {"date": "2025-10-02", "name": "Gandhi Jayanti", "impact": 1.3, "days_away": 33}
    ]
  },
  today_actual_data: {
    tp_pc: [35, 25, 15, 10, 20, 60, 140, 380, 320, 180, 150, 130, 115, 100, 90, 75, 220, 0, 0, 0, 0, 0, 0, 0],
    tp_cb: [50, 35, 25, 20, 30, 90, 200, 580, 460, 280, 220, 190, 165, 145, 125, 110, 320, 0, 0, 0, 0, 0, 0, 0],
    tp_sl: [40, 30, 22, 18, 28, 75, 175, 440, 380, 240, 195, 165, 145, 125, 110, 95, 280, 0, 0, 0, 0, 0, 0, 0]
  },
  today_predicted_data: {
    tp_pc: [38, 28, 18, 12, 22, 65, 145, 400, 335, 190, 160, 135, 120, 105, 95, 80, 230, 470, 365, 250, 145, 95, 65, 48],
    tp_cb: [55, 38, 28, 22, 33, 95, 210, 610, 485, 295, 235, 200, 175, 155, 135, 115, 340, 650, 545, 380, 235, 160, 95, 75],
    tp_sl: [45, 33, 25, 20, 30, 80, 185, 465, 400, 255, 210, 175, 155, 135, 118, 100, 295, 525, 420, 310, 200, 135, 80, 60]
  },
  tomorrow_predictions: {
    tp_pc: [40, 30, 20, 12, 25, 70, 155, 420, 350, 200, 170, 140, 125, 110, 100, 85, 250, 490, 385, 265, 155, 105, 70, 52],
    tp_cb: [58, 40, 30, 24, 35, 100, 220, 640, 510, 310, 250, 210, 185, 165, 145, 125, 360, 680, 570, 400, 250, 170, 105, 80],
    tp_sl: [48, 35, 27, 22, 32, 85, 195, 485, 420, 270, 220, 185, 165, 145, 125, 105, 310, 550, 440, 325, 210, 145, 85, 65]
  },
  system_status: {
    last_update: "2025-08-30T16:30:00",
    next_update: "2025-08-31T23:30:00",
    prediction_accuracy: 87.3,
    system_health: "Excellent",
    auto_updates: true
  },
  operational_costs: {
    fuel_per_km: 8.5,
    driver_salary_per_hour: 120,
    maintenance_per_km: 3.2,
    bus_capacity: 45
  }
};

// Global variables
let currentAnalyticsRoute = 'tp_pc';
let comparisonChart = null;
let accuracyChart = null;
let allocationChart = null;
let updateInterval = null;
let clockInterval = null;
let currentTime = new Date();

// Wait for DOM to be fully loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}

function initializeApp() {
  console.log('Initializing Advanced Transport System...');
  
  // Initialize core functions with delays to ensure DOM is ready
  setTimeout(() => {
    setupNavigation();
    setupDateTime();
    setupRouteSelectors();
    setupModalHandlers();
    updateDashboard();
    
    // Create charts after a short delay
    setTimeout(() => {
      createAllCharts();
    }, 1000);
    
    startRealTimeUpdates();
    simulateSystemUpdates();
    
    console.log('Advanced Transport System initialized successfully');
  }, 100);
}

// FIXED Navigation Setup with better error handling
function setupNavigation() {
  console.log('Setting up navigation...');
  
  // Wait a bit more to ensure DOM is ready
  setTimeout(() => {
    const navBtns = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    console.log('Found navigation buttons:', navBtns.length);
    console.log('Found sections:', sections.length);
    
    if (navBtns.length === 0) {
      console.error('No navigation buttons found!');
      return;
    }
    
    if (sections.length === 0) {
      console.error('No sections found!');
      return;
    }
    
    // Add click handlers to navigation buttons
    navBtns.forEach((btn, index) => {
      const targetSection = btn.getAttribute('data-section');
      console.log(`Setting up button ${index}: "${btn.textContent}" -> section "${targetSection}"`);
      
      if (!targetSection) {
        console.error('Button missing data-section attribute:', btn);
        return;
      }
      
      // Remove any existing listeners and add new one
      btn.removeEventListener('click', handleNavigation);
      btn.addEventListener('click', handleNavigation);
    });
    
    console.log('Navigation setup complete');
  }, 200);
}

// Navigation handler function
function handleNavigation(e) {
  e.preventDefault();
  e.stopPropagation();
  
  const targetSection = this.getAttribute('data-section');
  console.log('Navigation clicked:', targetSection);
  
  if (!targetSection) {
    console.error('No target section specified');
    return;
  }
  
  // Update active navigation button
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach(btn => btn.classList.remove('active'));
  this.classList.add('active');
  
  // Show target section
  const sections = document.querySelectorAll('.section');
  let sectionFound = false;
  
  sections.forEach(section => {
    section.classList.remove('active');
    
    if (section.id === targetSection) {
      section.classList.add('active');
      sectionFound = true;
      console.log('Showing section:', targetSection);
      
      // Handle section-specific initialization
      handleSectionSwitch(targetSection);
    }
  });
  
  if (!sectionFound) {
    console.error('Target section not found:', targetSection);
  }
}

// Handle section-specific logic when switching
function handleSectionSwitch(sectionId) {
  console.log('Switched to section:', sectionId);
  
  // Add delay to ensure section is visible before updating charts
  setTimeout(() => {
    switch (sectionId) {
      case 'analytics':
        refreshAnalyticsCharts();
        break;
      case 'scheduler':
        refreshSchedulerCharts();
        break;
      case 'recommendations':
        console.log('Recommendations section loaded');
        break;
      case 'external':
        console.log('External factors section loaded');
        break;
      default:
        console.log('Dashboard section loaded');
    }
  }, 300);
}

// Enhanced Date and Time Display
function setupDateTime() {
  function updateDateTime() {
    currentTime = new Date();
    
    const options = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    
    const dateStr = currentTime.toLocaleDateString('en-US', options);
    const timeStr = currentTime.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: 'Asia/Kolkata'
    }) + ' IST';
    
    updateElementText('current-date', dateStr);
    updateElementText('current-time', timeStr);
    updateRefreshCountdown();
  }
  
  updateDateTime();
  clockInterval = setInterval(updateDateTime, 1000);
}

function updateRefreshCountdown() {
  const nextUpdateEl = document.getElementById('next-update');
  if (!nextUpdateEl) return;
  
  const now = Math.floor(Date.now() / 1000);
  const nextUpdate = now + (30 - (now % 30));
  const countdown = nextUpdate - now;
  
  const minutes = Math.floor(countdown / 60);
  const seconds = countdown % 60;
  
  nextUpdateEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Route Selectors Setup
function setupRouteSelectors() {
  const analyticsRouteSelect = document.getElementById('analytics-route');
  
  if (analyticsRouteSelect) {
    analyticsRouteSelect.addEventListener('change', function(e) {
      currentAnalyticsRoute = e.target.value;
      console.log('Analytics route changed to:', currentAnalyticsRoute);
      refreshAnalyticsCharts();
      updateRouteMetrics();
    });
  }
}

// Modal Handlers Setup
function setupModalHandlers() {
  // Use event delegation for better reliability
  document.addEventListener('click', function(e) {
    
    // Approve Schedule Button
    if (e.target.id === 'approve-schedule') {
      e.preventDefault();
      console.log('Approve schedule clicked');
      showApprovalModal();
      return;
    }
    
    // Modify Schedule Button  
    if (e.target.id === 'modify-schedule') {
      e.preventDefault();
      alert('Schedule modification interface would be implemented here.');
      return;
    }
    
    // Close Modal Buttons
    if (e.target.id === 'close-approval-modal') {
      e.preventDefault();
      hideApprovalModal();
      return;
    }
    
    // Confirm Deployment Button
    if (e.target.id === 'confirm-deployment') {
      e.preventDefault();
      deploySchedule();
      return;
    }
    
    // Modal overlay clicks
    if (e.target.classList.contains('modal-overlay') || e.target.classList.contains('modal')) {
      const modal = e.target.closest('.modal');
      if (modal) {
        modal.classList.add('hidden');
      }
      return;
    }
    
    // Recommendation buttons
    if (e.target.matches('.recommendation-card .btn--primary')) {
      e.preventDefault();
      const card = e.target.closest('.recommendation-card');
      const title = card.querySelector('h4').textContent;
      console.log(`Implementing recommendation: ${title}`);
      
      e.target.textContent = 'Implemented ✓';
      e.target.disabled = true;
      e.target.classList.remove('btn--primary');
      e.target.classList.add('btn--secondary');
      return;
    }
    
    if (e.target.matches('.recommendation-card .btn--outline')) {
      e.preventDefault();
      const card = e.target.closest('.recommendation-card');
      const title = card.querySelector('h4').textContent;
      alert(`Opening detailed review for: ${title}`);
      return;
    }
  });
}

// Dashboard Updates
function updateDashboard() {
  updateMetrics();
  updateRouteCards();
  updateTomorrowPreview();
  updateSystemStatus();
}

function updateMetrics() {
  const currentHour = currentTime.getHours();
  const totalPassengers = Object.values(appData.today_actual_data).reduce((sum, route) => {
    return sum + route.slice(0, currentHour + 1).reduce((a, b) => a + b, 0);
  }, 0);
  
  const totalBuses = appData.routes.reduce((sum, route) => sum + route.current_buses, 0);
  
  // Calculate performance vs prediction
  let totalActual = 0;
  let totalPredicted = 0;
  
  Object.keys(appData.today_actual_data).forEach(routeId => {
    const actual = appData.today_actual_data[routeId].slice(0, currentHour + 1).reduce((a, b) => a + b, 0);
    const predicted = appData.today_predicted_data[routeId].slice(0, currentHour + 1).reduce((a, b) => a + b, 0);
    totalActual += actual;
    totalPredicted += predicted;
  });
  
  const performanceRatio = totalPredicted > 0 ? (totalActual / totalPredicted) * 100 : 100;
  
  // Update metric displays
  updateElementText('today-performance', `${performanceRatio.toFixed(1)}%`);
  updateElementText('active-buses', totalBuses.toString());
  updateElementText('passengers-served', totalPassengers.toLocaleString());
  
  // Update trends
  const performanceTrend = document.getElementById('performance-trend');
  const passengerTrend = document.getElementById('passenger-trend');
  
  if (performanceTrend) {
    const trendValue = (performanceRatio - 100).toFixed(1);
    performanceTrend.textContent = `${trendValue > 0 ? '+' : ''}${trendValue}%`;
    performanceTrend.className = `metric-trend ${trendValue >= 0 ? 'up' : 'down'}`;
  }
  
  if (passengerTrend) {
    passengerTrend.textContent = '+12.8%';
    passengerTrend.className = 'metric-trend up';
  }
}

function updateRouteCards() {
  appData.routes.forEach(route => {
    const currentHour = currentTime.getHours();
    const actualData = appData.today_actual_data[route.id];
    const predictedData = appData.today_predicted_data[route.id];
    
    // Calculate current load (last hour)
    const currentLoad = actualData[currentHour] || 0;
    const capacity = route.current_buses * appData.operational_costs.bus_capacity;
    const loadPercentage = Math.min(100, (currentLoad / capacity * 100)).toFixed(0);
    
    // Calculate accuracy
    const actualSum = actualData.slice(0, currentHour + 1).reduce((a, b) => a + b, 0);
    const predictedSum = predictedData.slice(0, currentHour + 1).reduce((a, b) => a + b, 0);
    const accuracy = predictedSum > 0 ? ((1 - Math.abs(actualSum - predictedSum) / predictedSum) * 100).toFixed(0) : 100;
    
    // Update route-specific elements
    const routeCode = route.id.split('_')[1];
    updateElementText(`${routeCode}-load`, `${loadPercentage}%`);
    updateElementText(`${routeCode}-accuracy`, `${accuracy}%`);
    updateElementText(`${routeCode}-next`, `${Math.floor(Math.random() * 20) + 5} min`);
  });
}

function updateTomorrowPreview() {
  const weatherFactor = appData.weather_data.forecast_tomorrow.weather_factor;
  const totalCurrentBuses = appData.routes.reduce((sum, route) => sum + route.current_buses, 0);
  const recommendedBuses = Math.ceil(totalCurrentBuses * weatherFactor);
  
  updateElementText('tomorrow-buses', recommendedBuses.toString());
}

function updateSystemStatus() {
  const statusEl = document.getElementById('system-status');
  if (statusEl) {
    const indicator = statusEl.querySelector('.status-indicator');
    if (indicator) {
      indicator.className = 'status-indicator online';
    }
  }
}

// Chart Creation and Management
function createAllCharts() {
  console.log('Creating all charts...');
  
  // Add small delays between chart creation
  setTimeout(() => createComparisonChart(), 100);
  setTimeout(() => createAccuracyChart(), 200);
  setTimeout(() => createAllocationChart(), 300);
}

function createComparisonChart() {
  const canvas = document.getElementById('comparison-chart');
  if (!canvas) {
    console.log('Comparison chart canvas not found, will create when analytics section is accessed');
    return;
  }
  
  console.log('Creating comparison chart');
  const ctx = canvas.getContext('2d');
  
  const hours = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  
  if (comparisonChart) {
    comparisonChart.destroy();
  }
  
  comparisonChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [
        {
          label: 'Today (Actual)',
          data: appData.today_actual_data[currentAnalyticsRoute],
          borderColor: '#1FB8CD',
          backgroundColor: 'rgba(31, 184, 205, 0.1)',
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 3
        },
        {
          label: 'Today (Predicted)',
          data: appData.today_predicted_data[currentAnalyticsRoute],
          borderColor: '#FFC185',
          backgroundColor: 'rgba(255, 193, 133, 0.1)',
          fill: false,
          tension: 0.4,
          pointRadius: 2,
          borderWidth: 2,
          borderDash: [5, 5]
        },
        {
          label: 'Tomorrow (Forecast)',
          data: appData.tomorrow_predictions[currentAnalyticsRoute],
          borderColor: '#B4413C',
          backgroundColor: 'rgba(180, 65, 60, 0.1)',
          fill: false,
          tension: 0.4,
          pointRadius: 2,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time (24-hour format)'
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Passengers per Hour'
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    }
  });
  
  console.log('Comparison chart created successfully');
}

function createAccuracyChart() {
  const canvas = document.getElementById('accuracy-chart');
  if (!canvas) {
    console.log('Accuracy chart canvas not found, will create when analytics section is accessed');
    return;
  }
  
  console.log('Creating accuracy chart');
  const ctx = canvas.getContext('2d');
  
  if (accuracyChart) {
    accuracyChart.destroy();
  }
  
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const accuracyData = [85.2, 87.8, 89.1, 86.5, 88.9, 90.2, 87.3];
  
  accuracyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: days,
      datasets: [{
        label: 'Prediction Accuracy (%)',
        data: accuracyData,
        borderColor: '#1FB8CD',
        backgroundColor: 'rgba(31, 184, 205, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          min: 80,
          max: 95,
          title: {
            display: true,
            text: 'Accuracy (%)'
          }
        }
      }
    }
  });
  
  console.log('Accuracy chart created successfully');
}

function createAllocationChart() {
  const canvas = document.getElementById('allocation-chart');
  if (!canvas) {
    console.log('Allocation chart canvas not found, will create when scheduler section is accessed');
    return;
  }
  
  console.log('Creating allocation chart');
  const ctx = canvas.getContext('2d');
  
  if (allocationChart) {
    allocationChart.destroy();
  }
  
  const hours = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const allocationData = [8, 6, 4, 3, 5, 12, 25, 35, 32, 20, 18, 15, 14, 13, 12, 11, 28, 38, 35, 25, 18, 15, 12, 10];
  
  allocationChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: hours,
      datasets: [{
        label: 'Buses Required',
        data: allocationData,
        backgroundColor: '#1FB8CD',
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time (24-hour format)'
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Buses'
          }
        }
      }
    }
  });
  
  console.log('Allocation chart created successfully');
}

// Chart Refresh Functions
function refreshAnalyticsCharts() {
  console.log('Refreshing analytics charts for route:', currentAnalyticsRoute);
  
  // Create chart if it doesn't exist yet
  if (!comparisonChart) {
    setTimeout(createComparisonChart, 100);
  } else {
    comparisonChart.data.datasets[0].data = appData.today_actual_data[currentAnalyticsRoute];
    comparisonChart.data.datasets[1].data = appData.today_predicted_data[currentAnalyticsRoute];
    comparisonChart.data.datasets[2].data = appData.tomorrow_predictions[currentAnalyticsRoute];
    comparisonChart.update();
    console.log('Comparison chart updated');
  }
  
  if (!accuracyChart) {
    setTimeout(createAccuracyChart, 200);
  }
  
  updateConfidenceScore();
}

function refreshSchedulerCharts() {
  console.log('Refreshing scheduler charts');
  
  // Create chart if it doesn't exist yet
  if (!allocationChart) {
    setTimeout(createAllocationChart, 100);
  } else {
    // Simulate dynamic allocation based on current conditions
    const baseAllocation = [8, 6, 4, 3, 5, 12, 25, 35, 32, 20, 18, 15, 14, 13, 12, 11, 28, 38, 35, 25, 18, 15, 12, 10];
    const weatherAdjustment = appData.weather_data.forecast_tomorrow.weather_factor;
    const adjustedAllocation = baseAllocation.map(val => Math.ceil(val * weatherAdjustment));
    
    allocationChart.data.datasets[0].data = adjustedAllocation;
    allocationChart.update();
    console.log('Allocation chart updated with weather adjustment:', weatherAdjustment);
  }
}

function updateConfidenceScore() {
  const route = appData.routes.find(r => r.id === currentAnalyticsRoute);
  if (!route) return;
  
  // Calculate confidence based on historical accuracy and current conditions
  let baseConfidence = appData.system_status.prediction_accuracy;
  
  // Adjust for weather uncertainty
  if (appData.weather_data.forecast_tomorrow.rainfall > 0) {
    baseConfidence -= 5;
  }
  
  // Adjust for market days
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const dayOfWeek = tomorrow.getDay();
  
  if (route.market_days.includes(dayOfWeek)) {
    baseConfidence -= 3;
  }
  
  const confidenceScore = Math.max(70, Math.min(95, baseConfidence)).toFixed(1);
  updateElementText('confidence-score', `${confidenceScore}%`);
}

// Modal Functions
function showApprovalModal() {
  const modal = document.getElementById('approval-modal');
  if (modal) {
    modal.classList.remove('hidden');
    console.log('Approval modal shown');
  }
}

function hideApprovalModal() {
  const modal = document.getElementById('approval-modal');
  if (modal) {
    modal.classList.add('hidden');
    console.log('Approval modal hidden');
  }
}

function deploySchedule() {
  // Simulate deployment process
  const confirmBtn = document.getElementById('confirm-deployment');
  if (confirmBtn) {
    confirmBtn.textContent = 'Deploying...';
    confirmBtn.disabled = true;
    
    setTimeout(() => {
      confirmBtn.textContent = 'Deployed Successfully ✓';
      setTimeout(() => {
        hideApprovalModal();
      }, 2000);
    }, 2000);
  }
}

// Real-time Updates and Simulations
function startRealTimeUpdates() {
  // Update metrics every 30 seconds
  updateInterval = setInterval(() => {
    simulateDataUpdates();
    updateDashboard();
    updateRouteMetrics();
  }, 30000);
}

function simulateSystemUpdates() {
  // Simulate system health monitoring
  setInterval(() => {
    const variations = ['Excellent', 'Good', 'Fair'];
    const randomHealth = variations[Math.floor(Math.random() * variations.length)];
    
    // Update prediction accuracy with slight variations
    const currentAccuracy = appData.system_status.prediction_accuracy;
    const variation = (Math.random() - 0.5) * 2; // -1 to +1
    appData.system_status.prediction_accuracy = Math.max(75, Math.min(95, currentAccuracy + variation));
    
  }, 60000); // Every minute
}

function simulateDataUpdates() {
  const currentHour = currentTime.getHours();
  
  // Update current hour data with small variations
  Object.keys(appData.today_actual_data).forEach(routeId => {
    const currentValue = appData.today_actual_data[routeId][currentHour];
    if (currentValue > 0) {
      const variation = Math.floor((Math.random() - 0.5) * 20); // -10 to +10
      appData.today_actual_data[routeId][currentHour] = Math.max(0, currentValue + variation);
    }
  });
}

function updateRouteMetrics() {
  // Update live route performance indicators
  const routes = ['pc', 'cb', 'sl'];
  routes.forEach(routeCode => {
    const nextBusTime = Math.floor(Math.random() * 25) + 5;
    updateElementText(`${routeCode}-next`, `${nextBusTime} min`);
  });
}

// Utility Functions
function updateElementText(id, text) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = text;
  } else {
    console.log(`Element with id '${id}' not found`);
  }
}

// Cleanup function
function cleanup() {
  if (updateInterval) clearInterval(updateInterval);
  if (clockInterval) clearInterval(clockInterval);
  
  // Destroy charts
  if (comparisonChart) comparisonChart.destroy();
  if (accuracyChart) accuracyChart.destroy();
  if (allocationChart) allocationChart.destroy();
}

// Handle page unload
window.addEventListener('beforeunload', cleanup);

console.log('Advanced Transport Optimization System JavaScript loaded successfully');