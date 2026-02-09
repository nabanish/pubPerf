#!/usr/bin/env python3
"""
Feature Engineering Module for AI Scaler V3
Extracts and transforms multi-metric features from Prometheus data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from prometheus_client import PrometheusClient

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Extract and engineer features from Prometheus metrics
    for ML model training and prediction
    """
    
    def __init__(self, prometheus_client: PrometheusClient):
        """
        Initialize feature engineer
        
        Args:
            prometheus_client: Prometheus client for querying metrics
        """
        self.prom = prometheus_client
        logger.info("Initialized FeatureEngineer")
    
    def extract_features(self, namespace: str = "default", 
                        app_label: str = "tomcat-sample-app") -> Dict[str, Any]:
        """
        Extract all features for current state
        
        Args:
            namespace: Kubernetes namespace
            app_label: Application label
            
        Returns:
            Dictionary of engineered features
        """
        try:
            # Get current metrics
            current_metrics = self.prom.get_comprehensive_metrics(namespace, app_label)
            
            # Get historical metrics
            historical_cpu = self._get_historical_metrics('cpu', namespace, app_label)
            historical_memory = self._get_historical_metrics('memory', namespace, app_label)
            
            # Extract features
            features = {}
            
            # Current state features
            features.update(self._extract_current_features(current_metrics))
            
            # Historical features
            features.update(self._extract_historical_features(historical_cpu, 'cpu'))
            features.update(self._extract_historical_features(historical_memory, 'memory'))
            
            # Time-based features
            features.update(self._extract_time_features())
            
            # Trend features
            features.update(self._extract_trend_features(historical_cpu, 'cpu'))
            features.update(self._extract_trend_features(historical_memory, 'memory'))
            
            # Pattern features
            features.update(self._extract_pattern_features(historical_cpu, 'cpu'))
            
            logger.debug(f"Extracted {len(features)} features")
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return self._get_default_features()
    
    def _extract_current_features(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from current metrics"""
        features = {}
        
        # Pod features
        features['pod_count'] = float(metrics.get('pod_count', 1))
        
        # CPU features
        cpu = metrics.get('cpu', {})
        features['cpu_current'] = cpu.get('cpu_per_pod', 0.0)
        features['cpu_total'] = cpu.get('total_cpu', 0.0)
        
        # Memory features
        memory = metrics.get('memory', {})
        features['memory_current'] = memory.get('memory_per_pod_mb', 0.0)
        features['memory_total'] = memory.get('total_memory_mb', 0.0)
        
        # Network features
        network = metrics.get('network', {})
        features['network_in_rate'] = network.get('network_in_mbps', 0.0)
        features['network_out_rate'] = network.get('network_out_mbps', 0.0)
        features['network_total'] = features['network_in_rate'] + features['network_out_rate']
        
        # Resource utilization ratios
        if features['pod_count'] > 0:
            features['cpu_per_pod_ratio'] = features['cpu_current'] / 500.0  # Target 500m
            features['memory_per_pod_ratio'] = features['memory_current'] / 512.0  # Target 512MB
        else:
            features['cpu_per_pod_ratio'] = 0.0
            features['memory_per_pod_ratio'] = 0.0
        
        return features
    
    def _extract_historical_features(self, historical_data: List[Dict], 
                                    metric_name: str) -> Dict[str, float]:
        """Extract features from historical data"""
        features = {}
        
        if not historical_data or len(historical_data) < 2:
            return {
                f'{metric_name}_avg_15m': 0.0,
                f'{metric_name}_avg_1h': 0.0,
                f'{metric_name}_max_15m': 0.0,
                f'{metric_name}_min_15m': 0.0,
                f'{metric_name}_std_15m': 0.0,
            }
        
        # Convert to numpy array
        values = np.array([d['value'] for d in historical_data])
        
        # Calculate statistics
        features[f'{metric_name}_avg_15m'] = float(np.mean(values))
        features[f'{metric_name}_max_15m'] = float(np.max(values))
        features[f'{metric_name}_min_15m'] = float(np.min(values))
        features[f'{metric_name}_std_15m'] = float(np.std(values))
        
        # Calculate 1-hour average (if enough data)
        if len(values) >= 240:  # 1 hour at 15s intervals
            features[f'{metric_name}_avg_1h'] = float(np.mean(values[-240:]))
        else:
            features[f'{metric_name}_avg_1h'] = features[f'{metric_name}_avg_15m']
        
        # Volatility (coefficient of variation)
        if features[f'{metric_name}_avg_15m'] > 0:
            features[f'{metric_name}_volatility'] = (
                features[f'{metric_name}_std_15m'] / features[f'{metric_name}_avg_15m']
            )
        else:
            features[f'{metric_name}_volatility'] = 0.0
        
        return features
    
    def _extract_time_features(self) -> Dict[str, Any]:
        """Extract time-based features"""
        now = datetime.now()
        
        features = {
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'is_business_hours': 1 if (9 <= now.hour < 17 and now.weekday() < 5) else 0,
            'is_weekend': 1 if now.weekday() >= 5 else 0,
            'is_peak_hour': 1 if now.hour in [9, 10, 11, 14, 15, 16] else 0,
        }
        
        # Cyclical encoding for hour and day
        features['hour_sin'] = np.sin(2 * np.pi * now.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * now.hour / 24)
        features['day_sin'] = np.sin(2 * np.pi * now.weekday() / 7)
        features['day_cos'] = np.cos(2 * np.pi * now.weekday() / 7)
        
        return features
    
    def _extract_trend_features(self, historical_data: List[Dict], 
                               metric_name: str) -> Dict[str, float]:
        """Extract trend features from historical data"""
        features = {}
        
        if not historical_data or len(historical_data) < 10:
            return {
                f'{metric_name}_trend': 0.0,
                f'{metric_name}_trend_strength': 0.0,
            }
        
        # Get recent values
        values = np.array([d['value'] for d in historical_data[-60:]])  # Last 15 minutes
        
        # Calculate linear trend
        x = np.arange(len(values))
        if len(values) > 1:
            coeffs = np.polyfit(x, values, 1)
            features[f'{metric_name}_trend'] = float(coeffs[0])  # Slope
            
            # Trend strength (R-squared)
            y_pred = np.polyval(coeffs, x)
            ss_res = np.sum((values - y_pred) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            if ss_tot > 0:
                features[f'{metric_name}_trend_strength'] = float(1 - (ss_res / ss_tot))
            else:
                features[f'{metric_name}_trend_strength'] = 0.0
        else:
            features[f'{metric_name}_trend'] = 0.0
            features[f'{metric_name}_trend_strength'] = 0.0
        
        # Rate of change
        if len(values) >= 2:
            recent_change = values[-1] - values[-10] if len(values) >= 10 else values[-1] - values[0]
            features[f'{metric_name}_rate_of_change'] = float(recent_change)
        else:
            features[f'{metric_name}_rate_of_change'] = 0.0
        
        return features
    
    def _extract_pattern_features(self, historical_data: List[Dict], 
                                  metric_name: str) -> Dict[str, Any]:
        """Extract pattern features"""
        features = {}
        
        if not historical_data or len(historical_data) < 10:
            return {
                f'{metric_name}_pattern': 'unknown',
                f'{metric_name}_is_increasing': 0,
                f'{metric_name}_is_stable': 0,
                f'{metric_name}_is_decreasing': 0,
            }
        
        values = np.array([d['value'] for d in historical_data[-60:]])
        
        # Determine pattern
        if len(values) >= 3:
            recent_avg = np.mean(values[-20:])
            older_avg = np.mean(values[:20])
            
            change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            if change_pct > 10:
                pattern = 'increasing'
            elif change_pct < -10:
                pattern = 'decreasing'
            else:
                pattern = 'stable'
        else:
            pattern = 'unknown'
        
        features[f'{metric_name}_pattern'] = pattern
        features[f'{metric_name}_is_increasing'] = 1 if pattern == 'increasing' else 0
        features[f'{metric_name}_is_stable'] = 1 if pattern == 'stable' else 0
        features[f'{metric_name}_is_decreasing'] = 1 if pattern == 'decreasing' else 0
        
        return features
    
    def _get_historical_metrics(self, metric_type: str, namespace: str, 
                               app_label: str, duration_minutes: int = 15) -> List[Dict]:
        """Get historical metrics from Prometheus"""
        try:
            if metric_type == 'cpu':
                return self.prom.get_historical_cpu(namespace, app_label, duration_minutes)
            elif metric_type == 'memory':
                # Would need to implement get_historical_memory in prometheus_client
                return []
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to get historical {metric_type} metrics: {e}")
            return []
    
    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features when extraction fails"""
        return {
            'pod_count': 1.0,
            'cpu_current': 0.0,
            'cpu_total': 0.0,
            'memory_current': 0.0,
            'memory_total': 0.0,
            'network_in_rate': 0.0,
            'network_out_rate': 0.0,
            'network_total': 0.0,
            'cpu_per_pod_ratio': 0.0,
            'memory_per_pod_ratio': 0.0,
            'cpu_avg_15m': 0.0,
            'cpu_max_15m': 0.0,
            'cpu_min_15m': 0.0,
            'cpu_std_15m': 0.0,
            'cpu_avg_1h': 0.0,
            'cpu_volatility': 0.0,
            'cpu_trend': 0.0,
            'cpu_trend_strength': 0.0,
            'cpu_rate_of_change': 0.0,
            'cpu_pattern': 'unknown',
            'cpu_is_increasing': 0,
            'cpu_is_stable': 0,
            'cpu_is_decreasing': 0,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_business_hours': 0,
            'is_weekend': 0,
            'is_peak_hour': 0,
            'hour_sin': 0.0,
            'hour_cos': 1.0,
            'day_sin': 0.0,
            'day_cos': 1.0,
        }
    
    def features_to_dataframe(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert features dictionary to pandas DataFrame
        
        Args:
            features: Dictionary of features
            
        Returns:
            DataFrame with single row of features
        """
        # Convert categorical features to numeric
        numeric_features = {}
        for key, value in features.items():
            if isinstance(value, (int, float)):
                numeric_features[key] = value
            elif isinstance(value, str):
                # Skip string features for now (will be handled by model)
                continue
            else:
                numeric_features[key] = float(value)
        
        return pd.DataFrame([numeric_features])
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        default_features = self._get_default_features()
        return [k for k, v in default_features.items() if isinstance(v, (int, float))]


if __name__ == "__main__":
    # Test the feature engineer
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from prometheus_client import PrometheusClient
    
    # Initialize clients
    prom_client = PrometheusClient("http://localhost:30090")
    feature_engineer = FeatureEngineer(prom_client)
    
    # Extract features
    print("Extracting features...")
    features = feature_engineer.extract_features()
    
    print(f"\nExtracted {len(features)} features:")
    for key, value in sorted(features.items()):
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Convert to DataFrame
    df = feature_engineer.features_to_dataframe(features)
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Feature names: {feature_engineer.get_feature_names()}")

# Made by Nabanish with Bob's assistance
