# 🚀 Quick Start Guide

Get the AI Autoscaler running with complete monitoring in 5 minutes!

## Prerequisites Check

```bash
# Check if tools are installed
which colima kubectl python3

# If missing, install:
brew install colima kubectl
```

## Complete Setup (After Mac Restart)

Follow these steps in order. You'll need **4 terminal windows** open simultaneously.

---

## Terminal 1: Start Kubernetes & Deploy Everything

```bash
# 1. Start Colima with Kubernetes (6 CPU, 16GB RAM recommended)
colima start --kubernetes --cpu 6 --memory 16 --disk 50

# Verify cluster is running
kubectl get nodes

# 2. Navigate to project directory
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler

# 3. Install Kubernetes Dashboard (for visual monitoring)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Wait for dashboard namespace to be created
sleep 10

# Apply dashboard admin user
kubectl apply -f kubernetes-manifests/dashboard-admin.yaml

# 4. Deploy Tomcat application
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml

# Wait for pods to be ready (up to 120 seconds)
kubectl wait --for=condition=ready pod -l app=tomcat-sample --timeout=120s

# Verify deployment
kubectl get pods

# 5. Port forward for JMeter/load testing (use port 9091)
kubectl port-forward svc/tomcat-sample-service 9091:8080
```

**✅ Keep this terminal running!** JMeter will connect to `http://localhost:9091/sample/`

---

## Terminal 2: Start AI Autoscaler

```bash
# Navigate to project
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Option A: Reset and start fresh (recommended)
./scripts/reset_and_start_v2.sh
python3 ai_scaler_v2.py

# Option B: Start without reset
python3 ai_scaler_v2.py
```

**✅ Keep this terminal running!** You'll see autoscaling decisions here.

---

## Terminal 3: Watch Pods in Real-Time

```bash
# Watch pods update every 2 seconds
watch kubectl get pods

# Alternative: Check resource usage
kubectl top pods
```

**✅ Keep this terminal running!** You'll see pods scale up/down here.

---

## Terminal 4: Kubernetes Dashboard (Visual Monitoring)

```bash
# Start kubectl proxy
kubectl proxy --port=8002

# If port 8002 is in use, kill existing process first:
# pkill -f "kubectl proxy"
# Then try again: kubectl proxy --port=8002
```

**Then open in browser:**
- Dashboard URL: `http://localhost:8002/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`
- Click "Skip" on the login page to view without token

**✅ Keep this terminal running!** Dashboard will show visual pod metrics.

---

## Generate Load for Testing

### Option 1: Using JMeter (Recommended)

**JMeter Configuration:**
- **Target Server:** `localhost`
- **Port:** `9091`
- **Path:** `/sample/`
- **Threads:** 100-200
- **Ramp-up:** 60 seconds

Use your existing `KubeProxy_LocalHost_Tomcat.jmx` file.

### Option 2: Using curl

```bash
# In a new terminal (Terminal 5)
for i in {1..1000}; do 
  curl http://localhost:9091/sample/ &
done
```

---

## Expected Behavior

### Initial State (No Load)
```
📊 Current Metrics:
   CPU per pod: 2-10m
   Current pods: 1
   Status: Stable
```

### Under Load (JMeter Running)
```
📊 Current Metrics:
   CPU per pod: 700-800m
   
⚡ Scaling from 1 to 2 replicas...
✅ Successfully scaled to 2 replicas
```

### After Scale-Up
```
📊 Current Metrics:
   CPU per pod: 350-400m (distributed across pods)
   Current pods: 2
   Status: Stable
```

### Scale-Down (After Load Stops)
```
📊 Current Metrics:
   CPU per pod: 50-100m
   
⚡ Scaling from 2 to 1 replicas...
✅ Successfully scaled to 1 replica
```

---

## What You'll See in Each Terminal

### Terminal 1 (Port Forward)
```
Forwarding from 127.0.0.1:9091 -> 8080
Forwarding from [::1]:9091 -> 8080
Handling connection for 9091
Handling connection for 9091
...
```

### Terminal 2 (AI Autoscaler)
```
🤖 AI-Driven Kubernetes Autoscaler V2
====================================
Target: tomcat-sample-app
Namespace: default

📊 Iteration 1
   CPU per pod: 5m
   Current pods: 1
   Status: Stable

📊 Iteration 2
   CPU per pod: 750m
   ⚡ Scaling from 1 to 2 replicas...
   ✅ Successfully scaled to 2 replicas
```

### Terminal 3 (Watch Pods)
```
NAME                                 READY   STATUS    RESTARTS   AGE
tomcat-sample-app-6ccdc4f4b4-lx2bl   1/1     Running   0          2m
tomcat-sample-app-6ccdc4f4b4-xyz12   1/1     Running   0          15s
```

### Terminal 4 (Dashboard)
```
Starting to serve on 127.0.0.1:8002
```

---

## Monitoring Commands

```bash
# Check pod status
kubectl get pods

# Check resource usage
kubectl top pods
kubectl top nodes

# Check deployment
kubectl get deployment tomcat-sample-app

# View autoscaler logs (if running in background)
tail -f autoscaler.log
```

---

## Stopping Everything

```bash
# Terminal 2: Stop autoscaler
Ctrl+C

# Terminal 1: Stop port forward
Ctrl+C

# Terminal 3: Stop watch
Ctrl+C

# Terminal 4: Stop kubectl proxy
Ctrl+C

# Terminal 5: Stop load generation (if using curl)
Ctrl+C

# Optional: Clean up resources
./scripts/stop_and_cleanup.sh

# Optional: Stop Colima
colima stop
```

---

## Troubleshooting

### Issue: "No module named 'kubernetes'"
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: "Unable to connect to the server"
```bash
# Check if Colima is running
colima status

# Start if stopped
colima start --kubernetes --cpu 6 --memory 16 --disk 50
```

### Issue: "Port 9091 already in use"
```bash
# Find and kill the process
lsof -ti:9091 | xargs kill -9

# Or use a different port
kubectl port-forward svc/tomcat-sample-service 9092:8080
# Then update JMeter to use port 9092
```

### Issue: "Port 8002 already in use" (kubectl proxy)
```bash
# Kill existing kubectl proxy
pkill -f "kubectl proxy"

# Or use a different port
kubectl proxy --port=8003
# Then update browser URL to use port 8003
```

### Issue: "kubernetes-dashboard namespace not found"
```bash
# Install Kubernetes Dashboard first
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Wait 10 seconds, then apply admin user
sleep 10
kubectl apply -f kubernetes-manifests/dashboard-admin.yaml
```

### Issue: Autoscaler not scaling
```bash
# Check CPU usage
kubectl top pods

# Verify metrics-server is running
kubectl get pods -n kube-system | grep metrics-server

# Generate more load (increase JMeter threads to 200-300)
```

### Issue: Pods stuck in "Pending" state
```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name>

# May need to increase Colima resources
colima stop
colima start --kubernetes --cpu 6 --memory 16 --disk 50
```

---

## Configuration

### Adjust Colima Resources
```bash
# Stop Colima
colima stop

# Start with different resources
colima start --kubernetes --cpu 8 --memory 20 --disk 100
```

### Adjust Autoscaler Thresholds

Edit `ai_scaler_v2.py`:
```python
# Scaling limits
self.min_replicas = 1
self.max_replicas = 6

# CPU thresholds (millicores)
self.target_cpu_per_pod = 500
self.scale_up_threshold = 700
self.scale_down_threshold = 200
```

### Adjust Pod Resources

Edit `kubernetes-manifests/tomcat-with-sample-app.yaml`:
```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1000m"
    memory: "1Gi"
```

---

## Quick Commands Reference

### Start Everything (After Mac Restart)
```bash
# Terminal 1
colima start --kubernetes --cpu 6 --memory 16 --disk 50
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
sleep 10
kubectl apply -f kubernetes-manifests/dashboard-admin.yaml
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml
kubectl wait --for=condition=ready pod -l app=tomcat-sample --timeout=120s
kubectl port-forward svc/tomcat-sample-service 9091:8080

# Terminal 2
cd /Users/nabanish/Desktop/Kubernetes_AIAutoScaler
source venv/bin/activate
python3 ai_scaler_v2.py

# Terminal 3
watch kubectl get pods

# Terminal 4
kubectl proxy --port=8002
# Open: http://localhost:8002/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### Monitor
```bash
watch kubectl get pods
kubectl top pods
kubectl top nodes
```

### Generate Load
```bash
# JMeter: localhost:9091, path: /sample/
# Or curl:
for i in {1..1000}; do curl http://localhost:9091/sample/ & done
```

### Stop Everything
```bash
# Ctrl+C in all terminals
./scripts/stop_and_cleanup.sh
colima stop
```

---

## Success Indicators

✅ **Colima running:** `colima status` shows "Running"  
✅ **Pods ready:** `kubectl get pods` shows "Running" status  
✅ **Port forward active:** Terminal 1 shows "Handling connection" messages  
✅ **Autoscaler active:** Terminal 2 shows iteration updates  
✅ **Dashboard accessible:** Browser shows Kubernetes Dashboard  
✅ **Scaling works:** Pod count changes with load in Terminal 3  

---

## Next Steps

1. **Read Documentation**: Check `docs/` folder for detailed guides
2. **Test Scenarios**: Follow `docs/TESTING_GUIDE.md`
3. **Customize**: Edit `ai_scaler_v2.py` configuration
4. **Monitor ML**: Watch model training at iteration 20, 40, 60...
5. **Experiment**: Try different load patterns and observe scaling behavior

---

## Key Features

- **Machine Learning**: Random Forest model learns optimal scaling patterns
- **Intelligent Dampening**: Prevents rapid oscillations
- **Multi-metric**: Considers CPU, memory, time patterns, and trends
- **Real-time Monitoring**: Live updates in multiple terminals
- **Visual Dashboard**: Kubernetes Dashboard for graphical monitoring

---

**Need help?** Check the main [README.md](README.md) or open an issue!

**Made by Nabanish with the help of Bob**