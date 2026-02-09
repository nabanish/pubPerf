#!/usr/bin/env python3
"""
AI-Driven Kubernetes Autoscaler V2
Uses machine learning to predict optimal pod count based on CPU/Memory load
Fixed: Removed feedback loop by calculating optimal pods from CPU utilization
"""

import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from kubernetes import client, config
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
import json

class AIAutoscaler:
    def __init__(self, deployment_name="tomcat-sample-app", namespace="default"):
        """Initialize the AI Autoscaler"""
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.min_replicas = 1
        self.max_replicas = 6  # Allows scaling for high JMeter load (2000-5000 TPS)
        self.check_interval = 30  # seconds
        self.history_file = "metrics_history_v2.json"
        self.model_file = "scaler_model_v2.pkl"
        
        # CPU thresholds for calculating optimal pods
        # ADJUSTED FOR LOWER LOAD: Original was 500/700/200
        self.target_cpu_per_pod = 200  # Target 200m CPU per pod (was 500m)
        self.scale_up_threshold = 250  # Scale up if CPU > 250m per pod (was 700m)
        self.scale_down_threshold = 50   # Scale down if CPU < 50m per pod (was 200m)
        
        # Load Kubernetes config
        try:
            config.load_kube_config()
        except:
            config.load_incluster_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
        
        # Initialize metrics history
        self.metrics_history = self.load_history()
        
        # Initialize or load ML model
        self.model = self.load_or_create_model()
        
        print(f"🤖 AI Autoscaler V2 initialized for {deployment_name}")
        print(f"📊 Min replicas: {self.min_replicas}, Max replicas: {self.max_replicas}")
        print(f"🎯 Target CPU per pod: {self.target_cpu_per_pod}m")
        print(f"⏱️  Check interval: {self.check_interval} seconds\n")
    
    def load_history(self):
        """Load metrics history from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Save metrics history to file"""
        # Keep only last 1000 entries
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.metrics_history, f)
    
    def load_or_create_model(self):
        """Load existing model or create new one"""
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                print("📦 Loaded existing ML model")
                return pickle.load(f)
        else:
            print("🆕 Creating new ML model")
            return RandomForestRegressor(n_estimators=50, random_state=42)
    
    def save_model(self):
        """Save ML model to file"""
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)
    
    def get_current_metrics(self):
        """Get current CPU and memory metrics from metrics-server"""
        try:
            # Get pod metrics
            pod_metrics = self.custom_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=self.namespace,
                plural="pods"
            )
            
            # Filter pods for our deployment
            deployment_pods = [
                pod for pod in pod_metrics['items']
                if self.deployment_name in pod['metadata']['name']
            ]
            
            if not deployment_pods:
                return None
            
            # Calculate average CPU and memory across all pods
            total_cpu = 0
            total_memory = 0
            
            for pod in deployment_pods:
                for container in pod['containers']:
                    # Parse CPU (e.g., "3m" -> 3)
                    cpu_str = container['usage']['cpu']
                    cpu_value = int(cpu_str.replace('n', '').replace('m', '').replace('u', ''))
                    if 'n' in cpu_str:
                        cpu_value = cpu_value / 1000000  # nanocores to millicores
                    elif 'u' in cpu_str:
                        cpu_value = cpu_value / 1000  # microcores to millicores
                    
                    # Parse memory (e.g., "123Mi" -> 123)
                    mem_str = container['usage']['memory']
                    mem_value = int(mem_str.replace('Ki', '').replace('Mi', '').replace('Gi', ''))
                    if 'Ki' in mem_str:
                        mem_value = mem_value / 1024  # Ki to Mi
                    elif 'Gi' in mem_str:
                        mem_value = mem_value * 1024  # Gi to Mi
                    
                    total_cpu += cpu_value
                    total_memory += mem_value
            
            num_pods = len(deployment_pods)
            avg_cpu = total_cpu / num_pods if num_pods > 0 else 0
            avg_memory = total_memory / num_pods if num_pods > 0 else 0
            
            return {
                'cpu_millicores': avg_cpu,
                'memory_mi': avg_memory,
                'total_cpu': total_cpu,
                'num_pods': num_pods,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"❌ Error getting metrics: {e}")
            return None
    
    def calculate_optimal_pods(self, metrics):
        """Calculate optimal number of pods based on total CPU load"""
        total_cpu = metrics['total_cpu']
        
        # Calculate how many pods we need to keep CPU per pod around target
        optimal_pods = max(1, int(np.ceil(total_cpu / self.target_cpu_per_pod)))
        
        # Constrain to min/max
        optimal_pods = max(self.min_replicas, min(self.max_replicas, optimal_pods))
        
        return optimal_pods
    
    def get_current_replicas(self):
        """Get current number of replicas"""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace
            )
            return deployment.spec.replicas
        except Exception as e:
            print(f"❌ Error getting replicas: {e}")
            return None
    
    def set_replicas(self, replicas):
        """Set number of replicas"""
        try:
            # Ensure within bounds
            replicas = max(self.min_replicas, min(self.max_replicas, replicas))
            
            deployment = self.apps_v1.read_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace
            )
            
            deployment.spec.replicas = replicas
            
            self.apps_v1.patch_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace,
                body=deployment
            )
            
            return True
        except Exception as e:
            print(f"❌ Error setting replicas: {e}")
            return False
    
    def extract_features(self, metrics_list):
        """Extract features from metrics history for ML model"""
        if len(metrics_list) < 5:
            return None
        
        df = pd.DataFrame(metrics_list)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate optimal pods for each historical point
        df['optimal_pods'] = df.apply(
            lambda row: max(1, int(np.ceil(row['total_cpu'] / self.target_cpu_per_pod))),
            axis=1
        )
        df['optimal_pods'] = df['optimal_pods'].clip(self.min_replicas, self.max_replicas)
        
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['minute'] = df['timestamp'].dt.minute
        
        # Calculate trends
        df['cpu_trend'] = df['cpu_millicores'].diff().fillna(0)
        df['mem_trend'] = df['memory_mi'].diff().fillna(0)
        df['total_cpu_trend'] = df['total_cpu'].diff().fillna(0)
        
        # Rolling averages
        df['cpu_ma_5'] = df['cpu_millicores'].rolling(window=5, min_periods=1).mean()
        df['mem_ma_5'] = df['memory_mi'].rolling(window=5, min_periods=1).mean()
        df['total_cpu_ma_5'] = df['total_cpu'].rolling(window=5, min_periods=1).mean()
        
        return df
    
    def train_model(self):
        """Train ML model on historical data"""
        if len(self.metrics_history) < 20:
            print("⏳ Not enough data to train model (need at least 20 samples)")
            return False
        
        df = self.extract_features(self.metrics_history)
        if df is None:
            return False
        
        # Features for prediction (NO num_pods to avoid feedback loop)
        feature_cols = ['hour', 'day_of_week', 'minute', 'cpu_millicores', 
                       'memory_mi', 'total_cpu', 'cpu_trend', 'mem_trend', 
                       'total_cpu_trend', 'cpu_ma_5', 'mem_ma_5', 'total_cpu_ma_5']
        
        X = df[feature_cols].values
        # Target: optimal number of pods based on CPU load
        y = df['optimal_pods'].values
        
        # Train model
        self.model.fit(X, y)
        self.save_model()
        
        print(f"✅ Model trained on {len(X)} samples")
        print(f"   Feature importance: CPU-based optimal pod calculation")
        return True
    
    def predict_optimal_replicas(self, current_metrics):
        """Use ML model to predict optimal number of replicas"""
        if current_metrics is None:
            return None
        
        # If not enough history, use simple heuristic
        if len(self.metrics_history) < 20:
            return self.simple_heuristic(current_metrics)
        
        # Prepare features
        df = self.extract_features(self.metrics_history + [current_metrics])
        if df is None:
            return self.simple_heuristic(current_metrics)
        
        # Get latest features
        feature_cols = ['hour', 'day_of_week', 'minute', 'cpu_millicores', 
                       'memory_mi', 'total_cpu', 'cpu_trend', 'mem_trend',
                       'total_cpu_trend', 'cpu_ma_5', 'mem_ma_5', 'total_cpu_ma_5']
        
        latest_features = df[feature_cols].iloc[-1:].values
        
        # Predict
        predicted_replicas = self.model.predict(latest_features)[0]
        
        # Round and constrain
        predicted_replicas = int(round(predicted_replicas))
        predicted_replicas = max(self.min_replicas, min(self.max_replicas, predicted_replicas))
        
        return predicted_replicas
    
    def simple_heuristic(self, metrics):
        """Simple rule-based heuristic when ML model isn't ready"""
        avg_cpu = metrics['cpu_millicores']
        current_pods = metrics['num_pods']
        
        # Use average CPU per pod to make decisions
        if avg_cpu > self.scale_up_threshold:  # High CPU per pod
            return min(current_pods + 1, self.max_replicas)
        elif avg_cpu < self.scale_down_threshold and current_pods > self.min_replicas:
            return max(current_pods - 1, self.min_replicas)
        else:
            return current_pods
    
    def run(self):
        """Main loop"""
        print("🚀 AI Autoscaler V2 started!\n")
        print("📝 Key improvements:")
        print("   - No feedback loop: predicts based on CPU load, not current pod count")
        print("   - Target-based scaling: aims for optimal CPU per pod")
        print("   - Better feature engineering: includes total CPU and trends\n")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                print(f"{'='*60}")
                print(f"Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Get current metrics
                metrics = self.get_current_metrics()
                if metrics is None:
                    print("⚠️  Could not get metrics, skipping...")
                    time.sleep(self.check_interval)
                    continue
                
                # Add to history
                self.metrics_history.append(metrics)
                self.save_history()
                
                # Display current state
                print(f"📊 Current Metrics:")
                print(f"   CPU per pod: {metrics['cpu_millicores']:.1f}m")
                print(f"   Total CPU: {metrics['total_cpu']:.1f}m")
                print(f"   Memory per pod: {metrics['memory_mi']:.1f}Mi")
                print(f"   Current pods: {metrics['num_pods']}")
                
                # Calculate what would be optimal based on current load
                optimal_by_formula = self.calculate_optimal_pods(metrics)
                print(f"   Optimal (by formula): {optimal_by_formula} pods")
                
                # Train model periodically
                if iteration % 10 == 0 and len(self.metrics_history) >= 20:
                    print("\n🎓 Training ML model...")
                    self.train_model()
                
                # Predict optimal replicas
                current_replicas = self.get_current_replicas()
                predicted_replicas = self.predict_optimal_replicas(metrics)
                
                if predicted_replicas is None:
                    print("⚠️  Could not predict replicas")
                    time.sleep(self.check_interval)
                    continue
                
                mode = "ML Model" if len(self.metrics_history) >= 20 else "Heuristic"
                print(f"\n🤖 AI Decision ({mode}):")
                print(f"   Current replicas: {current_replicas}")
                print(f"   Recommended replicas: {predicted_replicas}")
                
                # Apply scaling decision with dampening
                if predicted_replicas != current_replicas:
                    # Scale up more aggressively, scale down conservatively
                    should_scale = (
                        # Always scale up if CPU is high
                        (predicted_replicas > current_replicas and metrics['cpu_millicores'] > self.scale_up_threshold) or
                        # Scale down only if CPU is very low
                        (predicted_replicas < current_replicas and metrics['cpu_millicores'] < self.scale_down_threshold) or
                        # Or if difference is large (2+)
                        abs(predicted_replicas - current_replicas) >= 2 or
                        # Or at extremes
                        (predicted_replicas == self.min_replicas and metrics['cpu_millicores'] < 100) or
                        (predicted_replicas == self.max_replicas and metrics['cpu_millicores'] > 800)
                    )
                    
                    if should_scale:
                        print(f"\n⚡ Scaling from {current_replicas} to {predicted_replicas} replicas...")
                        if self.set_replicas(predicted_replicas):
                            print(f"✅ Successfully scaled to {predicted_replicas} replicas")
                        else:
                            print("❌ Failed to scale")
                    else:
                        print(f"\n⏸️  Dampening: difference too small, keeping {current_replicas} replicas")
                else:
                    print("\n✓ No scaling needed")
                
                print(f"\n⏳ Waiting {self.check_interval} seconds...\n")
                time.sleep(self.check_interval)
            
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping AI Autoscaler...")
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(self.check_interval)

if __name__ == "__main__":
    scaler = AIAutoscaler()
    scaler.run()

# Made by Nabanish with the help of Bob - V2 with fixed feedback loop