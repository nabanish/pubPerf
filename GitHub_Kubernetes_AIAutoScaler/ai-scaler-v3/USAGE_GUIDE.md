# AI Scaler V3 - Complete Usage Guide

## 🎯 How to Run AI Scaler V3

### Step 1: Verify Prerequisites

```bash
# Check Kubernetes cluster
kubectl cluster-info

# Check Prometheus is running
kubectl get pods -n monitoring

# Check target deployment exists
kubectl get deployment tomcat-sample-app
```

### Step 2: Start the Autoscaler

**Option A: Using the start script (Recommended)**

```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3
./start_v3.sh
```

The script will automatically:
- ✓ Verify Kubernetes connection
- ✓ Check Prometheus accessibility
- ✓ Validate target deployment
- ✓ Start the autoscaler

**Option B: Manual start**

```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3
source venv/bin/activate
python3 ai_scaler_v3.py --config config.yaml
```

### Step 3: Monitor the Autoscaler

**Watch the logs in real-time:**

```bash
tail -f ai_scaler_v3.log
```

**In another terminal, watch pod scaling:**

```bash
watch kubectl get pods
```

**View in Grafana:**

1. Open: http://localhost:30300
2. Login: admin/admin123
3. Go to "AI Autoscaler Dashboard"

### Step 4: Stop the Autoscaler

**Option A: Using the stop script**

```bash
./stop_v3.sh
```

**Option B: Manual stop**

Press `Ctrl+C` in the terminal running the autoscaler.

## 📊 Understanding the Output

### Typical Scaling Cycle Output

```
======================================================================
Scaling Cycle - 2025-11-04 21:30:00
======================================================================
Current replicas: 1
Extracting features from Prometheus...
CPU Usage: 45.2%
Memory Usage: 52.1%
Network I/O: 8.45 MB/s
Making scaling decision...
Decision: no_change
Target replicas: 1
Confidence: 0.60
Reason: No scaling needed (dampening)
Weighted score: 52.3
✓ No scaling action needed
Sleeping for 30s...
```

### Decision Types

1. **scale_up**: Increasing replicas due to high load
   ```
   Decision: scale_up
   Target replicas: 3
   Reason: High load: score=87.3
   ⬆ Scaling up: 1 → 3
   ```

2. **scale_down**: Decreasing replicas due to low load
   ```
   Decision: scale_down
   Target replicas: 1
   Reason: Low load: score=25.8
   ⬇ Scaling down: 3 → 1
   ```

3. **no_change**: No scaling needed
   ```
   Decision: no_change
   Reason: No scaling needed (dampening)
   ✓ No scaling action needed
   ```

### Dampening Reasons

The autoscaler may block scaling for these reasons:

1. **Score threshold**: `Score difference too small: 12.3 < 15.0`
2. **Large difference**: `Large difference: 3 pods`
3. **Rapid trend**: `Rapid trend detected`
4. **Boundary check**: `At minimum replicas`
5. **Cooldown**: `Cooldown active: 45s remaining`

## 🧪 Testing Scenarios

### Test 1: Normal Operation (No Load)

```bash
# Start autoscaler
./start_v3.sh

# Expected: Maintains 1 replica
# Watch logs for "no_change" decisions
```

### Test 2: Simulate High CPU Load

```bash
# In another terminal, generate load
kubectl run load-generator --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://tomcat-sample-app:8080; done"

# Expected: Scales up to 2-3 replicas
# Watch logs for "scale_up" decisions

# Cleanup
kubectl delete pod load-generator
```

### Test 3: Scale Down After Load

```bash
# After stopping load generator
# Expected: Gradually scales down to 1 replica
# Watch logs for "scale_down" decisions
```

### Test 4: Rapid Load Changes

```bash
# Start multiple load generators
for i in {1..3}; do
  kubectl run load-generator-$i --image=busybox --restart=Never -- \
    /bin/sh -c "while true; do wget -q -O- http://tomcat-sample-app:8080; done"
done

# Expected: Scales up but with dampening to prevent flapping
# Watch logs for dampening messages

# Cleanup
kubectl delete pod load-generator-1 load-generator-2 load-generator-3
```

## 📈 Monitoring and Metrics

### View Current Metrics

```bash
# Check current pod count
kubectl get deployment tomcat-sample-app

# Check pod resource usage
kubectl top pods

# Check autoscaler logs
tail -20 ai_scaler_v3.log
```

### Grafana Dashboards

**AI Autoscaler Dashboard** shows:
- Current replica count
- CPU usage over time
- Memory usage over time
- Network I/O
- Scaling decisions
- Weighted scores
- Confidence levels
- Dampening events

### Prometheus Queries

Access Prometheus at http://localhost:30090 and try these queries:

```promql
# Current pod count
count(kube_pod_info{namespace="default", pod=~"tomcat-sample-app.*"})

# CPU usage
rate(container_cpu_usage_seconds_total{namespace="default", pod=~"tomcat-sample-app.*"}[5m]) * 100

# Memory usage
container_memory_working_set_bytes{namespace="default", pod=~"tomcat-sample-app.*"} / 1024 / 1024

# Network I/O
rate(container_network_receive_bytes_total{namespace="default", pod=~"tomcat-sample-app.*"}[5m])
```

## 🔧 Configuration Tuning

### Adjust Scaling Sensitivity

**More aggressive scaling:**

```yaml
scaling:
  check_interval: 15  # Check more frequently
  cooldown_period: 30  # Shorter cooldown

dampening:
  score_threshold: 10.0  # Lower threshold
```

**More conservative scaling:**

```yaml
scaling:
  check_interval: 60  # Check less frequently
  cooldown_period: 120  # Longer cooldown

dampening:
  score_threshold: 20.0  # Higher threshold
```

### Adjust Metric Priorities

**CPU-focused:**

```yaml
weights:
  cpu: 0.6      # Increase CPU weight
  memory: 0.2
  network: 0.1
  cost: 0.1
```

**Cost-optimized:**

```yaml
weights:
  cpu: 0.3
  memory: 0.2
  network: 0.1
  cost: 0.4      # Increase cost weight
```

### Adjust Target Thresholds

**Higher utilization targets:**

```yaml
thresholds:
  cpu_target: 80.0      # Allow higher CPU
  memory_target: 80.0   # Allow higher memory
```

**Lower utilization targets:**

```yaml
thresholds:
  cpu_target: 60.0      # Scale earlier
  memory_target: 60.0
```

## 🐛 Troubleshooting

### Issue: Autoscaler won't start

**Check 1: Kubernetes connection**
```bash
kubectl cluster-info
# If fails: colima start --kubernetes
```

**Check 2: Prometheus accessibility**
```bash
curl http://localhost:30090/api/v1/query?query=up
# If fails: kubectl port-forward -n monitoring svc/prometheus 30090:9090
```

**Check 3: Target deployment**
```bash
kubectl get deployment tomcat-sample-app
# If not found: Deploy the sample app first
```

### Issue: No scaling actions

**Check 1: Metrics availability**
```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3
source venv/bin/activate
python3 prometheus_client.py
```

**Check 2: Dampening logs**
```bash
grep "dampening" ai_scaler_v3.log
# Look for reasons why scaling is blocked
```

**Check 3: Cooldown period**
```bash
grep "Cooldown" ai_scaler_v3.log
# Check if cooldown is blocking scaling
```

### Issue: Metrics showing zero

**Wait 2-3 minutes** after deployment for Prometheus to collect metrics.

```bash
# Check if metrics are being scraped
kubectl logs -n monitoring prometheus-<pod-id> | grep tomcat
```

### Issue: Excessive scaling (flapping)

**Increase dampening:**

```yaml
dampening:
  score_threshold: 20.0      # Increase from 15.0
  large_difference: 3        # Increase from 2
```

**Increase cooldown:**

```yaml
scaling:
  cooldown_period: 120  # Increase from 60
```

## 📊 Performance Expectations

### Typical Behavior

- **Check interval**: 30 seconds
- **Cooldown period**: 60 seconds
- **Scale up time**: 1-2 minutes (including cooldown)
- **Scale down time**: 2-3 minutes (more conservative)
- **Metrics lag**: 2-3 minutes for new pods

### Resource Usage

- **CPU**: ~5-10% of one core
- **Memory**: ~100-200 MB
- **Network**: Minimal (Prometheus queries only)

## 🎓 Best Practices

1. **Start with defaults**: Run with default config first
2. **Monitor for 1 hour**: Observe behavior before tuning
3. **Tune gradually**: Change one parameter at a time
4. **Test with load**: Use load generators to validate
5. **Check Grafana**: Use dashboards for insights
6. **Review logs**: Look for patterns in decisions
7. **Adjust weights**: Based on your workload priorities

## 📝 Example Workflows

### Workflow 1: Production Deployment

```bash
# 1. Verify environment
kubectl cluster-info
kubectl get pods -n monitoring

# 2. Review configuration
cat config.yaml

# 3. Start autoscaler
./start_v3.sh

# 4. Monitor in Grafana
open http://localhost:30300

# 5. Check logs periodically
tail -f ai_scaler_v3.log
```

### Workflow 2: Load Testing

```bash
# 1. Start autoscaler
./start_v3.sh

# 2. In another terminal, generate load
kubectl run load-test --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://tomcat-sample-app:8080; done"

# 3. Watch scaling
watch kubectl get pods

# 4. Monitor decisions
tail -f ai_scaler_v3.log

# 5. Stop load
kubectl delete pod load-test

# 6. Watch scale down
watch kubectl get pods
```

### Workflow 3: Configuration Tuning

```bash
# 1. Stop autoscaler
./stop_v3.sh

# 2. Edit configuration
nano config.yaml

# 3. Restart autoscaler
./start_v3.sh

# 4. Monitor behavior
tail -f ai_scaler_v3.log

# 5. Compare with previous runs
grep "Decision:" ai_scaler_v3.log | tail -20
```

## 🔗 Related Documentation

- [README.md](README.md) - Overview and features
- [config.yaml](config.yaml) - Configuration reference
- [PHASE3_ARCHITECTURE.md](../docs/PHASE3_ARCHITECTURE.md) - Architecture details
- [QUICKSTART_PHASE3.md](../docs/QUICKSTART_PHASE3.md) - Quick start guide

---

**Need Help?** Check the troubleshooting section or review the logs for detailed error messages.