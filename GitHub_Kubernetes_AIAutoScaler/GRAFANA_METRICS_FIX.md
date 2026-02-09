# Grafana Dashboard Metrics Fix

## Issue
After deploying AI Scaler V3, the Grafana dashboard showed "No data" for CPU Usage, Memory Usage, and Network I/O panels. Only "Tomcat Pod Count" and "Service Health" were displaying data.

## Root Cause Analysis

### 1. CPU and Memory Metrics Issue
**Problem:** Dashboard queries were filtering for `container!=""` label, but cAdvisor metrics in K3s/Colima don't include a `container` label.

**Investigation:**
```bash
# Check available metrics
curl -s 'http://localhost:30090/api/v1/query?query=container_cpu_usage_seconds_total' | python3 -m json.tool

# Found that metrics only have: pod, namespace, id, cpu, instance, job
# No 'container' label exists
```

**Solution:** Removed the `container!=""` filter from CPU and memory queries.

### 2. Network Metrics Issue
**Problem:** Pod-level network metrics are not available in K3s/Colima with cAdvisor.

**Investigation:**
```bash
# Check network metrics
curl -s 'http://localhost:30090/api/v1/query?query=container_network_receive_bytes_total'

# Found that network metrics only have: id, interface, instance, job
# No 'pod' or 'namespace' labels - metrics are node-level only
```

**Solution:** Changed network queries to show node-level metrics instead of pod-specific metrics.

## Changes Made

### Dashboard Query Updates

#### Before (CPU Usage):
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"tomcat-sample-app.*", container!=""}[1m])) * 1000
```

#### After (CPU Usage):
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"tomcat-sample-app.*"}[1m])) * 1000
```

#### Before (Memory Usage):
```promql
sum(container_memory_working_set_bytes{namespace="default", pod=~"tomcat-sample-app.*", container!=""})
```

#### After (Memory Usage):
```promql
sum(container_memory_working_set_bytes{namespace="default", pod=~"tomcat-sample-app.*"})
```

#### Before (Network I/O):
```promql
sum(rate(container_network_receive_bytes_total{namespace="default", pod=~"tomcat-sample-app.*"}[1m]))
```

#### After (Network I/O):
```promql
sum(rate(container_network_receive_bytes_total{job="kubernetes-cadvisor"}[1m]))
```

## Technical Details

### Why Container Label Doesn't Exist
In K3s/Colima environments, cAdvisor collects metrics at the pod level, not the container level. The metrics structure is:
- `pod`: Pod name (e.g., `tomcat-sample-app-78c7bcbf87-l8q8r`)
- `namespace`: Kubernetes namespace (e.g., `default`)
- `id`: cgroup ID path
- `cpu`: CPU identifier
- `instance`: Node name
- `job`: Scrape job name

### Why Pod-Level Network Metrics Don't Exist
Network metrics in cAdvisor are collected at the network interface level, not per-pod:
- Metrics are aggregated at the node level
- Labels include: `interface` (e.g., `cni0`), `id`, `instance`, `job`
- No `pod` or `namespace` labels are available

This is a known limitation in Kubernetes networking with cAdvisor. Pod-level network metrics would require:
- Network plugins that expose per-pod metrics
- Service mesh (like Istio) with sidecar proxies
- Custom exporters that track per-pod network usage

## How to Apply the Fix

### Method 1: Using the Update Script
```bash
./scripts/update-grafana-dashboard.sh
```

### Method 2: Manual Update
1. Edit `grafana/dashboards/autoscaler-dashboard.json`
2. Remove `container!=""` filters from CPU and memory queries
3. Update network queries to use node-level metrics
4. Import the updated dashboard to Grafana via API or UI

## Verification

After applying the fix, verify in Grafana (http://localhost:30300):
1. **CPU Usage Panel**: Should show total CPU and per-pod CPU metrics
2. **Memory Usage Panel**: Should show total memory and per-pod memory metrics
3. **Network I/O Panel**: Should show node-level network in/out (labeled as "Node Level")
4. **Gauge Panels**: Should show current values for CPU, memory, and pod count

## Dashboard Versions
- **Version 1**: Original dashboard with incorrect queries
- **Version 2**: Fixed CPU and memory queries (removed container filter)
- **Version 3**: Fixed network queries (changed to node-level metrics)

## Notes

### Network Metrics Limitation
The "Network I/O (Node Level)" panel shows total network traffic for the entire node, not just Tomcat pods. This is a limitation of the current setup. To get pod-specific network metrics, you would need to:

1. **Deploy a service mesh** (e.g., Istio, Linkerd)
2. **Use network plugins** that expose per-pod metrics
3. **Deploy custom exporters** that track pod network usage
4. **Use eBPF-based solutions** for detailed network monitoring

For most use cases, node-level network metrics combined with pod-specific CPU and memory metrics provide sufficient visibility for autoscaling decisions.

## Related Files
- `grafana/dashboards/autoscaler-dashboard.json` - Updated dashboard definition
- `scripts/update-grafana-dashboard.sh` - Script to apply dashboard updates
- `kubernetes-manifests/prometheus-config.yaml` - Prometheus scrape configuration
- `kubernetes-manifests/grafana-deployment.yaml` - Grafana deployment

## References
- [Kubernetes Monitoring with Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#kubernetes_sd_config)
- [cAdvisor Metrics](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)