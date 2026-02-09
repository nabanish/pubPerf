# AI Autoscaler: V1 vs V2 Comparison

## 🐛 Problem with V1

### The Feedback Loop Issue

**V1 Code (Line 214):**
```python
y = df['num_pods'].values  # ❌ WRONG: Using current pod count as target
```

**What happened:**
1. V1 trained the ML model to predict `num_pods` (current number of pods)
2. The model learned: "When I see 6 pods running, I should predict 6 pods"
3. This created a **feedback loop** where the model reinforced whatever state it was in
4. Even with low CPU (2.5m), it kept predicting 6 pods because that's what it learned

**Why it's wrong:**
- The model learned to predict the **current state**, not the **optimal state**
- It couldn't adapt to changing load conditions
- It kept scaling up because it learned "more pods = normal"

### Example from Your Run:
```
CPU: 2.5m (very low!)
Pods: 6
AI Prediction: 6 pods ❌ (should be 1-2 pods)
```

The model saw 6 pods in history and predicted 6 pods, ignoring the actual CPU load.

---

## ✅ Solution in V2

### Fixed Target Calculation

**V2 Code (Lines 207-211):**
```python
# Calculate optimal pods for each historical point
df['optimal_pods'] = df.apply(
    lambda row: max(1, int(np.ceil(row['total_cpu'] / self.target_cpu_per_pod))),
    axis=1
)
```

**What changed:**
1. V2 calculates the **optimal** number of pods based on CPU load
2. Target: 500m CPU per pod (configurable)
3. Formula: `optimal_pods = total_cpu / target_cpu_per_pod`
4. The model learns to predict optimal pods based on load patterns, not current state

**Why it's better:**
- Model learns: "When total CPU is 3000m, I need 6 pods (3000/500)"
- Model learns: "When total CPU is 100m, I need 1 pod (100/500)"
- No feedback loop - predictions based on actual load

### Example with V2:
```
CPU per pod: 2.5m
Total CPU: 15m (6 pods × 2.5m)
Optimal by formula: 1 pod (15m / 500m = 0.03 → round up to 1)
AI Prediction: 1 pod ✅
```

---

## 🔑 Key Improvements in V2

### 1. **No Feedback Loop**
- **V1**: Predicts based on `num_pods` (current state)
- **V2**: Predicts based on `total_cpu` and load patterns

### 2. **Target-Based Scaling**
```python
self.target_cpu_per_pod = 500  # Target 500m CPU per pod
self.scale_up_threshold = 700  # Scale up if > 700m per pod
self.scale_down_threshold = 200  # Scale down if < 200m per pod
```

### 3. **Better Features**
**V1 Features:**
- hour, day_of_week, minute
- cpu_millicores, memory_mi
- cpu_trend, mem_trend
- cpu_ma_5, mem_ma_5

**V2 Features (added):**
- `total_cpu` - Total CPU across all pods
- `total_cpu_trend` - Trend in total CPU
- `total_cpu_ma_5` - Moving average of total CPU

### 4. **Dampening to Prevent Oscillation**
```python
# Only scale if difference is significant
should_scale = (
    abs(predicted_replicas - current_replicas) >= 2 or
    (predicted_replicas == min_replicas and cpu < 100) or
    (predicted_replicas == max_replicas and cpu > 800)
)
```

This prevents rapid back-and-forth scaling.

### 5. **Separate History Files**
- V1: `metrics_history.json`, `scaler_model.pkl`
- V2: `metrics_history_v2.json`, `scaler_model_v2.pkl`

Both versions can coexist without interfering.

---

## 📊 Expected Behavior Comparison

### Scenario: Low Load (10m total CPU)

| Metric | V1 Behavior | V2 Behavior |
|--------|-------------|-------------|
| Current Pods | 6 | 6 |
| CPU per Pod | 1.7m | 1.7m |
| Total CPU | 10m | 10m |
| V1 Prediction | 6 pods ❌ | - |
| V2 Prediction | - | 1 pod ✅ |
| Reasoning | "I learned 6 is normal" | "10m/500m = 1 pod needed" |

### Scenario: High Load (3000m total CPU)

| Metric | V1 Behavior | V2 Behavior |
|--------|-------------|-------------|
| Current Pods | 2 | 2 |
| CPU per Pod | 1500m | 1500m |
| Total CPU | 3000m | 3000m |
| V1 Prediction | 2 pods ❌ | - |
| V2 Prediction | - | 6 pods ✅ |
| Reasoning | "I learned 2 is normal" | "3000m/500m = 6 pods needed" |

---

## 🚀 How to Switch to V2

### Step 1: Stop V1
```bash
# Press Ctrl+C in the terminal running ai_scaler.py
```

### Step 2: Reset and Start V2
```bash
cd ~/Desktop/Kubernetes/ai-scaler
./reset_and_start_v2.sh
```

This will:
- Backup V1 metrics and model
- Scale deployment to 1 pod (baseline)
- Prepare for V2

### Step 3: Start V2
```bash
source venv/bin/activate
python3 ai_scaler_v2.py
```

---

## 🎓 Learning Points

### Machine Learning Pitfall: Target Leakage
**V1 suffered from "target leakage"** - using information about the outcome (num_pods) to predict the outcome itself.

**Correct approach (V2):**
1. Define what "optimal" means (500m CPU per pod)
2. Calculate optimal pods from load metrics
3. Train model to predict optimal pods based on patterns
4. Model learns time-based patterns, load trends, etc.

### Feature Engineering
**Bad feature:** `num_pods` (creates feedback loop)
**Good features:** `total_cpu`, `cpu_trend`, `hour`, `day_of_week`

### Model Validation
Always ask: "Is my model learning the right thing?"
- V1: ❌ Learning to maintain current state
- V2: ✅ Learning to predict optimal state based on load

---

## 📈 Expected V2 Results

After 20+ samples, V2 should:
1. **Scale down** when CPU is low (< 200m per pod)
2. **Scale up** when CPU is high (> 700m per pod)
3. **Learn patterns** like "high load at 3 PM, scale up proactively"
4. **Stabilize** around target (500m CPU per pod)

### Monitoring V2
Watch for these indicators of success:
- ✅ Scales down when load drops
- ✅ Scales up when load increases
- ✅ CPU per pod stays around 500m target
- ✅ No rapid oscillations (dampening works)

---

## 🔧 Tuning V2

You can adjust these parameters in `ai_scaler_v2.py`:

```python
self.target_cpu_per_pod = 500  # Lower = more aggressive scaling
self.scale_up_threshold = 700   # When to scale up
self.scale_down_threshold = 200 # When to scale down
self.min_replicas = 1           # Minimum pods
self.max_replicas = 10          # Maximum pods
```

---

## 🎯 Conclusion

**V1 Problem:** Feedback loop caused model to maintain current state regardless of load

**V2 Solution:** Calculate optimal pods from load, train model to predict optimal state

**Result:** AI that actually responds to load changes and learns useful patterns!

---

*Made by Nabanish with the help of Bob - Fixing ML feedback loops in production! 🤖*