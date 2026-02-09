#!/usr/bin/env python3
"""
Decision Engine for AI Scaler V3
Multi-metric weighted scoring and scaling decisions with ML learning
"""

import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Make scaling decisions based on multi-metric weighted scoring
    """
    
    def __init__(self,
                 target_cpu: float = 500.0,
                 target_memory: float = 512.0,
                 target_network: float = 10.0,
                 weights: Dict[str, float] = None,
                 min_replicas: int = 1,
                 max_replicas: int = 10,
                 ml_predictor: Optional[Any] = None):
        """
        Initialize decision engine
        
        Args:
            target_cpu: Target CPU per pod (millicores)
            target_memory: Target memory per pod (MB)
            target_network: Target network per pod (Mbps)
            weights: Scoring weights (cpu, memory, network, cost)
            min_replicas: Minimum pod count
            max_replicas: Maximum pod count
            ml_predictor: Optional ML predictor for learning-based decisions
        """
        self.target_cpu = target_cpu
        self.target_memory = target_memory
        self.target_network = target_network
        
        # Default weights: CPU 40%, Memory 30%, Network 20%, Cost 10%
        self.weights = weights or {
            'cpu': 0.40,
            'memory': 0.30,
            'network': 0.20,
            'cost': 0.10
        }
        
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        
        # ML Predictor for learning-based decisions
        self.ml_predictor = ml_predictor
        
        # Thresholds (more responsive)
        self.scale_up_score = 60  # Scale up if score > 60 (was 80)
        self.scale_down_score = 30  # Scale down if score < 30 (was 20)
        
        logger.info(f"Initialized DecisionEngine with weights: {self.weights}")
        if self.ml_predictor:
            logger.info("ML Predictor enabled for learning-based decisions")
    
    def calculate_weighted_score(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate weighted score from features
        
        Args:
            features: Feature dictionary
            
        Returns:
            Dictionary with individual scores and total weighted score
        """
        # CPU Score (0-100)
        cpu_current = features.get('cpu_current', 0.0)
        cpu_score = min((cpu_current / self.target_cpu) * 100, 100)
        
        # Memory Score (0-100)
        memory_current = features.get('memory_current', 0.0)
        memory_score = min((memory_current / self.target_memory) * 100, 100)
        
        # Network Score (0-100)
        network_total = features.get('network_total', 0.0)
        network_score = min((network_total / self.target_network) * 100, 100)
        
        # Cost Score (0-100) - simplified, inverse of pod count
        pod_count = features.get('pod_count', 1.0)
        cost_score = max(100 - (pod_count / self.max_replicas) * 100, 0)
        
        # Weighted total score
        total_score = (
            cpu_score * self.weights['cpu'] +
            memory_score * self.weights['memory'] +
            network_score * self.weights['network'] +
            cost_score * self.weights['cost']
        )
        
        return {
            'cpu_score': cpu_score,
            'memory_score': memory_score,
            'network_score': network_score,
            'cost_score': cost_score,
            'total_score': total_score
        }
    
    def calculate_optimal_replicas(self, features: Dict[str, Any]) -> int:
        """
        Calculate optimal number of replicas based on features
        
        Args:
            features: Feature dictionary
            
        Returns:
            Optimal replica count
        """
        cpu_current = features.get('cpu_current', 0.0)
        memory_current = features.get('memory_current', 0.0)
        pod_count = int(features.get('pod_count', 1))
        
        # Calculate based on CPU (primary metric)
        if cpu_current > 0:
            total_cpu = cpu_current * pod_count
            cpu_based_replicas = int(np.ceil(total_cpu / self.target_cpu))
        else:
            cpu_based_replicas = pod_count
        
        # Calculate based on memory (secondary metric)
        if memory_current > 0:
            total_memory = memory_current * pod_count
            memory_based_replicas = int(np.ceil(total_memory / self.target_memory))
        else:
            memory_based_replicas = pod_count
        
        # For very low CPU (< 10m per pod), prioritize CPU-based scaling
        # This allows aggressive scale-down when pods are truly idle
        cpu_per_pod = cpu_current / pod_count if pod_count > 0 else cpu_current
        if cpu_per_pod < 10.0:
            optimal_replicas = cpu_based_replicas
            logger.debug(f"Very low CPU ({cpu_per_pod:.1f}m/pod), using CPU-based replicas: {cpu_based_replicas}")
        else:
            # Take the maximum to ensure resources are sufficient
            optimal_replicas = max(cpu_based_replicas, memory_based_replicas)
        
        # Apply constraints
        optimal_replicas = max(self.min_replicas, min(optimal_replicas, self.max_replicas))
        
        return optimal_replicas
    
    def should_scale(self, current_replicas: int, predicted_replicas: int, 
                     scores: Dict[str, float], features: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if scaling should occur (dampening logic)
        
        Args:
            current_replicas: Current pod count
            predicted_replicas: Predicted optimal pod count
            scores: Weighted scores
            features: Feature dictionary
            
        Returns:
            Tuple of (should_scale, reason)
        """
        total_score = scores['total_score']
        cpu_trend = features.get('cpu_trend', 0.0)
        cpu_current = features.get('cpu_current', 0.0)
        
        # Condition 1: Large difference (2+ pods)
        if abs(predicted_replicas - current_replicas) >= 2:
            return True, f"Large difference: {abs(predicted_replicas - current_replicas)} pods"
        
        # Condition 2: High load and need to scale up
        if total_score > self.scale_up_score and predicted_replicas > current_replicas:
            return True, f"High load: score={total_score:.1f}"
        
        # Condition 3: Low load and need to scale down
        if total_score < self.scale_down_score and predicted_replicas < current_replicas:
            return True, f"Low load: score={total_score:.1f}"
        
        # Condition 4: Very low CPU (< 5m per pod) - scale down aggressively
        cpu_per_pod = cpu_current / current_replicas if current_replicas > 0 else cpu_current
        if cpu_per_pod < 5.0 and predicted_replicas < current_replicas:
            return True, f"Very low CPU: {cpu_per_pod:.1f}m per pod"
        
        # Condition 5: Rapid increase in CPU trend
        if cpu_trend > 50 and predicted_replicas > current_replicas:
            return True, f"Rapid CPU increase: trend={cpu_trend:.2f}"
        
        # Condition 6: At boundaries
        if predicted_replicas == self.min_replicas and total_score < 10:
            return True, f"At minimum with very low load: score={total_score:.1f}"
        
        if predicted_replicas == self.max_replicas and total_score > 90:
            return True, f"At maximum with very high load: score={total_score:.1f}"
        
        return False, "No scaling needed (dampening)"
    
    def make_decision(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make complete scaling decision with ML learning
        
        Args:
            features: Feature dictionary
            
        Returns:
            Decision dictionary with recommended action
        """
        current_replicas = int(features.get('pod_count', 1))
        
        # Calculate scores
        scores = self.calculate_weighted_score(features)
        
        # Calculate optimal replicas using rule-based approach
        rule_based_replicas = self.calculate_optimal_replicas(features)
        
        # Get ML prediction if available
        ml_replicas = None
        ml_confidence = 0.0
        if self.ml_predictor:
            ml_replicas, ml_confidence = self.ml_predictor.predict(features)
        
        # Combine rule-based and ML predictions
        # IMPORTANT: Always use rule-based for very low scores (< 25) to ensure aggressive scale-down
        total_score = scores['total_score']
        
        if total_score < 25:
            # Very low score - force rule-based to allow aggressive scale-down
            optimal_replicas = rule_based_replicas
            decision_source = f"Rule-based (low score: {total_score:.1f})"
            logger.debug(f"Forcing rule-based due to very low score: {total_score:.1f}")
        elif ml_replicas is not None and ml_confidence > 0.6:
            # Use ML prediction if confidence is high and score is not very low
            optimal_replicas = ml_replicas
            decision_source = f"ML (confidence: {ml_confidence:.2f})"
        else:
            # Fall back to rule-based
            optimal_replicas = rule_based_replicas
            decision_source = "Rule-based (ML confidence too low)"
        
        # Check if should scale
        should_scale, reason = self.should_scale(
            current_replicas, optimal_replicas, scores, features
        )
        
        # Make decision
        if should_scale:
            action = 'scale_up' if optimal_replicas > current_replicas else 'scale_down'
            target_replicas = optimal_replicas
        else:
            action = 'no_change'
            target_replicas = current_replicas
        
        # Add training sample to ML predictor
        if self.ml_predictor and action != 'no_change':
            self.ml_predictor.add_training_sample(features, target_replicas)
        
        decision = {
            'current_replicas': current_replicas,
            'target_replicas': target_replicas,
            'optimal_replicas': optimal_replicas,
            'rule_based_replicas': rule_based_replicas,
            'ml_replicas': ml_replicas,
            'ml_confidence': ml_confidence,
            'decision_source': decision_source,
            'action': action,
            'should_scale': should_scale,
            'reason': reason,
            'scores': scores,
            'confidence': self._calculate_confidence(scores, features)
        }
        
        logger.info(
            f"Decision: {action} | Current: {current_replicas} → Target: {target_replicas} | "
            f"Score: {scores['total_score']:.1f} | Source: {decision_source} | Reason: {reason}"
        )
        
        return decision
    
    def _calculate_confidence(self, scores: Dict[str, float], 
                             features: Dict[str, Any]) -> float:
        """
        Calculate confidence in the decision (0-1)
        
        Args:
            scores: Weighted scores
            features: Feature dictionary
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence on score extremes and trend strength
        total_score = scores['total_score']
        trend_strength = features.get('cpu_trend_strength', 0.0)
        
        # High confidence if score is extreme (very high or very low)
        if total_score > 80 or total_score < 20:
            score_confidence = 0.9
        elif total_score > 60 or total_score < 40:
            score_confidence = 0.7
        else:
            score_confidence = 0.5
        
        # Adjust by trend strength
        confidence = (score_confidence + trend_strength) / 2
        
        return min(confidence, 1.0)


if __name__ == "__main__":
    # Test the decision engine
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize engine
    engine = DecisionEngine(
        target_cpu=500.0,
        target_memory=512.0,
        target_network=10.0,
        min_replicas=1,
        max_replicas=10
    )
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Low Load',
            'features': {
                'pod_count': 3.0,
                'cpu_current': 100.0,
                'memory_current': 150.0,
                'network_total': 2.0,
                'cpu_trend': 0.0,
                'cpu_trend_strength': 0.5
            }
        },
        {
            'name': 'High Load',
            'features': {
                'pod_count': 2.0,
                'cpu_current': 700.0,
                'memory_current': 600.0,
                'network_total': 15.0,
                'cpu_trend': 10.0,
                'cpu_trend_strength': 0.8
            }
        },
        {
            'name': 'Stable Load',
            'features': {
                'pod_count': 3.0,
                'cpu_current': 450.0,
                'memory_current': 480.0,
                'network_total': 8.0,
                'cpu_trend': 0.5,
                'cpu_trend_strength': 0.3
            }
        }
    ]
    
    print("\n" + "="*70)
    print("Decision Engine Test Scenarios")
    print("="*70)
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print("-" * 70)
        
        decision = engine.make_decision(scenario['features'])
        
        print(f"Current Replicas: {decision['current_replicas']}")
        print(f"Target Replicas: {decision['target_replicas']}")
        print(f"Action: {decision['action']}")
        print(f"Reason: {decision['reason']}")
        print(f"Confidence: {decision['confidence']:.2f}")
        print(f"\nScores:")
        print(f"  CPU: {decision['scores']['cpu_score']:.1f}")
        print(f"  Memory: {decision['scores']['memory_score']:.1f}")
        print(f"  Network: {decision['scores']['network_score']:.1f}")
        print(f"  Cost: {decision['scores']['cost_score']:.1f}")
        print(f"  Total: {decision['scores']['total_score']:.1f}")

# Made by Nabanish with Bob's assistance
