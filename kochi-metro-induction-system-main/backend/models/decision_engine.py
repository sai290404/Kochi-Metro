import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp
from datetime import datetime, timedelta
import logging

class TrainInductionOptimizer:
    def __init__(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.trains = []
        self.constraints = {}
        self.objectives = {}
        
    def load_data(self, data_dict):
        """Load all data sources for optimization"""
        self.fitness_certs = data_dict['fitness_certificates']
        self.job_cards = data_dict['job_cards']
        self.branding_data = data_dict['branding_data']
        self.mileage_data = data_dict['mileage_data']
        self.cleaning_schedule = data_dict['cleaning_schedule']
        self.stabling_positions = data_dict['stabling_positions']
        
        # Get unique train list
        self.trains = self.fitness_certs['train_id'].unique().tolist()
        
    def calculate_train_readiness_score(self, train_id):
        """Calculate overall readiness score for a train (0-100)"""
        score = 100
        
        # Check fitness certificates
        train_certs = self.fitness_certs[self.fitness_certs['train_id'] == train_id]
        expired_certs = len(train_certs[train_certs['status'] == 'Expired'])
        expiring_soon = len(train_certs[train_certs['status'] == 'Expiring Soon'])
        
        score -= expired_certs * 30  # Heavy penalty for expired certs
        score -= expiring_soon * 10  # Medium penalty for expiring soon
        
        # Check job cards
        train_jobs = self.job_cards[self.job_cards['train_id'] == train_id]
        open_jobs = train_jobs[train_jobs['status'].isin(['Open', 'In Progress'])]
        
        for _, job in open_jobs.iterrows():
            if job['priority'] == 'Critical':
                score -= 25
            elif job['priority'] == 'High':
                score -= 15
            elif job['priority'] == 'Medium':
                score -= 8
            else:
                score -= 3
        
        # Check component wear
        train_mileage = self.mileage_data[self.mileage_data['train_id'] == train_id]
        if not train_mileage.empty:
            wear_data = train_mileage.iloc[0]
            avg_wear = (wear_data['bogie_wear_percent'] + 
                       wear_data['brake_wear_percent'] + 
                       wear_data['hvac_wear_percent']) / 3
            score -= avg_wear * 0.2  # Reduce score based on wear
        
        return max(0, score)
    
    def calculate_branding_priority(self, train_id):
        """Calculate branding priority score"""
        train_brand = self.branding_data[self.branding_data['train_id'] == train_id]
        
        if train_brand.empty:
            return 0
        
        brand_info = train_brand.iloc[0]
        
        if brand_info['status'] == 'Below Target':
            return 50  # High priority to meet contractual obligations
        elif brand_info['status'] == 'Meeting Target':
            return 25  # Medium priority to maintain
        else:
            return 10  # Low priority if exceeding
    
    def calculate_maintenance_urgency(self, train_id):
        """Calculate maintenance urgency score"""
        urgency = 0
        
        # Check cleaning due
        cleaning_info = self.cleaning_schedule[self.cleaning_schedule['train_id'] == train_id]
        if not cleaning_info.empty and cleaning_info.iloc[0]['cleaning_due']:
            urgency += 20
        
        # Check mileage targets
        mileage_info = self.mileage_data[self.mileage_data['train_id'] == train_id]
        if not mileage_info.empty:
            current_km = mileage_info.iloc[0]['current_daily_km']
            target_km = mileage_info.iloc[0]['daily_target_km']
            
            if current_km < target_km * 0.8:
                urgency += 30  # Need more service to balance mileage
        
        return urgency
    
    def optimize_induction_plan(self, target_service_trains=20):
        """Main optimization function using simple greedy approach for prototype"""
        # For prototype, use a simple greedy algorithm instead of OR-Tools
        # This ensures we always get a solution
        
        # Calculate scores for all trains
        train_scores = []
        for train in self.trains:
            readiness_score = self.calculate_train_readiness_score(train)
            branding_priority = self.calculate_branding_priority(train)
            maintenance_urgency = self.calculate_maintenance_urgency(train)
            
            # Check for critical constraints
            train_jobs = self.job_cards[self.job_cards['train_id'] == train]
            critical_jobs = train_jobs[
                (train_jobs['status'].isin(['Open', 'In Progress'])) & 
                (train_jobs['priority'] == 'Critical')
            ]
            
            # Heavy penalty for expired certificates
            train_certs = self.fitness_certs[self.fitness_certs['train_id'] == train]
            expired_certs = len(train_certs[train_certs['status'] == 'Expired'])
            
            # Skip trains with critical jobs
            if len(critical_jobs) > 0:
                can_induct = False
            else:
                can_induct = True
            
            # Calculate total score
            total_score = (
                readiness_score * 0.5 +  # 50% weight on readiness
                branding_priority * 0.3 +  # 30% weight on branding
                maintenance_urgency * 0.2 -  # 20% weight on maintenance
                expired_certs * 25  # Penalty for expired certificates
            )
            
            train_scores.append({
                'train_id': train,
                'score': total_score,
                'can_induct': can_induct,
                'readiness': readiness_score,
                'branding': branding_priority,
                'maintenance': maintenance_urgency,
                'expired_certs': expired_certs,
                'critical_jobs': len(critical_jobs)
            })
        
        # Sort by score (highest first) and filter inductable trains
        inductable_trains = [t for t in train_scores if t['can_induct']]
        inductable_trains.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top trains for service
        actual_service_count = min(target_service_trains, len(inductable_trains))
        inducted_trains = [t['train_id'] for t in inductable_trains[:actual_service_count]]
        
        return self._format_solution_simple(inducted_trains)
    
    def _format_solution_simple(self, inducted_trains):
        """Format the simple greedy solution"""
        standby_trains = []
        maintenance_trains = []
        
        for train in self.trains:
            if train not in inducted_trains:
                # Determine if standby or maintenance
                train_jobs = self.job_cards[self.job_cards['train_id'] == train]
                open_jobs = train_jobs[train_jobs['status'].isin(['Open', 'In Progress'])]
                
                cleaning_info = self.cleaning_schedule[self.cleaning_schedule['train_id'] == train]
                needs_cleaning = not cleaning_info.empty and cleaning_info.iloc[0]['cleaning_due']
                
                if len(open_jobs) > 0 or needs_cleaning:
                    maintenance_trains.append(train)
                else:
                    standby_trains.append(train)
        
        return {
            'inducted_for_service': inducted_trains,
            'standby': standby_trains,
            'maintenance_ibl': maintenance_trains,
            'summary': {
                'service_count': len(inducted_trains),
                'standby_count': len(standby_trains),
                'maintenance_count': len(maintenance_trains)
            }
        }
    
    def _format_solution(self, decision_vars):
        """Format the optimization solution"""
        inducted_trains = []
        standby_trains = []
        maintenance_trains = []
        
        for train in self.trains:
            if decision_vars[train].solution_value() == 1:
                inducted_trains.append(train)
            else:
                # Determine if standby or maintenance
                train_jobs = self.job_cards[self.job_cards['train_id'] == train]
                open_jobs = train_jobs[train_jobs['status'].isin(['Open', 'In Progress'])]
                
                cleaning_info = self.cleaning_schedule[self.cleaning_schedule['train_id'] == train]
                needs_cleaning = not cleaning_info.empty and cleaning_info.iloc[0]['cleaning_due']
                
                if len(open_jobs) > 0 or needs_cleaning:
                    maintenance_trains.append(train)
                else:
                    standby_trains.append(train)
        
        return {
            'inducted_for_service': inducted_trains,
            'standby': standby_trains,
            'maintenance_ibl': maintenance_trains,
            'summary': {
                'service_count': len(inducted_trains),
                'standby_count': len(standby_trains),
                'maintenance_count': len(maintenance_trains)
            }
        }
    
    def generate_detailed_report(self, solution):
        """Generate detailed report with explanations"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'solution': solution,
            'train_details': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Generate details for each train
        for train in self.trains:
            readiness = self.calculate_train_readiness_score(train)
            branding = self.calculate_branding_priority(train)
            maintenance = self.calculate_maintenance_urgency(train)
            
            # Get train status
            status = 'standby'
            if train in solution['inducted_for_service']:
                status = 'service'
            elif train in solution['maintenance_ibl']:
                status = 'maintenance'
            
            # Get specific issues
            issues = []
            train_certs = self.fitness_certs[self.fitness_certs['train_id'] == train]
            expired_certs = train_certs[train_certs['status'] == 'Expired']
            
            if len(expired_certs) > 0:
                issues.append(f"Expired certificates: {', '.join(expired_certs['department'].tolist())}")
            
            train_jobs = self.job_cards[self.job_cards['train_id'] == train]
            critical_jobs = train_jobs[
                (train_jobs['status'].isin(['Open', 'In Progress'])) & 
                (train_jobs['priority'] == 'Critical')
            ]
            
            if len(critical_jobs) > 0:
                issues.append(f"Critical jobs: {len(critical_jobs)} open")
            
            report['train_details'][train] = {
                'status': status,
                'readiness_score': round(readiness, 1),
                'branding_priority': round(branding, 1),
                'maintenance_urgency': round(maintenance, 1),
                'issues': issues
            }
            
            # Generate alerts
            if readiness < 50 and status == 'service':
                report['alerts'].append(f"WARNING: {train} inducted with low readiness score ({readiness:.1f})")
            
            if len(expired_certs) > 0:
                report['alerts'].append(f"CRITICAL: {train} has expired certificates - cannot be inducted")
        
        # Generate recommendations
        if len(solution['standby']) < 3:
            report['recommendations'].append("Consider maintaining more standby trains for operational flexibility")
        
        if len(report['alerts']) > 5:
            report['recommendations'].append("High number of alerts - review maintenance scheduling")
        
        return report

class PredictiveMaintenanceModel:
    """Simple predictive maintenance using historical patterns"""
    
    def __init__(self):
        self.model = None
        
    def train_model(self, historical_data):
        """Train a simple model on historical performance data"""
        # For prototype, use simple rules-based approach
        # In production, this would use XGBoost or similar
        pass
    
    def predict_failure_probability(self, train_id, train_data):
        """Predict probability of failure in next 24 hours"""
        # Simple rule-based prediction for prototype
        prob = 0.1  # Base probability
        
        # Increase based on wear
        if 'bogie_wear_percent' in train_data:
            prob += train_data['bogie_wear_percent'] * 0.002
            prob += train_data['brake_wear_percent'] * 0.003
            prob += train_data['hvac_wear_percent'] * 0.001
        
        # Increase based on days since maintenance
        if 'days_since_maintenance' in train_data:
            prob += train_data['days_since_maintenance'] * 0.005
        
        return min(1.0, prob)

if __name__ == "__main__":
    # Test the optimizer
    from data_generators.mock_data import MockDataGenerator
    
    generator = MockDataGenerator()
    data = generator.generate_all_data()
    
    optimizer = TrainInductionOptimizer()
    optimizer.load_data(data)
    
    solution = optimizer.optimize_induction_plan(target_service_trains=18)
    if solution:
        report = optimizer.generate_detailed_report(solution)
        print("Optimization successful!")
        print(f"Service: {len(solution['inducted_for_service'])} trains")
        print(f"Standby: {len(solution['standby'])} trains") 
        print(f"Maintenance: {len(solution['maintenance_ibl'])} trains")
    else:
        print("Optimization failed!")