# AI Scaler V3 Metrics Fix

## Problem
AI Scaler V3 was showing all metrics as 0.0% (CPU: 0.0%, Memory: 0.0%, Network: 0.00 MB/s) even though Grafana dashboard was successfully displaying metrics (CPU: 892 millicores, Memory: 279 MB, Network: 47.5 MB/s).

## Root Causes
There were TWO issues preventing metrics from displaying correctly:

### Issue 1: Prometheus Query Filter
The `prometheus_client.py` file was using Prometheus queries with a `container!=""` label filter, which doesn't exist in K3s/Colima's cAdvisor metrics. This is the same issue we encountered with the Grafana dashboard.

### Issue 2: Feature Key Mismatch
The `ai_scaler_v3.py` file was looking for feature keys that didn't match what `feature_engineering.py` was returning:
- AI Scaler expected: `cpu_usage_avg`, `memory_usage_avg`, `network_io_total`
- Feature engineering returned: `cpu_current`, `memory_current`, `network_total`

### Affected Queries
1. **CPU Usage** (lines 127-144):
   - Total CPU query had `container!=""` filter
   - Per-pod CPU query had `container!=""` filter

2. **Memory Usage** (lines 175-192):
   - Total memory query had `container!=""` filter
   - Per-pod memory query had `container!=""` filter

3. **Historical CPU** (lines 301-308):
   - Historical CPU query had `container!=""` filter

## Solution
Removed the `container!=""` filter from all CPU and memory queries in `prometheus_client.py`, matching the working Grafana queries.

### Changes Made

#### 1. CPU Usage Queries (lines 127-144)
**Before:**
```python
total_query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*", 
    container!=""
}}[1m])) * 1000
'''

per_pod_query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*", 
    container!=""
}}[1m])) * 1000 / 
count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
'''
```

**After:**
```python
total_query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*"
}}[1m])) * 1000
'''

per_pod_query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*"
}}[1m])) * 1000 / 
count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
'''
```

#### 2. Memory Usage Queries (lines 175-192)
**Before:**
```python
total_query = f'''
sum(container_memory_working_set_bytes{{
    namespace="{namespace}", 
    pod=~"{app_label}.*", 
    container!=""
}})
'''

per_pod_query = f'''
sum(container_memory_working_set_bytes{{
    namespace="{namespace}", 
    pod=~"{app_label}.*", 
    container!=""
}}) / 
count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
'''
```

**After:**
```python
total_query = f'''
sum(container_memory_working_set_bytes{{
    namespace="{namespace}", 
    pod=~"{app_label}.*"
}})
'''

per_pod_query = f'''
sum(container_memory_working_set_bytes{{
    namespace="{namespace}", 
    pod=~"{app_label}.*"
}}) / 
count(kube_pod_info{{namespace="{namespace}", pod=~"{app_label}.*"}})
'''
```

#### 3. Historical CPU Query (lines 301-308)
**Before:**
```python
query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*", 
    container!=""
}}[1m])) * 1000
'''
```

**After:**
```python
query = f'''
sum(rate(container_cpu_usage_seconds_total{{
    namespace="{namespace}", 
    pod=~"{app_label}.*"
}}[1m])) * 1000
'''
```

## Testing
After applying the fix, you need to:

### 1. Stop the Current AI Scaler
Press `Ctrl+C` in the terminal where AI Scaler V3 is running.

### 2. Reset the State (Clear Old Data)
Since the AI Scaler was collecting incorrect metrics (all 0.0%), we need to clear the log file:

```bash
cd ai-scaler-v3
./reset_v3.sh
```

This will:
- Clear the `ai_scaler_v3.log` file that contains decisions based on incorrect metrics
- Ensure the AI Scaler starts fresh with correct data

### 3. Restart AI Scaler V3
```bash
python3 ai_scaler_v3.py
```

### 4. Verify Metrics
You should now see real metrics instead of 0.0%:
```
CPU Usage: 2.8 millicores, Memory Usage: 279.0 MB, Network I/O: 0.00 Mbps
```

(Note: Network will show 0.00 Mbps when there's no traffic. Run JMeter load test to see network metrics increase.)

The AI Scaler will now make intelligent scaling decisions based on actual Prometheus metrics.

## Why This Happened
In K3s/Colima environments, cAdvisor metrics have the following labels:
- ✅ `pod` - Pod name
- ✅ `namespace` - Kubernetes namespace
- ❌ `container` - **NOT AVAILABLE** in K3s/Colima

Standard Kubernetes clusters typically have the `container` label, but K3s (used by Colima) doesn't expose it. The queries work fine without this filter since we're already filtering by pod name pattern.

## Related Issues
This is the same root cause as the Grafana dashboard metrics issue documented in `GRAFANA_METRICS_FIX.md`. Both required removing the `container!=""` filter to work with K3s/Colima.

## Files Modified
- `ai-scaler-v3/prometheus_client.py` - Removed `container!=""` filter from CPU and memory queries

## Date
December 2, 2025