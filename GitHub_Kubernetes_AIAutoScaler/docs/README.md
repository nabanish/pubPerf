# AI-Driven Kubernetes Autoscaler

## 🤖 What This Does

This AI autoscaler uses **Machine Learning** to automatically scale your Kubernetes pods based on:
- Historical CPU/memory patterns
- Time of day patterns
- Load trends
- Predictive analysis

**No more hard-coded thresholds!** The AI learns from your application's behavior.

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   AI Autoscaler                          │
│                                                          │
│  1. Collect Metrics ──▶ 2. Train ML Model ──▶ 3. Predict│
│         │                      │                    │    │
│         ▼                      ▼                    ▼    │
│   Kubernetes API        Random Forest         Scale Pods│
└─────────────────────────────────────────────────────────┘
```

### Phase 1: Learning (First 20 samples)
- Collects metrics every 30 seconds
- Uses simple rule-based scaling
- Builds historical dataset

### Phase 2: AI-Driven (After 20+ samples)
- Trains Random Forest model
- Predicts optimal pod count
- Continuously improves

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
cd ~/Desktop/Kubernetes/ai-scaler

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Kubernetes Access

```bash
# Make sure you can access your cluster
kubectl get pods

# Check metrics-server is working
kubectl top pods
```

## 🚀 Usage

### Start the AI Autoscaler

```bash
cd ~/Desktop/Kubernetes/ai-scaler
source venv/bin/activate  # if using venv
python3 ai_scaler.py
```

### What You'll See

```
🤖 AI Autoscaler initialized for tomcat-sample-app
📊 Min replicas: 1, Max replicas: 10
⏱️  Check interval: 30 seconds

🚀 AI Autoscaler started!

============================================================
Iteration #1 - 2025-11-03 20:15:30
============================================================
📊 Current Metrics:
   CPU: 45.2m
   Memory: 234.5Mi
   Pods: 1

🤖 AI Decision:
   Current replicas: 1
   Recommended replicas: 1

✓ No scaling needed

⏳ Waiting 30 seconds...
```

### During JMeter Test

When you run your JMeter performance test, you'll see:

```
============================================================
Iteration #15 - 2025-11-03 20:20:00
============================================================
📊 Current Metrics:
   CPU: 850.3m
   Memory: 456.7Mi
   Pods: 2

🎓 Training ML model...
✅ Model trained on 25 samples

🤖 AI Decision:
   Current replicas: 2
   Recommended replicas: 4

⚡ Scaling from 2 to 4 replicas...
✅ Successfully scaled to 4 replicas
```

## 📊 Features

### Intelligent Scaling
- ✅ Learns from historical patterns
- ✅ Predicts future load
- ✅ Adapts to your application
- ✅ No hard-coded thresholds

### Safety Features
- ✅ Min/max replica limits
- ✅ Gradual scaling
- ✅ Fallback to simple rules
- ✅ Error handling

### Data Collection
- ✅ Saves metrics history (`metrics_history.json`)
- ✅ Saves trained model (`scaler_model.pkl`)
- ✅ Continuous learning

## ⚙️ Configuration

Edit `ai_scaler.py` to customize:

```python
self.min_replicas = 1      # Minimum pods
self.max_replicas = 10     # Maximum pods
self.check_interval = 30   # Check every N seconds
```

## 📈 Monitoring

### Watch in Real-Time

**Terminal 1: Run AI Scaler**
```bash
python3 ai_scaler.py
```

**Terminal 2: Watch Pods**
```bash
watch -n 5 kubectl get pods -l app=tomcat-sample
```

**Terminal 3: Watch Metrics**
```bash
watch -n 5 kubectl top pods -l app=tomcat-sample
```

## 🧪 Testing with JMeter

1. **Start AI Scaler**
   ```bash
   python3 ai_scaler.py
   ```

2. **Start Application Access**
   ```bash
   cd ~/Desktop/Kubernetes
   ./access-tomcat-with-apps.sh
   ```

3. **Run JMeter Test**
   - Target: http://localhost:9091
   - Watch AI scaler automatically adjust pods!

## 📊 Understanding the AI

### Features Used by ML Model

The AI considers:
- **Time patterns:** Hour of day, day of week
- **Current load:** CPU and memory usage
- **Trends:** Is load increasing or decreasing?
- **Moving averages:** Smoothed metrics
- **Historical patterns:** What happened before?

### Decision Making

```python
if len(history) < 20:
    # Phase 1: Simple rules
    if cpu > 800m: scale_up()
    elif cpu < 200m: scale_down()
else:
    # Phase 2: AI predictions
    predicted_replicas = model.predict(features)
    scale_to(predicted_replicas)
```

## 🔧 Troubleshooting

### "Could not get metrics"
```bash
# Check metrics-server is running
kubectl get pods -n kube-system | grep metrics-server

# Test metrics access
kubectl top pods
```

### "Import errors"
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Or install individually
pip install numpy pandas scikit-learn kubernetes
```

### "Permission denied"
```bash
# Make sure kubectl is configured
kubectl get pods

# Check current context
kubectl config current-context
```

## 📁 Files Created

- `metrics_history.json` - Historical metrics data
- `scaler_model.pkl` - Trained ML model
- `ai_scaler.log` - Logs (if enabled)

## 🎓 How It Learns

### Iteration 1-20: Learning Phase
- Collects data
- Uses simple rules
- Builds training dataset

### Iteration 20+: AI Phase
- Trains Random Forest model
- Makes predictions
- Scales based on AI

### Iteration 30+: Continuous Improvement
- Retrains every 10 iterations
- Adapts to new patterns
- Improves accuracy

## 🆚 Comparison

### Before (Hard-Coded HPA)
```yaml
cpu: 70%  # Fixed threshold
min: 1    # Fixed minimum
max: 5    # Fixed maximum
```

### After (AI-Driven)
```python
# Dynamic, learned from your data
predicted_replicas = model.predict([
    hour, day, cpu, memory, trend, ...
])
# Adapts to your application's behavior!
```

## 🎯 Next Steps

1. **Run for 24 hours** to collect diverse data
2. **Analyze patterns** in `metrics_history.json`
3. **Fine-tune** min/max replicas
4. **Experiment** with different ML models

## 📚 Advanced Usage

### Custom ML Model

Replace Random Forest with your own:

```python
from sklearn.neural_network import MLPRegressor

self.model = MLPRegressor(
    hidden_layer_sizes=(100, 50),
    max_iter=1000
)
```

### Add More Features

```python
# In extract_features()
df['is_peak_hour'] = df['hour'].isin([9,10,11,14,15,16])
df['is_weekend'] = df['day_of_week'].isin([5,6])
```

### Export Metrics

```python
# Add to run() loop
with open('scaling_decisions.csv', 'a') as f:
    f.write(f"{timestamp},{cpu},{replicas}\n")
```

## 🎉 Success Metrics

You'll know it's working when:
- ✅ Pods scale up **before** load spikes
- ✅ Pods scale down **after** load drops
- ✅ No manual intervention needed
- ✅ Cost optimized (fewer idle pods)

## 🤝 Support

Questions? Check:
- Main guide: `../ai-driven-autoscaling-guide.md`
- Kubernetes docs: https://kubernetes.io/docs/
- scikit-learn docs: https://scikit-learn.org/

---

**Happy AI Scaling!** 🚀🤖