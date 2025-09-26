# Kochi Metro Train Induction Planning System

A comprehensive prototype system for optimizing daily train induction decisions at Kochi Metro, addressing the complex challenge of deciding which trainsets enter revenue service, remain on standby, or undergo maintenance.

## Problem Statement

Kochi Metro must decide every night which of its 25 four-car trainsets will enter revenue service at dawn. The decision involves six inter-dependent variables:

1. **Fitness Certificates** - Validity windows from Rolling-Stock, Signalling, and Telecom departments
2. **Job-Card Status** - Open vs. closed work orders from IBM Maximo
3. **Branding Priorities** - Contractual commitments for exterior wrap exposure hours
4. **Mileage Balancing** - Kilometer allocation to equalize component wear
5. **Cleaning & Detailing Slots** - Available manpower and bay occupancy
6. **Stabling Geometry** - Physical positions to minimize shunting time

## Solution Architecture

### Backend (Python)
- **Flask API** - RESTful endpoints for data and optimization
- **OR-Tools** - Constraint optimization for induction planning
- **Pandas/NumPy** - Data processing and analysis
- **Mock Data Generators** - Simulated train fleet data

### Frontend (React)
- **React Dashboard** - Interactive visualization and control panel
- **Chart.js** - Real-time charts for fleet status and metrics
- **Tailwind CSS** - Modern, responsive UI design
- **Axios** - API communication

### Key Features
- **Real-time Optimization** - Multi-objective constraint solving
- **Interactive Dashboard** - Fleet status, alerts, and recommendations
- **What-if Simulation** - Scenario planning capabilities
- **Explainable AI** - Detailed reasoning for each decision
- **Predictive Maintenance** - Failure probability estimation

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## API Endpoints

### Core Operations
- `GET /api/health` - Health check
- `POST /api/data/refresh` - Refresh mock data
- `GET /api/trains` - Get all trains summary
- `GET /api/trains/{id}` - Get detailed train information
- `POST /api/optimize` - Run optimization algorithm

### Dashboard & Analytics
- `GET /api/dashboard/summary` - Dashboard summary data
- `GET /api/alerts` - Current alerts and recommendations
- `POST /api/simulation` - Run what-if scenarios

## System Components

### Decision Engine (`decision_engine.py`)
- **TrainInductionOptimizer** - Main optimization class using OR-Tools
- **Multi-objective scoring** - Readiness, branding, maintenance urgency
- **Constraint handling** - Expired certificates, critical jobs
- **Solution formatting** - Service/standby/maintenance allocation

### Mock Data Generator (`mock_data.py`)
- **Realistic fleet simulation** - 25 trainsets with varied conditions
- **Certificate management** - Multi-department fitness tracking
- **Job card system** - Priority-based maintenance workflow
- **Branding contracts** - Advertiser SLA compliance
- **Component wear modeling** - Mileage-based degradation

### React Dashboard (`Dashboard.js`)
- **Real-time visualization** - Fleet status and allocation charts
- **Interactive controls** - Optimization triggers and data refresh
- **Alert system** - Critical issues and recommendations
- **Responsive design** - Mobile and desktop compatibility

## Optimization Algorithm

The system uses OR-Tools SCIP solver with the following approach:

1. **Decision Variables**: Binary variables for each train (induct/don't induct)
2. **Hard Constraints**: 
   - Exact number of service trains required
   - No induction with expired certificates
   - No induction with critical open jobs
3. **Objective Function**: Weighted combination of:
   - Readiness score (50% weight)
   - Branding priority (30% weight)
   - Maintenance urgency (20% weight)

## Data Model

### Train States
- **Service**: Active revenue operation
- **Standby**: Ready for service if needed
- **Maintenance**: In Inspection Bay Line (IBL)

### Scoring Metrics
- **Readiness Score**: 0-100 based on certificates, jobs, component wear
- **Branding Priority**: Contract compliance requirements
- **Maintenance Urgency**: Cleaning due, mileage balancing needs

## Future Enhancements

### Phase 2 (Production Ready)
- **Real data integration** - IBM Maximo, IoT sensors, UNS streams
- **Advanced ML models** - XGBoost for predictive maintenance
- **Reinforcement learning** - Priority balancing optimization
- **Prophet forecasting** - Operational time estimation
- **Multi-depot support** - Scale to 40 trainsets across 2 depots

### Phase 3 (Advanced Features)
- **Historical learning** - Performance feedback loops
- **Real-time monitoring** - Live fleet status updates
- **Mobile application** - Field supervisor interface
- **Integration APIs** - Third-party system connectivity

## Technical Specifications

### Performance Targets
- **Optimization time**: < 30 seconds for 25 trains
- **API response time**: < 2 seconds average
- **Dashboard load time**: < 3 seconds
- **Data refresh rate**: Every 5 minutes

### Scalability
- **Current capacity**: 25 trainsets, single depot
- **Target capacity**: 40 trainsets, 2 depots by 2027
- **Concurrent users**: Up to 10 supervisors

## Development Notes

This is a prototype system using mock data. For production deployment:

1. Replace mock data generators with real system integrations
2. Implement proper authentication and authorization
3. Add comprehensive error handling and logging
4. Set up monitoring and alerting infrastructure
5. Implement data backup and recovery procedures

## License

This prototype is developed for Kochi Metro Rail Limited (KMRL) evaluation purposes.
