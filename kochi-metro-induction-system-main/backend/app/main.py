from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_engine import TrainInductionOptimizer, PredictiveMaintenanceModel
from data_generators.mock_data import MockDataGenerator

app = Flask(__name__)

# ✅ Allow frontend domain (Netlify)
CORS(app, resources={r"/api/*": {"origins": "https://your-netlify-site.netlify.app"}})

# Global variables to store data and models
data_generator = MockDataGenerator()
optimizer = TrainInductionOptimizer()
ml_model = PredictiveMaintenanceModel()
current_data = None
current_solution = None

def initialize_data():
    """Initialize mock data and load into optimizer"""
    global current_data
    current_data = data_generator.generate_all_data()
    optimizer.load_data(current_data)
    return current_data


# ================== ROUTES ================== #

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Kochi Metro Induction System API"})


@app.route('/api/data/refresh', methods=['POST'])
def refresh_data():
    try:
        data = initialize_data()
        return jsonify({
            "status": "success",
            "message": "Data refreshed successfully",
            "summary": {
                "trains": len(data['fitness_certificates']['train_id'].unique()),
                "fitness_certificates": len(data['fitness_certificates']),
                "job_cards": len(data['job_cards']),
                "branding_contracts": len(data['branding_data'])
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/trains', methods=['GET'])
def get_trains():
    if current_data is None:
        initialize_data()
    try:
        trains_summary = []
        for train_id in current_data['fitness_certificates']['train_id'].unique():
            readiness = optimizer.calculate_train_readiness_score(train_id)
            branding = optimizer.calculate_branding_priority(train_id)
            maintenance = optimizer.calculate_maintenance_urgency(train_id)

            status = "Unknown"
            if current_solution:
                if train_id in current_solution['inducted_for_service']:
                    status = "Service"
                elif train_id in current_solution['standby']:
                    status = "Standby"
                elif train_id in current_solution['maintenance_ibl']:
                    status = "Maintenance"

            issues = []
            train_certs = current_data['fitness_certificates'][current_data['fitness_certificates']['train_id'] == train_id]
            expired_certs = len(train_certs[train_certs['status'] == 'Expired'])
            if expired_certs > 0:
                issues.append(f"{expired_certs} expired certificates")

            train_jobs = current_data['job_cards'][current_data['job_cards']['train_id'] == train_id]
            open_jobs = len(train_jobs[train_jobs['status'].isin(['Open', 'In Progress'])])
            if open_jobs > 0:
                issues.append(f"{open_jobs} open jobs")

            trains_summary.append({
                "train_id": train_id,
                "status": status,
                "readiness_score": round(readiness, 1),
                "branding_priority": round(branding, 1),
                "maintenance_urgency": round(maintenance, 1),
                "issues": issues
            })

        return jsonify({
            "status": "success",
            "trains": trains_summary,
            "total_count": len(trains_summary)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/trains/<train_id>', methods=['GET'])
def get_train_details(train_id):
    if current_data is None:
        initialize_data()
    try:
        certs = current_data['fitness_certificates'][current_data['fitness_certificates']['train_id'] == train_id]
        jobs = current_data['job_cards'][current_data['job_cards']['train_id'] == train_id]
        branding = current_data['branding_data'][current_data['branding_data']['train_id'] == train_id]
        mileage = current_data['mileage_data'][current_data['mileage_data']['train_id'] == train_id]
        cleaning = current_data['cleaning_schedule'][current_data['cleaning_schedule']['train_id'] == train_id]
        stabling = current_data['stabling_positions'][current_data['stabling_positions']['train_id'] == train_id]

        return jsonify({
            "status": "success",
            "train_id": train_id,
            "fitness_certificates": certs.to_dict('records'),
            "job_cards": jobs.to_dict('records'),
            "branding_data": branding.to_dict('records'),
            "mileage_data": mileage.to_dict('records'),
            "cleaning_schedule": cleaning.to_dict('records'),
            "stabling_positions": stabling.to_dict('records'),
            "readiness_score": optimizer.calculate_train_readiness_score(train_id),
            "branding_priority": optimizer.calculate_branding_priority(train_id),
            "maintenance_urgency": optimizer.calculate_maintenance_urgency(train_id)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_induction():
    if current_data is None:
        initialize_data()
    try:
        data = request.get_json() or {}
        target_service_trains = data.get('target_service_trains', 18)

        global current_solution
        current_solution = optimizer.optimize_induction_plan(target_service_trains)

        if current_solution is None:
            return jsonify({
                "status": "error",
                "message": "Optimization failed - no feasible solution found"
            }), 400

        report = optimizer.generate_detailed_report(current_solution)

        return jsonify({
            "status": "success",
            "solution": current_solution,
            "report": report,
            "optimization_params": {
                "target_service_trains": target_service_trains,
                "total_trains": len(optimizer.trains)
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    if current_data is None:
        initialize_data()
    try:
        total_trains = len(current_data['fitness_certificates']['train_id'].unique())
        cert_summary = current_data['fitness_certificates']['status'].value_counts().to_dict()
        job_summary = current_data['job_cards']['priority'].value_counts().to_dict()
        brand_summary = current_data['branding_data']['status'].value_counts().to_dict()

        solution_summary = {}
        alerts_count = 0
        if current_solution:
            solution_summary = current_solution['summary']
            report = optimizer.generate_detailed_report(current_solution)
            alerts_count = len(report['alerts'])

        return jsonify({
            "status": "success",
            "summary": {
                "total_trains": total_trains,
                "certificate_status": cert_summary,
                "job_priorities": job_summary,
                "branding_status": brand_summary,
                "current_allocation": solution_summary,
                "alerts_count": alerts_count,
                "last_optimization": current_solution is not None
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    if current_data is None:
        initialize_data()
    try:
        if current_solution is None:
            return jsonify({
                "status": "success",
                "alerts": [],
                "recommendations": ["Run optimization to generate alerts and recommendations"]
            })

        report = optimizer.generate_detailed_report(current_solution)

        return jsonify({
            "status": "success",
            "alerts": report['alerts'],
            "recommendations": report['recommendations'],
            "timestamp": report['timestamp']
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    if current_data is None:
        initialize_data()
    try:
        data = request.get_json() or {}
        scenarios = data.get('scenarios', [])

        results = []
        for scenario in scenarios:
            target_trains = scenario.get('target_service_trains', 18)
            scenario_name = scenario.get('name', f'Scenario {len(results) + 1}')

            temp_solution = optimizer.optimize_induction_plan(target_trains)
            if temp_solution:
                temp_report = optimizer.generate_detailed_report(temp_solution)
                results.append({
                    "scenario_name": scenario_name,
                    "parameters": {"target_service_trains": target_trains},
                    "solution": temp_solution,
                    "alerts_count": len(temp_report['alerts']),
                    "recommendations_count": len(temp_report['recommendations'])
                })
            else:
                results.append({
                    "scenario_name": scenario_name,
                    "parameters": {"target_service_trains": target_trains},
                    "solution": None,
                    "error": "No feasible solution"
                })

        return jsonify({
            "status": "success",
            "simulation_results": results
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ================== ENTRYPOINT ================== #

if __name__ == '__main__':
    initialize_data()
    port = int(os.environ.get("PORT", 5001))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    print("Starting Kochi Metro Induction System API...")
    print("Initializing with mock data...")
    print(f"Loaded data for {len(current_data['fitness_certificates']['train_id'].unique())} trains")

    app.run(host='0.0.0.0', port=port, debug=debug_mode)
