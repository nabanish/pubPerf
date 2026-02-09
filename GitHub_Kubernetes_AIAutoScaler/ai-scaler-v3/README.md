# AI Scaler V3 - ML-Powered Multi-Metric Kubernetes Autoscaler

Advanced AI-driven Kubernetes autoscaler with **Machine Learning**, multi-metric optimization, and Prometheus integration.

## 🚀 Features

- **🤖 Machine Learning**: RandomForestRegressor with continuous learning and model persistence
- **🎯 Hybrid Decision System**: ML predictions (>60% confidence) with rule-based fallback
- **📊 Multi-Metric Optimization**: Considers CPU, Memory, Network I/O, and Cost
- **⚖️ Weighted Scoring System**: Configurable weights for each metric (default: CPU 40%, Memory 30%, Network 20%, Cost 10%)
- **📈 Prometheus Integration**: Real-time metrics collection from Kubernetes cluster
- **🔧 Feature Engineering**: Extracts 37+ features including historical trends, patterns, and time-based features
- **🛡️ Enhanced Dampening**: 5-condition dampening logic to prevent flapping
- **💰 Cost Optimization**: Considers pod costs in scaling decisions
- **✅ Confidence Scoring**: Each decision includes a confidence score
- **💾 Model Persistence**: Saves and loads trained models using joblib
- **📝 Comprehensive Logging**: Detailed logs with ML statistics for debugging and monitoring

## 📋 Prerequisites

1. **Kubernetes Cluster**: Running k3s cluster (via Colima or similar)
2. **Prometheus**: Deployed and accessible (see Phase 2 setup)
3. **Python 3.8+**: With virtual environment support
4. **kubectl**: Configured to access your cluster

## 🛠️ Installation

### 1. Create Virtual Environment

```bash
cd ai-scaler-v3
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

Edit `config.yaml` to match your environment:

```yaml
prometheus:
  url: "http://localhost:30090"

target:
  namespace: "default"
  deployment: "tomcat-sample-app"

scaling:
  min_replicas: 1
  max_replicas: 10
  check_interval: 30
  cooldown_period: 60

weights:
  cpu: 0.4
  memory: 0.3
  network: 0.2
  cost: 0.1
```

## 🎯 Quick Start

### Start the Autoscaler

```bash
./start_v3.sh
```

The script will:
- ✓ Check Kubernetes connection
- ✓ Verify Prometheus is accessible
- ✓ Validate target deployment exists
- ✓ Start the autoscaler

### Stop the Autoscaler

```bash
./stop_v3.sh
```

Or press `Ctrl+C` in the terminal running the autoscaler.

## 📊 How It Works

### 1. Feature Extraction

Every 30 seconds (configurable), the autoscaler extracts 37+ features:

**Current State (8 features)**:
- Pod count, CPU usage, memory usage, network I/O
- CPU/memory requests and limits
- Pod age

**Historical Metrics (10 features)**:
- CPU/memory usage over 5m, 15m, 30m, 1h, 2h

**Time-Based Features (6 features)**:
- Hour of day, day of week, is business hours
- Is peak hours, is weekend, time since last scale

**Trend Features (7 features)**:
- CPU/memory/network trends
- Rate of change, acceleration

**Pattern Features (6 features)**:
- CPU/memory volatility and stability
- Load patterns

### 2. Machine Learning Prediction

**ML Model**: RandomForestRegressor with 100 estimators
- **Training**: Starts after 20 samples, retrains every 10 samples
- **Persistence**: Model saved to `models/scaler_model.pkl` using joblib
- **Features**: Uses all 37+ extracted features
- **Output**: Predicted optimal replicas + confidence score

**Continuous Learning**:
```python
# After each scaling decision
ml_predictor.add_training_sample(features, actual_replicas)
# Model automatically retrains every 10 samples
```

### 3. Weighted Scoring (Rule-Based Fallback)

Each metric is scored 0-100 and weighted:

```
Total Score = (CPU × 0.4) + (Memory × 0.3) + (Network × 0.2) + (Cost × 0.1)
```

**CPU Score**: Based on current usage vs target (70%)
**Memory Score**: Based on current usage vs target (70%)
**Network Score**: Based on I/O rate vs threshold
**Cost Score**: Considers pod costs and scale-down preference

### 4. Hybrid Decision System

The autoscaler uses a **hybrid approach**:

```python
if ml_confidence > 0.6:
    # Use ML prediction (high confidence)
    optimal_replicas = ml_prediction
    decision_source = "ML"
else:
    # Fallback to rule-based scoring
    optimal_replicas = rule_based_calculation(weighted_score)
    decision_source = "Rule-based"
```

**Benefits**:
- ✅ ML learns optimal patterns over time
- ✅ Rule-based provides stable fallback
- ✅ Confidence threshold prevents bad ML decisions
- ✅ Best of both worlds

### 5. Optimal Replica Calculation (Rule-Based)

Based on weighted scores:
- **Score < 30**: Scale down
- **Score 30-70**: Maintain current replicas
- **Score > 70**: Scale up

### 6. Enhanced Dampening

Scaling is blocked if any condition is met:
1. **Score threshold**: Score difference < 15 points
2. **Large difference**: Scaling by 2+ replicas
3. **Rapid trend**: Metrics changing rapidly
4. **Boundary check**: At min/max replicas
5. **Cooldown period**: Recent scaling action (60s default)

### 7. Scaling Decision

If dampening allows, the autoscaler:
- Calculates target replicas (ML or rule-based)
- Logs decision with confidence score and source
- Executes scaling via Kubernetes API
- Records action in history
- **Adds sample to ML training data**

## 📈 Monitoring

### View Logs

```bash
tail -f ai_scaler_v3.log
```

### Check Current Status

```bash
kubectl get deployment tomcat-sample-app
kubectl get pods
```

### View in Grafana

1. Open Grafana: http://localhost:30300
2. Login: admin/admin123
3. Navigate to "AI Autoscaler Dashboard"

## 🔧 Configuration Options

### Scaling Parameters

```yaml
scaling:
  min_replicas: 1        # Minimum number of replicas
  max_replicas: 10       # Maximum number of replicas
  check_interval: 30     # Seconds between checks
  cooldown_period: 60    # Seconds to wait after scaling
```

### Metric Weights

Adjust weights based on your priorities (must sum to 1.0):

```yaml
weights:
  cpu: 0.4      # CPU usage importance
  memory: 0.3   # Memory usage importance
  network: 0.2  # Network I/O importance
  cost: 0.1     # Cost optimization importance
```

### Target Thresholds

```yaml
thresholds:
  cpu_target: 70.0      # Target CPU usage %
  memory_target: 70.0   # Target memory usage %
  network_target: 70.0  # Target network usage %
```

### Dampening Configuration

```yaml
dampening:
  score_threshold: 15.0      # Min score difference to scale
  large_difference: 2        # Replicas considered "large"
  rapid_trend_threshold: 5.0 # Rapid change threshold
  boundary_buffer: 0.1       # Buffer for min/max (10%)
```

## 📝 Example Output

### With ML Prediction (High Confidence)
```
======================================================================
Scaling Cycle - 2025-12-02 21:30:00
======================================================================
Current replicas: 2
Extracting features from Prometheus...
CPU Usage: 85.2%
Memory Usage: 72.1%
Network I/O: 12.45 MB/s
ML Stats: 27 samples, trained: True
Making scaling decision...
ML prediction: 4 (confidence: 0.87)
Decision: scale_up
Target replicas: 4
Confidence: 0.87
Decision source: ML (confidence: 0.87)
Reason: High load: score=87.3
Weighted score: 87.3
⬆ Scaling up: 2 → 4
✓ Scaled deployment to 4 replicas
```

### With Rule-Based Fallback (Low ML Confidence)
```
======================================================================
Scaling Cycle - 2025-12-02 21:35:00
======================================================================
Current replicas: 4
Extracting features from Prometheus...
CPU Usage: 45.3%
Memory Usage: 52.1%
Network I/O: 5.23 MB/s
ML Stats: 28 samples, trained: True
Making scaling decision...
ML prediction: 3 (confidence: 0.52)
Decision: maintain
Target replicas: 4
Confidence: 0.75
Decision source: Rule-based (ML confidence too low: 0.52)
Reason: Moderate load: score=48.5
Weighted score: 48.5
→ Maintaining current replicas: 4
```

## 🧪 Testing

### Test Individual Components

```bash
# Test Prometheus client
python prometheus_client.py

# Test feature engineering
python feature_engineering.py

# Test decision engine
python decision_engine.py
```

### Simulate Load

```bash
# Generate CPU load
kubectl run load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://tomcat-sample-app:8080; done"

# Watch scaling
watch kubectl get pods
```

## 🐛 Troubleshooting

### Autoscaler Not Starting

1. Check Kubernetes connection:
   ```bash
   kubectl cluster-info
   ```

2. Verify Prometheus is accessible:
   ```bash
   curl http://localhost:30090/api/v1/query?query=up
   ```

3. Check target deployment exists:
   ```bash
   kubectl get deployment tomcat-sample-app
   ```

### No Scaling Actions

1. Check logs for dampening reasons:
   ```bash
   grep "dampening" ai_scaler_v3.log
   ```

2. Verify metrics are being collected:
   ```bash
   python prometheus_client.py
   ```

3. Check cooldown period hasn't blocked scaling:
   ```bash
   grep "Cooldown" ai_scaler_v3.log
   ```

### Metrics Showing Zero

Wait 2-3 minutes after deployment for Prometheus to collect metrics.

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Scaler V3                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐ │
│  │  Prometheus  │───▶│   Feature    │───▶│   ML Predictor   │ │
│  │    Client    │    │  Engineering │    │  (RandomForest)  │ │
│  └──────────────┘    └──────────────┘    └──────────────────┘ │
│         │                    │                    │            │
│         │                    │                    ▼            │
│         │                    │            ┌──────────────────┐ │
│         │                    │            │  Model Storage   │ │
│         │                    │            │  (joblib .pkl)   │ │
│         │                    │            └──────────────────┘ │
│         │                    │                    │            │
│         │                    ▼                    ▼            │
│         │            ┌────────────────────────────────────┐   │
│         │            │      Decision Engine               │   │
│         │            │  ┌──────────────────────────────┐  │   │
│         │            │  │  Hybrid Decision System:     │  │   │
│         │            │  │  • ML (confidence > 60%)     │  │   │
│         │            │  │  • Rule-based (fallback)     │  │   │
│         │            │  └──────────────────────────────┘  │   │
│         │            └────────────────────────────────────┘   │
│         │                            │                        │
│         ▼                            ▼                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Kubernetes API Client                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           │  (Feedback Loop)                   │
│                           ▼                                    │
│                  ┌─────────────────┐                          │
│                  │  Training Data  │◀─────────────────────────┤
│                  │  Collection     │                          │
│                  └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │   Kubernetes     │
                  │   Deployment     │
                  └──────────────────┘
```

## 🔄 Comparison with V2

| Feature | V2 | V3 |
|---------|----|----|
| **ML Algorithm** | RandomForest (only) | **Hybrid: RandomForest + Rules** |
| **Model Persistence** | No | **Yes (joblib)** |
| **Continuous Learning** | No | **Yes (retrains every 10 samples)** |
| **Decision System** | ML only | **Hybrid (ML + rule-based fallback)** |
| **Confidence Threshold** | No | **Yes (60% for ML)** |
| Metrics | CPU only | CPU, Memory, Network, Cost |
| Data Source | kubectl | Prometheus |
| Features | 5 basic | 37+ advanced |
| Scoring | Simple threshold | Weighted multi-metric |
| Dampening | 3 conditions | 5 conditions |
| Cost Aware | No | Yes |
| Historical Data | Limited | 15 minutes lookback |

## 📄 Files

- `ai_scaler_v3.py` - Main autoscaler implementation
- `ml_predictor.py` - **ML model with RandomForestRegressor and persistence**
- `prometheus_client.py` - Prometheus query client
- `feature_engineering.py` - Feature extraction module
- `decision_engine.py` - Hybrid decision logic (ML + rule-based)
- `config.yaml` - Configuration file
- `requirements.txt` - Python dependencies (includes scikit-learn, joblib)
- `start_v3.sh` - Start script
- `stop_v3.sh` - Stop script
- `models/` - **Directory for saved ML models (.pkl files)**
- `README.md` - This file
- `ALGORITHM_V3.md` - Detailed algorithm documentation

## 🤝 Contributing

This is an internal IBM project. For questions or improvements, contact the development team.

## 📜 License

IBM Confidential - Internal Use Only

---

**Version**: 3.0.0  
**Last Updated**: 2025-11-04  
**Status**: Production Ready