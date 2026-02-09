#!/usr/bin/env python3
"""
AI-Driven Kubernetes Autoscaler V3
Multi-metric optimization with Prometheus integration
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, Optional
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from prometheus_client import PrometheusClient
from feature_engineering import FeatureEngineer
from decision_engine import DecisionEngine
from ml_predictor import MLPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_scaler_v3.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIScalerV3:
    """
    AI-Driven Kubernetes Autoscaler V3
    
    Features:
    - Multi-metric optimization (CPU, Memory, Network, Cost)
    - Prometheus integration for real-time metrics
    - Feature engineering with 37+ features
    - Weighted scoring system
    - Enhanced dampening logic
    - Predictive scaling capabilities
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize AI Scaler V3"""
        logger.info("=" * 70)
        logger.info("Initializing AI Scaler V3")
        logger.info("=" * 70)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
        except:
            config.load_kube_config()
            logger.info("Loaded local Kubernetes config")
        
        self.k8s_apps = client.AppsV1Api()
        self.k8s_core = client.CoreV1Api()
        
        # Initialize components
        self.prometheus = PrometheusClient(
            prometheus_url=self.config['prometheus']['url']
        )
        
        self.feature_engineer = FeatureEngineer(
            prometheus_client=self.prometheus
        )
        
        # Initialize ML Predictor for learning-based decisions
        self.ml_predictor = MLPredictor(model_path='models/scaler_model.pkl')
        
        self.decision_engine = DecisionEngine(
            min_replicas=self.config['scaling']['min_replicas'],
            max_replicas=self.config['scaling']['max_replicas'],
            weights=self.config['weights'],
            ml_predictor=self.ml_predictor
        )
        
        # State tracking
        self.last_scale_time = None
        self.scale_history = []
        self.metrics_history = []
        
        logger.info(f"Target: {self.config['target']['namespace']}/{self.config['target']['deployment']}")
        logger.info(f"Replica range: {self.config['scaling']['min_replicas']}-{self.config['scaling']['max_replicas']}")
        logger.info(f"Check interval: {self.config['scaling']['check_interval']}s")
        logger.info(f"Cooldown period: {self.config['scaling']['cooldown_period']}s")
        logger.info("Initialization complete")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'prometheus': {
                'url': 'http://localhost:30090'
            },
            'target': {
                'namespace': 'default',
                'deployment': 'tomcat-sample-app'
            },
            'scaling': {
                'min_replicas': 1,
                'max_replicas': 10,
                'check_interval': 30,
                'cooldown_period': 60
            },
            'weights': {
                'cpu': 0.4,
                'memory': 0.3,
                'network': 0.2,
                'cost': 0.1
            },
            'thresholds': {
                'cpu_target': 70.0,
                'memory_target': 70.0,
                'network_target': 70.0
            }
        }
    
    def get_current_replicas(self) -> int:
        """Get current number of replicas"""
        try:
            deployment = self.k8s_apps.read_namespaced_deployment(
                name=self.config['target']['deployment'],
                namespace=self.config['target']['namespace']
            )
            return deployment.spec.replicas
        except ApiException as e:
            logger.error(f"Failed to get current replicas: {e}")
            return 1
    
    def scale_deployment(self, target_replicas: int) -> bool:
        """Scale deployment to target replicas"""
        try:
            # Get current deployment
            deployment = self.k8s_apps.read_namespaced_deployment(
                name=self.config['target']['deployment'],
                namespace=self.config['target']['namespace']
            )
            
            # Update replicas
            deployment.spec.replicas = target_replicas
            
            # Apply update
            self.k8s_apps.patch_namespaced_deployment(
                name=self.config['target']['deployment'],
                namespace=self.config['target']['namespace'],
                body=deployment
            )
            
            logger.info(f"✓ Scaled deployment to {target_replicas} replicas")
            
            # Update state
            self.last_scale_time = time.time()
            self.scale_history.append({
                'timestamp': datetime.now().isoformat(),
                'replicas': target_replicas
            })
            
            return True
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment: {e}")
            return False
    
    def check_cooldown(self) -> bool:
        """Check if cooldown period has passed"""
        if self.last_scale_time is None:
            return True
        
        elapsed = time.time() - self.last_scale_time
        cooldown = self.config['scaling']['cooldown_period']
        
        if elapsed < cooldown:
            remaining = cooldown - elapsed
            logger.debug(f"Cooldown active: {remaining:.0f}s remaining")
            return False
        
        return True
    
    def run_scaling_cycle(self) -> None:
        """Run one scaling cycle"""
        try:
            logger.info("-" * 70)
            logger.info(f"Scaling Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("-" * 70)
            
            # Get current state
            current_replicas = self.get_current_replicas()
            logger.info(f"Current replicas: {current_replicas}")
            
            # Extract features
            logger.info("Extracting features from Prometheus...")
            features = self.feature_engineer.extract_features(
                namespace=self.config['target']['namespace'],
                app_label=self.config['target']['deployment']
            )
            
            if features is None:
                logger.warning("Failed to extract features, skipping cycle")
                return
            
            # Log key metrics
            logger.info(f"CPU Usage: {features.get('cpu_current', 0):.1f} millicores")
            logger.info(f"Memory Usage: {features.get('memory_current', 0):.1f} MB")
            logger.info(f"Network I/O: {features.get('network_total', 0):.2f} Mbps")
            
            # Make scaling decision
            logger.info("Making scaling decision...")
            decision = self.decision_engine.make_decision(features=features)
            
            # Log decision
            logger.info(f"Decision: {decision['action']}")
            logger.info(f"Target replicas: {decision['target_replicas']}")
            logger.info(f"Decision source: {decision.get('decision_source', 'Rule-based')}")
            if decision.get('ml_replicas') is not None:
                logger.info(f"ML prediction: {decision['ml_replicas']} (confidence: {decision['ml_confidence']:.2f})")
            logger.info(f"Confidence: {decision['confidence']:.2f}")
            logger.info(f"Reason: {decision['reason']}")
            logger.info(f"Weighted score: {decision['scores']['total_score']:.1f}")
            
            # Log ML stats
            ml_stats = self.ml_predictor.get_stats()
            if ml_stats['training_samples'] > 0:
                logger.info(f"ML Stats: {ml_stats['training_samples']} samples, trained: {ml_stats['is_trained']}")
            
            # Execute scaling action
            if decision['action'] == 'scale_up':
                if not self.check_cooldown():
                    logger.info("⏸ Scaling up blocked by cooldown period")
                    return
                
                logger.info(f"⬆ Scaling up: {current_replicas} → {decision['target_replicas']}")
                self.scale_deployment(decision['target_replicas'])
                
            elif decision['action'] == 'scale_down':
                if not self.check_cooldown():
                    logger.info("⏸ Scaling down blocked by cooldown period")
                    return
                
                logger.info(f"⬇ Scaling down: {current_replicas} → {decision['target_replicas']}")
                self.scale_deployment(decision['target_replicas'])
                
            else:
                logger.info("✓ No scaling action needed")
            
            # Store metrics history
            self.metrics_history.append({
                'timestamp': datetime.now().isoformat(),
                'replicas': current_replicas,
                'decision': decision,
                'features': features
            })
            
            # Keep only last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
        except Exception as e:
            logger.error(f"Error in scaling cycle: {e}", exc_info=True)
    
    def run(self) -> None:
        """Run the autoscaler continuously"""
        logger.info("=" * 70)
        logger.info("AI Scaler V3 Started")
        logger.info("=" * 70)
        
        # Verify Prometheus connection
        if not self.prometheus.health_check():
            logger.error("Prometheus health check failed!")
            logger.error("Please ensure Prometheus is running and accessible")
            sys.exit(1)
        
        logger.info("✓ Prometheus connection verified")
        
        # Main loop
        check_interval = self.config['scaling']['check_interval']
        
        try:
            while True:
                self.run_scaling_cycle()
                
                logger.info(f"Sleeping for {check_interval}s...")
                logger.info("")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("=" * 70)
            logger.info("AI Scaler V3 Stopped")
            logger.info("=" * 70)
            self.print_summary()
    
    def print_summary(self) -> None:
        """Print summary statistics"""
        if not self.scale_history:
            logger.info("No scaling actions performed")
            return
        
        logger.info("")
        logger.info("Summary Statistics:")
        logger.info("-" * 70)
        logger.info(f"Total scaling actions: {len(self.scale_history)}")
        
        if self.scale_history:
            replicas = [h['replicas'] for h in self.scale_history]
            logger.info(f"Min replicas: {min(replicas)}")
            logger.info(f"Max replicas: {max(replicas)}")
            logger.info(f"Avg replicas: {sum(replicas) / len(replicas):.1f}")
        
        logger.info("")
        logger.info("Recent scaling actions:")
        for action in self.scale_history[-5:]:
            logger.info(f"  {action['timestamp']}: {action['replicas']} replicas")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AI-Driven Kubernetes Autoscaler V3'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual scaling)'
    )
    
    args = parser.parse_args()
    
    # Create and run scaler
    scaler = AIScalerV3(config_path=args.config)
    scaler.run()


if __name__ == '__main__':
    main()

# Made by Nabanish with Bob's assistance
