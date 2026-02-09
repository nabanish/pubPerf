# AI Autoscaler V2 - Testing Guide

## 🎯 What We're Testing

The improved AI autoscaler that:
- ✅ No feedback loop (calculates optimal pods from CPU load)
- ✅ Target-based scaling (aims for 500m CPU per pod)
- ✅ Max 3 replicas (to avoid resource exhaustion)
- ✅ Dampening to prevent oscillations

---

## 📊 Current Setup

**Cluster**: Colima with k3s (4 CPU, 8GB RAM)
**Deployment**: tomcat-sample-app
**Current Pods**: 1
**Service**: Port-forwarded to localhost:9091
**Pod Label**: `app=tomcat-sample` (NOT `app=tomcat-sample-app`)

---

## 🧪 Test Scenarios

### Scenario 1: Baseline (No Load)
**Expected Behavior:**
- AI scaler collects metrics every 30 seconds
- CPU should be very low (< 10m per pod)
- Should maintain 1 pod
- After 20 samples (10 minutes), ML model trains

**Monitor:**
```bash
# Terminal 2
watch -n 5 'kubectl get pods -l app=tomcat-sample'
```

### Scenario 2: Light Load
**Generate Load:**
```bash
# Terminal 3
for i in {1..100}; do curl http://localhost:9091 > /dev/null 2>&1 & done
```

**Expected Behavior:**
- CPU increases to ~100-300m per pod
- Should stay at 1 pod (below 500m target)
- AI learns this is normal load

### Scenario 3: Medium Load
**Generate Load:**
```bash
# Terminal 3
while true; do curl http://localhost:9091 > /dev/null 2>&1; sleep 0.1; done
```

**Expected Behavior:**
- CPU increases to ~600-800m per pod
- Should scale UP to 2 pods
- Total CPU ~1200-1600m across 2 pods
- CPU per pod drops to ~600-800m

### Scenario 4: High Load
**Generate Load:**
```bash
# Terminal 3 (run 2-3 of these in parallel)
while true; do curl http://localhost:9091 > /dev/null 2>&1; done
```

**Expected Behavior:**
- CPU increases significantly
- Should scale UP to 3 pods (max)
- Distributes load across 3 pods
- CPU per pod should stabilize around 500-700m

### Scenario 5: Scale Down
**Stop Load:**
```bash
# Terminal 3 - Press Ctrl+C to stop load
```

**Expected Behavior:**
- CPU drops significantly
- After dampening period, scales DOWN to 2 pods
- Eventually scales DOWN to 1 pod
- Takes time due to dampening (prevents rapid oscillation)

---

## 📈 What to Watch For

### Good Signs ✅
- Stable at 1 pod with no load
- Scales up when CPU > 700m per pod
- Scales down when CPU < 200m per pod
- No rapid oscillations (dampening works)
- ML model trains after 20 samples

### Warning Signs ⚠️
- Rapid scaling up/down (oscillation)
- Pods stuck in Pending state (resource exhaustion)
- CPU spikes during pod startup (normal, should stabilize)
- Errors in autoscaler output

### Red Flags 🚨
- Scales to max (3) with no load
- Never scales down
- Constant pod creation/termination
- "Insufficient CPU" errors

---

## 🔍 Monitoring Commands

### Watch Pods (Correct Label!)
```bash
watch -n 5 'kubectl get pods -l app=tomcat-sample'
```

### Check Deployment
```bash
kubectl get deployment tomcat-sample-app
```

### Check Pod Details
```bash
kubectl describe pod <pod-name>
```

### Check Metrics
```bash
kubectl top pods -l app=tomcat-sample
```

### View Autoscaler Logs
The autoscaler prints to stdout, so just watch Terminal 1

---

## 📊 Expected Timeline

| Time | Event | Expected State |
|------|-------|----------------|
| 0:00 | Start autoscaler | 1 pod, collecting metrics |
| 0:30 | Iteration 1 | 1 pod, heuristic mode |
| 10:00 | Iteration 20 | ML model trains |
| 10:30 | Iteration 21 | AI mode activated |
| 15:00 | Generate load | Scales to 2-3 pods |
| 20:00 | Stop load | Scales back to 1 pod |

---

## 🎓 Learning Points

### Phase 1: Heuristic Mode (0-20 samples)
- Uses simple rules
- Collects data for ML training
- Should be stable at 1 pod (no load)

### Phase 2: AI Mode (20+ samples)
- ML model predicts optimal pods
- Learns time patterns
- Learns load patterns
- Makes intelligent predictions

### Key Metrics
- **CPU per pod**: Target is 500m
- **Total CPU**: Sum across all pods
- **Optimal pods**: total_cpu / 500m
- **Dampening**: Prevents scaling unless difference >= 2 or at extremes

---

## 🛠️ Troubleshooting

### Problem: Autoscaler not scaling
**Check:**
- Is it in heuristic mode? (needs 20 samples)
- Is dampening preventing it? (difference < 2)
- Check autoscaler output for errors

### Problem: Pods stuck in Pending
**Cause:** Cluster out of resources
**Fix:** 
```bash
kubectl scale deployment tomcat-sample-app --replicas=1
```

### Problem: Rapid oscillations
**Cause:** Dampening not working
**Check:** V2 code has dampening logic (line 359)

### Problem: Wrong pod count
**Check:** Using correct label `app=tomcat-sample`

---

## 📝 Notes

- First 10 minutes: Data collection phase
- ML model needs 20+ samples to train
- Dampening prevents rapid changes
- Pod startup consumes CPU (temporary spike)
- Scale-down is slower than scale-up (by design)

---

**Ready to test!** Start the autoscaler and follow the scenarios above.