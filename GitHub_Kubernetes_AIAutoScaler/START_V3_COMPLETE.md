# 🚀 Complete Startup Guide for AI Scaler V3

## Overview
This guide will help you start everything from scratch after a Mac restart:
1. Start Colima with Kubernetes
2. Deploy Tomcat application
3. Deploy Prometheus monitoring stack
4. Deploy Grafana dashboard
5. Start AI Scaler V3
6. Monitor autoscaling in action

---

## Prerequisites Check

```bash
# Verify installations
colima version
kubectl version --client
python3 --version
```

---

## PART 1: Start Kubernetes Cluster

### Step 1.1: Start Colima with Kubernetes
```bash
colima start --cpu 6 --memory 16 --kubernetes
```

**Expected output:**
```
INFO[0000] starting colima
INFO[0000] runtime: docker+k3s
INFO[0XXX] done
```

**Wait time:** 2-3 minutes

---

### Step 1.2: Verify Kubernetes is Ready
```bash
kubectl get nodes
```

**Expected output:**
```
NAME     STATUS   ROLES                  AGE   VERSION
colima   Ready    control-plane,master   XXs   v1.31.2+k3s1
```

---

## PART 2: Deploy Tomcat Application

### Step 2.1: Navigate to Project Directory
```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler
```

---

### Step 2.2: Deploy Tomcat
```bash
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml
```

**Expected output:**
```
deployment.apps/tomcat-sample-app created
service/tomcat-sample-service created
```

---

### Step 2.3: Wait for Tomcat to be Ready
```bash
kubectl get pods -w
```

**Wait until you see:**
```
NAME                                 READY   STATUS    RESTARTS   AGE
tomcat-sample-app-XXXXXXXXXX-XXXXX   1/1     Running   0          XXs
```

**Press Ctrl+C to stop watching**

---

### Step 2.4: Verify Tomcat is Accessible
```bash
# Test home page
curl -s -o /dev/null -w "HomePage: %{http_code}\n" http://localhost:8080/

# Test examples
curl -s -o /dev/null -w "Examples: %{http_code}\n" http://localhost:8080/examples/

# Test docs
curl -s -o /dev/null -w "Docs: %{http_code}\n" http://localhost:8080/docs/
```

**Expected output:**
```
HomePage: 200
Examples: 200
Docs: 200
```

✅ **Tomcat is ready!**

---

## PART 3: Deploy Prometheus Monitoring Stack

### Step 3.1: Create Monitoring Namespace
```bash
kubectl create namespace monitoring
```

---

### Step 3.2: Deploy Prometheus Configuration
```bash
kubectl apply -f kubernetes-manifests/prometheus-config.yaml
```

**Expected output:**
```
configmap/prometheus-config created
```

---

### Step 3.3: Deploy Prometheus
```bash
kubectl apply -f kubernetes-manifests/prometheus-deployment.yaml
```

**Expected output:**
```
serviceaccount/prometheus created
clusterrole.rbac.authorization.k8s.io/prometheus created
clusterrolebinding.rbac.authorization.k8s.io/prometheus created
persistentvolumeclaim/prometheus-storage created
deployment.apps/prometheus created
service/prometheus created
```

---

### Step 3.4: Deploy kube-state-metrics
```bash
kubectl apply -f kubernetes-manifests/kube-state-metrics.yaml
```

**Expected output:**
```
serviceaccount/kube-state-metrics created
clusterrole.rbac.authorization.k8s.io/kube-state-metrics created
clusterrolebinding.rbac.authorization.k8s.io/kube-state-metrics created
deployment.apps/kube-state-metrics created
service/kube-state-metrics created
```

---

### Step 3.5: Deploy Grafana
```bash
kubectl apply -f kubernetes-manifests/grafana-deployment.yaml
```

**Expected output:**
```
deployment.apps/grafana created
service/grafana created
```

---

### Step 3.6: Wait for Monitoring Stack to be Ready
```bash
kubectl get pods -n monitoring -w
```

**Wait until all pods show Running:**
```
NAME                                  READY   STATUS    RESTARTS   AGE
prometheus-XXXXXXXXXX-XXXXX           1/1     Running   0          XXs
kube-state-metrics-XXXXXXXXXX-XXXXX   1/1     Running   0          XXs
grafana-XXXXXXXXXX-XXXXX              1/1     Running   0          XXs
```

**Press Ctrl+C to stop watching**

**Wait time:** 1-2 minutes

---

### Step 3.7: Verify Prometheus is Accessible
```bash
curl -s http://localhost:30090/-/healthy
```

**Expected output:**
```
Prometheus is Healthy.
```

✅ **Prometheus is ready!**

---

## PART 4: Access Grafana Dashboard

### Step 4.1: Get Grafana URL
```bash
echo "Grafana URL: http://localhost:30300"
```

---

### Step 4.2: Open Grafana in Browser
```bash
# Open in default browser (macOS)
open http://localhost:30300
```

**Or manually open:** `http://localhost:30300`

---

### Step 4.3: Login to Grafana
```
Username: admin
Password: admin123
```

**Note:** You may be prompted to change the password (you can skip this)

---

### Step 4.4: Import Autoscaler Dashboard

1. Click **"+"** (Create) in left sidebar
2. Click **"Import"**
3. Click **"Upload JSON file"**
4. Select: `/Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/grafana/dashboards/autoscaler-dashboard.json`
5. Click **"Import"**

✅ **Grafana dashboard is ready!**

---

## PART 5: Access Kubernetes Dashboard

### Step 5.1: Open Kubernetes Dashboard
```bash
# Run the helper script
./scripts/open-k8s-dashboard.sh
```

**The script will:**
1. Generate a fresh access token
2. Display the dashboard URL
3. Show the token for authentication
4. Start kubectl proxy automatically

---

### Step 5.2: Login to Kubernetes Dashboard

1. **Copy the token** displayed in the terminal
2. **Open the URL** in your browser:
   ```
   http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
   ```
3. **Select "Token"** authentication method
4. **Paste the token** you copied
5. **Click "Sign In"**

---

### Step 5.3: Explore Kubernetes Dashboard

**What you can see:**
- **Workloads > Pods**: View all Tomcat pods and their status
- **Workloads > Deployments**: See `tomcat-sample-app` deployment
- **Workloads > Replica Sets**: Monitor how pods are managed
- **Service > Services**: View `tomcat-sample-service` LoadBalancer
- **Config and Storage**: See ConfigMaps and PersistentVolumes
- **Cluster > Nodes**: View node resources and capacity

**Useful views:**
- Click on any pod to see logs, events, and resource usage
- Monitor CPU and memory usage in real-time
- Watch pods being created/deleted during autoscaling

---

### Step 5.4: Keep kubectl Proxy Running

**Important:** The kubectl proxy must stay running for dashboard access.
- The script terminal will show: `Starting to serve on 127.0.0.1:8001`
- Keep this terminal open
- Press **Ctrl+C** to stop the proxy when done

✅ **Kubernetes Dashboard is ready!**

**Note:** If the token expires, simply run `./scripts/open-k8s-dashboard.sh` again to generate a new one.

---

## PART 6: Install Python Dependencies for V3</search>
</search_and_replace>

### Step 5.1: Navigate to AI Scaler V3 Directory
```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3
```

---

### Step 5.2: Install Python Requirements
```bash
pip3 install -r requirements.txt
```

**Expected packages:**
- kubernetes
- prometheus-api-client
- pyyaml
- numpy
- pandas

---

### Step 5.3: Verify Installation
```bash
pip3 list | grep -E "kubernetes|prometheus|pyyaml|numpy|pandas"
```

✅ **Python dependencies installed!**

---

## PART 6: Start AI Scaler V3

### Step 6.1: Make Start Script Executable
```bash
chmod +x start_v3.sh
```

---

### Step 6.2: Start AI Scaler V3
```bash
./start_v3.sh
```

**Or start directly with Python:**
```bash
python3 ai_scaler_v3.py
```

---

### Step 6.3: Expected Output
```
🚀 AI Scaler V3 Starting...
📊 Configuration loaded from config.yaml
🔗 Connecting to Prometheus at http://localhost:30090
✅ Prometheus connection successful
🎯 Target deployment: tomcat-sample-app (namespace: default)
📈 Scaling range: 1-10 replicas
⚖️  Metric weights: CPU=40%, Memory=30%, Network=20%, Cost=10%
⏱️  Check interval: 30 seconds

============================================================
Iteration #1 - 2024-12-02 15:10:00
============================================================
📊 Current Metrics:
   CPU Usage: 15.2%
   Memory Usage: 45.3%
   Network I/O: 1.2 MB/s
   Current Replicas: 1

🧮 Feature Engineering:
   Extracted 37 features
   CPU Trend: stable
   Memory Trend: stable
   Load Pattern: low

⚖️  Weighted Scoring:
   CPU Score: 15.2 (weight: 0.40)
   Memory Score: 45.3 (weight: 0.30)
   Network Score: 12.0 (weight: 0.20)
   Cost Score: 20.0 (weight: 0.10)
   Total Score: 24.5
   Confidence: 0.85

🎯 Decision:
   Recommended Replicas: 1
   Current Replicas: 1
   Action: No scaling needed

⏳ Next check in 30 seconds...
```

✅ **AI Scaler V3 is running!**

---

## PART 7: Monitor Autoscaling

### Option 1: Watch AI Scaler V3 Logs (Current Terminal)
The AI Scaler V3 terminal will show:
- Current metrics every 30 seconds
- Scaling decisions
- Confidence scores
- Actions taken

---

### Option 2: Watch Pods Scale (New Terminal)
```bash
# Open new terminal
kubectl get pods -w
```

You'll see pods being created/deleted as V3 scales

---

### Option 3: Monitor in Grafana Dashboard
1. Open Grafana: `http://localhost:30300`
2. Go to **"Autoscaler Dashboard"**
3. Watch real-time metrics:
   - Pod count
   - CPU usage
   - Memory usage
   - Network I/O
   - Scaling decisions

---

### Option 4: Check Metrics with kubectl
```bash
# In new terminal
watch kubectl top pods
```

Shows real-time CPU/Memory usage

---

## PART 8: Generate Load with JMeter

### Step 8.1: Open New Terminal
**Don't close the AI Scaler V3 terminal!**

---

### Step 8.2: Navigate to JMeter
```bash
cd /Users/nabanish/Desktop/apache-jmeter-5.6.3/bin
```

---

### Step 8.3: Run Load Test
```bash
./jmeter -n -t /Users/nabanish/Desktop/LocalHost_Tomcat.jmx -l results.jtl
```

**Expected behavior:**
1. JMeter generates load (5500+ TPS)
2. CPU/Memory increases on Tomcat pods
3. AI Scaler V3 detects high load
4. V3 scales up: 1 → 2 → 3 → 4 → 5 pods
5. Load distributes across pods
6. CPU stabilizes around 70% per pod

---

### Step 8.4: Watch Autoscaling in Action

**In AI Scaler V3 terminal, you'll see:**
```
============================================================
Iteration #15 - 2024-12-02 15:17:30
============================================================
📊 Current Metrics:
   CPU Usage: 85.7%  ⬆️ (was 15.2%)
   Memory Usage: 62.1%
   Network I/O: 45.3 MB/s
   Current Replicas: 1

⚖️  Weighted Scoring:
   Total Score: 78.5  ⬆️ (was 24.5)
   Confidence: 0.92

🎯 Decision:
   Recommended Replicas: 3  ⬆️
   Current Replicas: 1
   Action: SCALING UP from 1 to 3 replicas

⚡ Executing scaling action...
✅ Successfully scaled to 3 replicas
```

**In Grafana dashboard, you'll see:**
- Pod count graph increasing
- CPU per pod decreasing
- Total throughput maintained

---

## PART 9: Stop Everything (When Done)

### Step 9.1: Stop JMeter
Press **Ctrl+C** in JMeter terminal

---

### Step 9.2: Stop AI Scaler V3
Press **Ctrl+C** in AI Scaler V3 terminal

**Or use stop script:**
```bash
cd /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3
./stop_v3.sh
```

---

### Step 9.3: (Optional) Clean Up Kubernetes Resources
```bash
# Delete Tomcat
kubectl delete -f /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/kubernetes-manifests/tomcat-with-sample-app.yaml

# Delete monitoring stack
kubectl delete namespace monitoring
```

---

### Step 9.4: (Optional) Stop Colima
```bash
colima stop
```

---

## Quick Reference Commands

### Check Status
```bash
# Colima status
colima status

# Kubernetes nodes
kubectl get nodes

# All pods
kubectl get pods --all-namespaces

# Tomcat pods
kubectl get pods -l app=tomcat-sample

# Monitoring pods
kubectl get pods -n monitoring

# Pod CPU/Memory
kubectl top pods
```

---

### Access URLs
```
Kubernetes Dashboard: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
                      (Run: ./scripts/open-k8s-dashboard.sh for token)
Tomcat:              http://localhost:8080
Prometheus:          http://localhost:30090
Grafana:             http://localhost:30300 (admin/admin123)
```

---

### Logs
```bash
# AI Scaler V3 log file
tail -f /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3/ai_scaler_v3.log

# Tomcat pod logs
kubectl logs -f <tomcat-pod-name>

# Prometheus logs
kubectl logs -f -n monitoring <prometheus-pod-name>
```

---

## Troubleshooting

### Issue: Colima won't start
```bash
colima delete
colima start --cpu 6 --memory 16 --kubernetes
```

---

### Issue: Prometheus not accessible
```bash
# Check if Prometheus pod is running
kubectl get pods -n monitoring

# Check Prometheus logs
kubectl logs -n monitoring <prometheus-pod-name>

# Restart Prometheus
kubectl rollout restart deployment/prometheus -n monitoring
```

---

### Issue: AI Scaler V3 can't connect to Prometheus
```bash
# Verify Prometheus is accessible
curl http://localhost:30090/-/healthy

# Check config.yaml has correct URL
cat /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/ai-scaler-v3/config.yaml | grep url
```

---

### Issue: Grafana dashboard shows "No Data"
```bash
# Wait 2-3 minutes for metrics to populate
# Check if Prometheus is scraping metrics
curl http://localhost:30090/api/v1/targets

# Verify kube-state-metrics is running
kubectl get pods -n monitoring | grep kube-state-metrics
```

---

## Summary

**Complete startup sequence:**
1. ✅ Start Colima (2-3 min)
2. ✅ Deploy Tomcat (1 min)
3. ✅ Deploy Prometheus stack (2 min)
4. ✅ Access Grafana dashboard
5. ✅ Access Kubernetes Dashboard
6. ✅ Install Python deps (1 min)
7. ✅ Start AI Scaler V3
8. ✅ Run JMeter load test
9. ✅ Watch autoscaling in action!

**Total setup time:** ~10 minutes

**You're ready to see AI Scaler V3 in action!** 🚀

---

**Made by Nabanish with Bob's assistance**