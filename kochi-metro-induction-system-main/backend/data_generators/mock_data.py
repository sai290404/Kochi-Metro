import random
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class MockDataGenerator:
    def __init__(self):
        self.train_ids = [f"KMRL-{str(i).zfill(3)}" for i in range(1, 26)]  # 25 trainsets
        self.departments = ["Rolling-Stock", "Signalling", "Telecom"]
        self.brands = ["Coca-Cola", "Samsung", "Airtel", "BSNL", "Kerala Tourism"]
        
    def generate_fitness_certificates(self):
        """Generate fitness certificate data for all trains"""
        data = []
        for train_id in self.train_ids:
            for dept in self.departments:
                # Random validity window (some expired, some valid, some expiring soon)
                days_offset = random.randint(-10, 30)
                issue_date = datetime.now() - timedelta(days=random.randint(1, 60))
                expiry_date = issue_date + timedelta(days=random.randint(30, 90))
                
                status = "Valid"
                if expiry_date < datetime.now():
                    status = "Expired"
                elif expiry_date < datetime.now() + timedelta(days=7):
                    status = "Expiring Soon"
                
                data.append({
                    "train_id": train_id,
                    "department": dept,
                    "certificate_id": f"{dept[:2]}-{train_id}-{random.randint(1000, 9999)}",
                    "issue_date": issue_date.strftime("%Y-%m-%d"),
                    "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "inspector": f"Inspector {random.choice(['A', 'B', 'C', 'D'])}"
                })
        
        return pd.DataFrame(data)
    
    def generate_job_cards(self):
        """Generate job card data from maintenance system"""
        data = []
        for train_id in self.train_ids:
            # Each train might have 0-3 open job cards
            num_jobs = random.randint(0, 3)
            for i in range(num_jobs):
                priority = random.choice(["Low", "Medium", "High", "Critical"])
                status = random.choice(["Open", "In Progress", "Closed"])
                
                # Critical jobs are more likely to be open
                if priority == "Critical":
                    status = random.choice(["Open", "In Progress"])
                
                data.append({
                    "train_id": train_id,
                    "job_card_id": f"JC-{random.randint(10000, 99999)}",
                    "description": random.choice([
                        "Brake pad replacement", "HVAC filter change", "Door mechanism check",
                        "Bogie inspection", "Electrical system check", "Interior cleaning",
                        "Exterior wash", "Signal system calibration"
                    ]),
                    "priority": priority,
                    "status": status,
                    "estimated_hours": random.randint(1, 8),
                    "assigned_to": f"Tech {random.choice(['Team A', 'Team B', 'Team C'])}",
                    "created_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                })
        
        return pd.DataFrame(data)
    
    def generate_branding_data(self):
        """Generate branding priority data"""
        data = []
        for train_id in self.train_ids:
            # Some trains have branding, some don't
            if random.random() > 0.3:  # 70% chance of having branding
                brand = random.choice(self.brands)
                contract_start = datetime.now() - timedelta(days=random.randint(30, 365))
                contract_end = contract_start + timedelta(days=random.randint(90, 730))
                
                # Required exposure hours per day
                required_hours = random.randint(8, 16)
                current_hours = random.randint(0, required_hours + 2)
                
                status = "Meeting Target"
                if current_hours < required_hours * 0.8:
                    status = "Below Target"
                elif current_hours >= required_hours:
                    status = "Exceeding Target"
                
                data.append({
                    "train_id": train_id,
                    "brand": brand,
                    "contract_start": contract_start.strftime("%Y-%m-%d"),
                    "contract_end": contract_end.strftime("%Y-%m-%d"),
                    "required_daily_hours": required_hours,
                    "current_daily_hours": current_hours,
                    "status": status,
                    "penalty_per_hour": random.randint(5000, 25000)  # INR
                })
        
        return pd.DataFrame(data)
    
    def generate_mileage_data(self):
        """Generate mileage and wear data"""
        data = []
        for train_id in self.train_ids:
            total_km = random.randint(50000, 200000)
            
            # Component wear levels (0-100%)
            bogie_wear = min(100, (total_km / 1000000) * 100 + random.randint(-10, 10))
            brake_wear = min(100, (total_km / 500000) * 100 + random.randint(-15, 15))
            hvac_wear = min(100, (total_km / 750000) * 100 + random.randint(-10, 10))
            
            data.append({
                "train_id": train_id,
                "total_kilometers": total_km,
                "daily_target_km": random.randint(200, 400),
                "current_daily_km": random.randint(150, 450),
                "bogie_wear_percent": max(0, bogie_wear),
                "brake_wear_percent": max(0, brake_wear),
                "hvac_wear_percent": max(0, hvac_wear),
                "last_maintenance": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            })
        
        return pd.DataFrame(data)
    
    def generate_cleaning_schedule(self):
        """Generate cleaning and detailing schedule"""
        data = []
        cleaning_bays = ["Bay-A", "Bay-B", "Bay-C", "Bay-D"]
        
        for train_id in self.train_ids:
            last_cleaned = datetime.now() - timedelta(days=random.randint(1, 14))
            cleaning_due = random.choice([True, False])
            
            # Some trains are scheduled for cleaning
            scheduled_bay = None
            scheduled_time = None
            if cleaning_due and random.random() > 0.5:
                scheduled_bay = random.choice(cleaning_bays)
                scheduled_time = f"{random.randint(22, 23)}:{random.randint(0, 59):02d}"
            
            data.append({
                "train_id": train_id,
                "last_deep_clean": last_cleaned.strftime("%Y-%m-%d"),
                "cleaning_due": cleaning_due,
                "scheduled_bay": scheduled_bay,
                "scheduled_time": scheduled_time,
                "estimated_duration": random.randint(2, 6),  # hours
                "cleanliness_score": random.randint(60, 100)
            })
        
        return pd.DataFrame(data)
    
    def generate_stabling_positions(self):
        """Generate current stabling positions and constraints"""
        data = []
        positions = list(range(1, 26))  # 25 positions
        random.shuffle(positions)
        
        for i, train_id in enumerate(self.train_ids):
            current_pos = positions[i]
            
            # Calculate shunting time based on position
            # Positions 1-5 are closest to exit, 21-25 are furthest
            if current_pos <= 5:
                shunting_time = random.randint(5, 15)
            elif current_pos <= 15:
                shunting_time = random.randint(15, 30)
            else:
                shunting_time = random.randint(30, 45)
            
            data.append({
                "train_id": train_id,
                "current_position": current_pos,
                "optimal_position": random.randint(1, 25),
                "shunting_time_minutes": shunting_time,
                "access_difficulty": random.choice(["Easy", "Medium", "Hard"]),
                "power_connection": random.choice([True, False])
            })
        
        return pd.DataFrame(data)
    
    def generate_historical_performance(self):
        """Generate historical performance data for ML training"""
        data = []
        for _ in range(1000):  # 1000 historical records
            train_id = random.choice(self.train_ids)
            date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            # Service metrics
            on_time_departure = random.choice([True, False])
            service_hours = random.randint(8, 16)
            breakdown_occurred = random.choice([True, False])
            
            # Factors that influenced performance
            cert_status = random.choice(["Valid", "Expired", "Expiring Soon"])
            open_jobs = random.randint(0, 3)
            mileage = random.randint(50000, 200000)
            last_maintenance_days = random.randint(1, 90)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "train_id": train_id,
                "on_time_departure": on_time_departure,
                "service_hours": service_hours,
                "breakdown_occurred": breakdown_occurred,
                "cert_status": cert_status,
                "open_jobs_count": open_jobs,
                "total_mileage": mileage,
                "days_since_maintenance": last_maintenance_days,
                "weather": random.choice(["Clear", "Rain", "Heavy Rain"]),
                "passenger_load": random.choice(["Low", "Medium", "High"])
            })
        
        return pd.DataFrame(data)
    
    def generate_all_data(self):
        """Generate all mock data and return as dictionary"""
        return {
            "fitness_certificates": self.generate_fitness_certificates(),
            "job_cards": self.generate_job_cards(),
            "branding_data": self.generate_branding_data(),
            "mileage_data": self.generate_mileage_data(),
            "cleaning_schedule": self.generate_cleaning_schedule(),
            "stabling_positions": self.generate_stabling_positions(),
            "historical_performance": self.generate_historical_performance()
        }

if __name__ == "__main__":
    generator = MockDataGenerator()
    data = generator.generate_all_data()
    
    # Save to CSV files for inspection
    for name, df in data.items():
        df.to_csv(f"../data/{name}.csv", index=False)
        print(f"Generated {len(df)} records for {name}")
