#!/usr/bin/env python3
"""
ML Predictor for AI Scaler V3
Uses RandomForestRegressor to learn optimal replica counts
"""

import os
import logging
import pickle
from typing import Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)


class MLPredictor:
    """
    Machine Learning predictor for optimal replica counts
    Uses RandomForestRegressor with continuous learning
    """
    
    def __init__(self, model_path: str = 'models/scaler_model.pkl'):
        """
        Initialize ML Predictor
        
        Args:
            model_path: Path to save/load the trained model
        """
        self.model_path = model_path
        self.model_dir = os.path.dirname(model_path)
        
        # Create models directory if it doesn't exist
        if self.model_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            logger.info(f"Created models directory: {self.model_dir}")
        
        # Initialize model and scaler
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        
        # Training data buffers
        self.training_features = []
        self.training_labels = []
        
        # Model state
        self.is_trained = False
        self.training_samples = 0
        self.min_samples_for_training = 20  # Minimum samples before training
        
        # Load existing model if available
        self.load_model()
        
        logger.info(f"Initialized MLPredictor (trained: {self.is_trained}, samples: {self.training_samples})")
    
    def extract_ml_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Extract features for ML model
        
        Args:
            features: Feature dictionary from feature_engineering
            
        Returns:
            Feature array for ML model
        """
        # Select key features for prediction
        feature_list = [
            features.get('cpu_current', 0.0),
            features.get('memory_current', 0.0),
            features.get('network_total', 0.0),
            features.get('cpu_avg', 0.0),
            features.get('cpu_max', 0.0),
            features.get('cpu_min', 0.0),
            features.get('cpu_std', 0.0),
            features.get('memory_avg', 0.0),
            features.get('memory_max', 0.0),
            features.get('cpu_trend', 0.0),
            features.get('cpu_trend_strength', 0.0),
            features.get('pod_count', 1.0),
        ]
        
        return np.array(feature_list).reshape(1, -1)
    
    def predict(self, features: Dict[str, Any]) -> Tuple[Optional[int], float]:
        """
        Predict optimal replica count
        
        Args:
            features: Feature dictionary
            
        Returns:
            Tuple of (predicted_replicas, confidence)
        """
        if not self.is_trained:
            return None, 0.0
        
        try:
            # Extract and scale features
            X = self.extract_ml_features(features)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            predicted_replicas = max(1, int(round(prediction)))
            
            # Calculate confidence based on model's estimators agreement
            predictions = np.array([tree.predict(X_scaled)[0] for tree in self.model.estimators_])
            std = np.std(predictions)
            confidence = max(0.0, min(1.0, 1.0 - (std / max(prediction, 1.0))))
            
            logger.debug(f"ML Prediction: {predicted_replicas} replicas (confidence: {confidence:.2f})")
            
            return predicted_replicas, confidence
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None, 0.0
    
    def add_training_sample(self, features: Dict[str, Any], actual_replicas: int) -> None:
        """
        Add a training sample
        
        Args:
            features: Feature dictionary
            actual_replicas: Actual replica count that was used
        """
        try:
            X = self.extract_ml_features(features)
            self.training_features.append(X[0])
            self.training_labels.append(actual_replicas)
            self.training_samples += 1
            
            logger.debug(f"Added training sample (total: {self.training_samples})")
            
            # Train if we have enough samples
            if self.training_samples >= self.min_samples_for_training:
                if self.training_samples % 10 == 0:  # Retrain every 10 samples
                    self.train()
                    
        except Exception as e:
            logger.error(f"Error adding training sample: {e}")
    
    def train(self) -> bool:
        """
        Train the model on collected samples
        
        Returns:
            True if training successful
        """
        if len(self.training_features) < self.min_samples_for_training:
            logger.warning(f"Not enough samples for training ({len(self.training_features)} < {self.min_samples_for_training})")
            return False
        
        try:
            logger.info(f"Training model with {len(self.training_features)} samples...")
            
            # Prepare data
            X = np.array(self.training_features)
            y = np.array(self.training_labels)
            
            # Fit scaler and transform features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Calculate training score
            score = self.model.score(X_scaled, y)
            logger.info(f"✓ Model trained successfully (R² score: {score:.3f})")
            
            # Save model
            self.save_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def save_model(self) -> bool:
        """
        Save model to disk
        
        Returns:
            True if save successful
        """
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'training_samples': self.training_samples,
                'is_trained': self.is_trained,
                'training_features': self.training_features[-100:],  # Keep last 100
                'training_labels': self.training_labels[-100:]
            }
            
            joblib.dump(model_data, self.model_path)
            logger.info(f"✓ Model saved to {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self) -> bool:
        """
        Load model from disk
        
        Returns:
            True if load successful
        """
        if not os.path.exists(self.model_path):
            logger.info("No existing model found, starting fresh")
            return False
        
        try:
            model_data = joblib.load(self.model_path)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.training_samples = model_data['training_samples']
            self.is_trained = model_data['is_trained']
            self.training_features = model_data.get('training_features', [])
            self.training_labels = model_data.get('training_labels', [])
            
            logger.info(f"✓ Model loaded from {self.model_path} ({self.training_samples} samples)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get model statistics
        
        Returns:
            Dictionary with model stats
        """
        return {
            'is_trained': self.is_trained,
            'training_samples': self.training_samples,
            'model_exists': os.path.exists(self.model_path),
            'min_samples_needed': self.min_samples_for_training
        }


if __name__ == "__main__":
    # Test the ML predictor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    predictor = MLPredictor()
    
    # Simulate training data
    print("\nSimulating training data...")
    for i in range(30):
        features = {
            'cpu_current': 100 + i * 20,
            'memory_current': 200 + i * 10,
            'network_total': 5 + i * 0.5,
            'cpu_avg': 100 + i * 20,
            'cpu_max': 150 + i * 20,
            'cpu_min': 50 + i * 20,
            'cpu_std': 10,
            'memory_avg': 200 + i * 10,
            'memory_max': 250 + i * 10,
            'cpu_trend': 0.5,
            'cpu_trend_strength': 0.3,
            'pod_count': 1 + (i // 10)
        }
        replicas = 1 + (i // 10)
        predictor.add_training_sample(features, replicas)
    
    # Test prediction
    print("\nTesting prediction...")
    test_features = {
        'cpu_current': 500,
        'memory_current': 400,
        'network_total': 15,
        'cpu_avg': 500,
        'cpu_max': 600,
        'cpu_min': 400,
        'cpu_std': 50,
        'memory_avg': 400,
        'memory_max': 450,
        'cpu_trend': 1.0,
        'cpu_trend_strength': 0.5,
        'pod_count': 2
    }
    
    predicted, confidence = predictor.predict(test_features)
    print(f"Predicted replicas: {predicted} (confidence: {confidence:.2f})")
    
    # Show stats
    print(f"\nModel stats: {predictor.get_stats()}")

# Made by Nabanish with Bob's assistance