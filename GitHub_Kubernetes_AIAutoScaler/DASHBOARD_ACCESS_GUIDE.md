# Dashboard Access Guide

This guide provides instructions for accessing all monitoring dashboards in the AI Scaler V3 system.

## Quick Access Summary

| Dashboard | URL | Credentials | Purpose |
|-----------|-----|-------------|---------|
| **Kubernetes Dashboard** | http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/ | Token-based | View pods, deployments, resources |
| **Grafana** | http://localhost:30300 | admin / admin123 | View metrics and charts |
| **Prometheus** | http://localhost:30090 | None | Query raw metrics |
| **Tomcat Application** | http://localhost:8080 | None | Test application |

---

## 1. Kubernetes Dashboard

### Purpose
Visual interface to view and manage Kubernetes resources including:
- Pods and their status
- Deployments and ReplicaSets
- Services and Ingresses
- Resource usage (CPU, Memory)
- Logs and events
- ConfigMaps and Secrets

### Access Method

#### Option 1: Using the Helper Script (Recommended)
```bash
./scripts/open-k8s-dashboard.sh
```

This script will:
1. Generate a fresh access token
2. Display the dashboard URL
3. Show the token for authentication
4. Start kubectl proxy automatically

#### Option 2: Manual Access
```bash
# Step 1: Start kubectl proxy
kubectl proxy

# Step 2: Get the access token
kubectl -n kubernetes-dashboard create token admin-user

# Step 3: Open the URL in your browser
# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

# Step 4: Select "Token" and paste the token from Step 2
```

### Login Steps
1. Open the dashboard URL in your browser
2. Select **"Token"** authentication method
3. Paste the token provided by the script
4. Click **"Sign In"**

### What to View
- **Workloads > Deployments**: See `tomcat-sample-app` deployment
- **Workloads > Pods**: View individual Tomcat pods and their status
- **Workloads > Replica Sets**: See how pods are managed
- **Service > Services**: View `tomcat-sample-service` LoadBalancer
- **Config and Storage > Config Maps**: See Prometheus and Grafana configs
- **Cluster > Nodes**: View node resources and capacity

### Troubleshooting
- **Token expired**: Run the script again to generate a new token
- **Proxy not running**: Make sure `kubectl proxy` is running in a terminal
- **Can't access**: Verify Kubernetes cluster is running with `kubectl get nodes`

---

## 2. Grafana Dashboard

### Purpose
Real-time visualization of application metrics:
- CPU usage (total and per-pod)
- Memory usage (total and per-pod)
- Network I/O (node-level)
- Pod count and scaling events
- Service health status

### Access
```bash
# URL
http://localhost:30300

# Credentials
Username: admin
Password: admin123
```

### Navigation
1. Open http://localhost:30300 in your browser
2. Login with admin/admin123
3. Click **"Dashboards"** in the left menu
4. Select **"AI Autoscaler - Tomcat Monitoring"**

### Dashboard Panels
- **Tomcat Pod Count**: Number of running pods over time
- **CPU Usage**: Total and per-pod CPU consumption
- **Memory Usage**: Total and per-pod memory consumption
- **Network I/O (Node Level)**: Network traffic in/out
- **Avg CPU per Pod**: Current average CPU gauge
- **Current Pod Count**: Current number of pods gauge
- **Avg Memory per Pod**: Current average memory gauge
- **Service Health**: Running/Down status

### Features
- **Time Range**: Adjust in top-right corner (default: last 15 minutes)
- **Refresh Rate**: Auto-refresh every 5 seconds
- **Zoom**: Click and drag on any graph to zoom in
- **Legend**: Click legend items to show/hide series

### Troubleshooting
- **No data showing**: Wait a few minutes for metrics to accumulate
- **Login fails**: Use admin/admin123 (case-sensitive)
- **Dashboard not found**: Run `./scripts/update-grafana-dashboard.sh`

---

## 3. Prometheus

### Purpose
Raw metrics storage and querying:
- Query metrics using PromQL
- View all available metrics
- Check scrape targets health
- Debug metric collection issues

### Access
```bash
# URL
http://localhost:30090

# No authentication required
```

### Useful Queries
```promql
# CPU usage for Tomcat pods
sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"tomcat-sample-app.*"}[1m])) * 1000

# Memory usage for Tomcat pods
sum(container_memory_working_set_bytes{namespace="default", pod=~"tomcat-sample-app.*"})

# Pod count
count(kube_pod_info{namespace="default", pod=~"tomcat-sample-app.*"})

# Network traffic
sum(rate(container_network_receive_bytes_total{job="kubernetes-cadvisor"}[1m]))
```

### Navigation
1. Open http://localhost:30090
2. Click **"Graph"** tab
3. Enter a PromQL query
4. Click **"Execute"**
5. View results in table or graph format

### Check Targets
1. Click **"Status"** > **"Targets"**
2. Verify all targets are **"UP"**
3. Check scrape duration and last scrape time

---

## 4. Tomcat Application

### Purpose
Test application to generate load and verify autoscaling:
- Homepage and sample pages
- Examples and documentation
- Manager and host-manager apps

### Access
```bash
# URL
http://localhost:8080

# No authentication required for main pages
```

### Available URLs
- **Homepage**: http://localhost:8080/
- **Examples**: http://localhost:8080/examples/
- **Docs**: http://localhost:8080/docs/
- **Manager**: http://localhost:8080/manager/ (requires auth)

### Testing Load
Use JMeter to generate load:
```bash
# From V2 directory
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler/
jmeter -n -t LocalHost_Tomcat.jmx -l results.jtl
```

---

## Complete Monitoring Workflow

### 1. Start Everything
```bash
# Start AI Scaler V3
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/
python3 ai-scaler-v3/ai_scaler_v3.py

# In another terminal, open Kubernetes Dashboard
./scripts/open-k8s-dashboard.sh
```

### 2. Open All Dashboards
- **Kubernetes Dashboard**: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
- **Grafana**: http://localhost:30300 (admin/admin123)
- **Prometheus**: http://localhost:30090
- **Tomcat**: http://localhost:8080

### 3. Monitor Autoscaling
1. **In Kubernetes Dashboard**:
   - Go to Workloads > Pods
   - Watch pod count change as load increases/decreases
   - View pod resource usage

2. **In Grafana**:
   - Watch real-time CPU and memory graphs
   - See pod count changes
   - Monitor network traffic

3. **In AI Scaler Terminal**:
   - Watch scaling decisions
   - See metric collection
   - View ML predictions

### 4. Generate Load
```bash
# Start JMeter load test
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler/
jmeter -n -t LocalHost_Tomcat.jmx -l results.jtl
```

### 5. Observe Scaling
- **Kubernetes Dashboard**: See new pods being created
- **Grafana**: Watch metrics spike and pod count increase
- **AI Scaler logs**: See scaling decisions being made
- **Prometheus**: Query metrics to verify data collection

---

## Troubleshooting

### Kubernetes Dashboard Issues
```bash
# Check if dashboard is running
kubectl get pods -n kubernetes-dashboard

# Restart dashboard if needed
kubectl rollout restart deployment kubernetes-dashboard -n kubernetes-dashboard

# Generate new token
kubectl -n kubernetes-dashboard create token admin-user
```

### Grafana Issues
```bash
# Check if Grafana is running
kubectl get pods -n monitoring -l app=grafana

# Restart Grafana
kubectl rollout restart deployment grafana -n monitoring

# Update dashboard
./scripts/update-grafana-dashboard.sh
```

### Prometheus Issues
```bash
# Check if Prometheus is running
kubectl get pods -n monitoring -l app=prometheus

# Check targets
curl http://localhost:30090/api/v1/targets

# Restart Prometheus
kubectl rollout restart deployment prometheus -n monitoring
```

### General Issues
```bash
# Check all pods
kubectl get pods --all-namespaces

# Check services
kubectl get svc --all-namespaces

# Check cluster status
kubectl cluster-info

# View pod logs
kubectl logs <pod-name> -n <namespace>
```

---

## Security Notes

### Kubernetes Dashboard
- Token-based authentication
- Admin-level access
- Token expires after some time
- Generate new token when needed

### Grafana
- Default credentials: admin/admin123
- Change password in production
- Access via NodePort (30300)

### Prometheus
- No authentication by default
- Internal cluster access only
- Exposed via NodePort (30090)

### Tomcat
- Public access on port 8080
- Manager apps require authentication
- Examples and docs are public

---

## Quick Reference Commands

```bash
# Start Kubernetes Dashboard
./scripts/open-k8s-dashboard.sh

# Update Grafana Dashboard
./scripts/update-grafana-dashboard.sh

# Start AI Scaler V3
python3 ai-scaler-v3/ai_scaler_v3.py

# Check all pods
kubectl get pods --all-namespaces

# Check services
kubectl get svc --all-namespaces

# View AI Scaler logs
tail -f ai-scaler-v3/logs/ai_scaler.log

# Generate load
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler/
jmeter -n -t LocalHost_Tomcat.jmx -l results.jtl
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs: `kubectl logs <pod-name> -n <namespace>`
3. Verify cluster status: `kubectl get pods --all-namespaces`
4. Check documentation: `README.md`, `START_V3_COMPLETE.md`