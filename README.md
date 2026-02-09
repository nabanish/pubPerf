# 🤖 Kubernetes AI-Driven Autoscaler

An intelligent, machine learning-powered Kubernetes autoscaler that uses Random Forest regression to predict optimal pod counts based on real-time metrics and historical patterns.

## 🌟 Features

- **Machine Learning Predictions**: Uses Random Forest regression to learn from historical data
- **Intelligent Scaling**: Combines ML predictions with heuristic rules for robust decision-making
- **Feedback Loop Prevention**: V2 fixes the critical feedback loop issue found in V1
- **Dampening Logic**: Prevents rapid oscillations and unnecessary scaling
- **Feature Engineering**: Time patterns, CPU trends, moving averages, and more
- **Real-time Monitoring**: Tracks CPU, memory, and pod metrics
- **Automatic Model Retraining**: Continuously improves predictions over time

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Testing](#testing)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

### How It Works

1. **Metrics Collection**: Gathers CPU, memory, and pod count from Kubernetes metrics-server
2. **Feature Engineering**: Creates time-based features, trends, and moving averages
3. **ML Prediction**: Random Forest model predicts optimal pod count
4. **Heuristic Validation**: Validates ML predictions against rule-based logic
5. **Dampening**: Prevents unnecessary scaling with intelligent thresholds
6. **Scaling Decision**: Executes scale operations via Kubernetes API

### Key Components

```
┌─────────────────────────────────────────────────────────┐
│                   AI Autoscaler V2                      │
├─────────────────────────────────────────────────────────┤
│  Metrics Collection → Feature Engineering → ML Model    │
│         ↓                    ↓                 ↓        │
│  Heuristic Rules → Dampening Logic → Scale Decision     │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Prerequisites

### System Requirements

- **macOS** (tested on Apple Silicon)
- **Colima** with Kubernetes (k3s)
- **Python 3.8+**
- **kubectl** configured
- **4+ CPU cores** recommended

### Software Installation

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Colima and kubectl
brew install colima kubectl

# Start Colima with Kubernetes
colima start --kubernetes --cpu 4 --memory 8 --disk 50
```

### Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install kubernetes scikit-learn numpy pandas
```

## 🚀 Quick Start

### 1. Deploy Kubernetes Resources

```bash
# Deploy Tomcat application
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml

# Deploy Kubernetes Dashboard (optional)
kubectl apply -f kubernetes-manifests/dashboard-admin.yaml

# Verify deployment
kubectl get pods -n default
```

### 2. Start the AI Autoscaler

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Reset and start autoscaler
./scripts/reset_and_start_v2.sh
```

### 3. Generate Load for Testing

```bash
# Port forward to access Tomcat
kubectl port-forward svc/tomcat-sample-service 9091:8080

# Use JMeter or curl to generate load
# JMeter: 100-200 threads, 60 second ramp-up
# Or use curl in a loop:
for i in {1..1000}; do curl http://localhost:9091/sample/ & done
```

## ⚙️ Configuration

### Autoscaler Parameters

Edit `ai_scaler_v2.py` to customize:

```python
# Scaling limits
self.min_replicas = 1
self.max_replicas = 6

# CPU thresholds (millicores)
self.target_cpu_per_pod = 500
self.scale_up_threshold = 700
self.scale_down_threshold = 200

# Dampening settings
self.dampening_window = 3  # iterations
```

### Deployment Configuration

Edit `kubernetes-manifests/tomcat-with-sample-app.yaml`:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "512Mi"
```

## 🧪 Testing

### Test Scenarios

1. **Scale-Up Test**
   ```bash
   # Generate high load (100-200 threads)
   # Expected: Scale from 1 → 2 → 3+ pods
   ```

2. **Scale-Down Test**
   ```bash
   # Stop load generation
   # Expected: Scale back to 1 pod after cooldown
   ```

3. **ML Model Training**
   ```bash
   # Run for 20+ iterations
   # Expected: ML predictions improve over time
   ```

4. **Extreme Load Test**
   ```bash
   # Generate very high load (300-500 threads)
   # Expected: Scale to max_replicas (6 pods)
   ```

### Monitoring

```bash
# Watch autoscaler logs
python3 ai_scaler_v2.py

# Monitor pods in real-time
watch kubectl get pods

# Check resource usage
kubectl top pods
```

## 📚 Documentation

- **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)**: Comprehensive testing scenarios
- **[V1_VS_V2_COMPARISON.md](docs/V1_VS_V2_COMPARISON.md)**: Feedback loop analysis and fix
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Detailed system architecture (if exists)

## 🔍 Troubleshooting

### Common Issues

**Issue: Autoscaler not scaling**
```bash
# Check if metrics-server is running
kubectl get pods -n kube-system | grep metrics-server

# Verify pod labels
kubectl get pods --show-labels

# Check CPU metrics
kubectl top pods
```

**Issue: "Dampening: difference too small"**
- This is normal behavior preventing oscillations
- CPU must cross scale_up_threshold (700m) to scale up
- Or difference must be >= 2 pods

**Issue: ML model not improving**
- Needs 20+ iterations for first retraining
- Requires diverse load patterns
- Check metrics_history_v2.json for data

### Reset Everything

```bash
# Stop autoscaler (Ctrl+C)

# Clean up
./scripts/stop_and_cleanup.sh

# Start fresh
./scripts/reset_and_start_v2.sh
```

## 📊 Key Metrics

### Scaling Thresholds

| Metric | Value | Purpose |
|--------|-------|---------|
| Target CPU | 500m | Ideal CPU per pod |
| Scale-Up | 700m | Trigger scale-up |
| Scale-Down | 200m | Trigger scale-down |
| Min Replicas | 1 | Minimum pods |
| Max Replicas | 6 | Maximum pods |

### ML Model Features

- Hour of day (0-23)
- Day of week (0-6)
- CPU millicores
- Memory usage
- Current pod count
- CPU trend (5-iteration moving average)
- Load velocity (rate of change)

## 🎯 V1 vs V2 Differences

### V1 Problem: Feedback Loop

```python
# V1 (WRONG): Used num_pods as target
target = metrics['num_pods']  # Feedback loop!
```

**Result**: Autoscaler maintained current state instead of predicting optimal state.

### V2 Solution: Calculate Optimal Pods

```python
# V2 (CORRECT): Calculate optimal from load
optimal_pods = total_cpu / target_cpu_per_pod
```

**Result**: Autoscaler predicts optimal state based on actual load.

See [V1_VS_V2_COMPARISON.md](docs/V1_VS_V2_COMPARISON.md) for detailed analysis.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional ML models (LSTM, Prophet)
- Memory-based scaling
- Multi-metric optimization
- Predictive scaling (time-series forecasting)
- Cost optimization features

## 📝 License

This software is IBM Confidential.

PID 5900-AST, 5900-BJ5, 5900-AQE, 5737-L66, 5737-L74

© Copyright IBM Corp. 2019, 2025

## 👨‍💻 Author

**Made by Nabanish Sinha**

## � Acknowledgments

- Kubernetes community for excellent documentation
- scikit-learn for ML capabilities
- Colima for lightweight Kubernetes on macOS

## 📧 Contact

For questions or issues, please contact nabanishs@gmail.com or +91-9007084606

---

**Happy Autoscaling! 🚀**