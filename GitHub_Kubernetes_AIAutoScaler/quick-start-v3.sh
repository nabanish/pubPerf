#!/bin/bash

# Quick Start Script for AI Scaler V3
# This script automates the complete setup process

set -e  # Exit on error

echo "🚀 AI Scaler V3 - Quick Start Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to wait for pods to be ready
wait_for_pods() {
    local namespace=$1
    local label=$2
    local timeout=300  # 5 minutes
    local elapsed=0
    
    print_info "Waiting for pods with label $label in namespace $namespace..."
    
    while [ $elapsed -lt $timeout ]; do
        if kubectl get pods -n $namespace -l $label 2>/dev/null | grep -q "Running"; then
            local ready=$(kubectl get pods -n $namespace -l $label -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null)
            if [[ "$ready" == *"true"* ]]; then
                print_success "Pods are ready!"
                return 0
            fi
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    print_error "Timeout waiting for pods to be ready"
    return 1
}

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
if ! command -v colima &> /dev/null; then
    print_error "Colima not found. Please install: brew install colima"
    exit 1
fi
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install: brew install kubectl"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found. Please install Python 3"
    exit 1
fi
print_success "All prerequisites found"
echo ""

# Step 2: Start Colima
echo "🐳 Step 2: Starting Colima with Kubernetes..."
if colima status &> /dev/null; then
    print_info "Colima is already running"
else
    print_info "Starting Colima (this may take 2-3 minutes)..."
    colima start --cpu 6 --memory 16 --kubernetes
    sleep 10
fi
print_success "Colima is running"
echo ""

# Step 3: Verify Kubernetes
echo "☸️  Step 3: Verifying Kubernetes cluster..."
if kubectl get nodes &> /dev/null; then
    print_success "Kubernetes cluster is ready"
else
    print_error "Kubernetes cluster is not ready"
    exit 1
fi
echo ""

# Step 4: Deploy Tomcat
echo "🐱 Step 4: Deploying Tomcat application..."
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml
wait_for_pods "default" "app=tomcat-sample"
print_success "Tomcat deployed successfully"
echo ""

# Step 5: Verify Tomcat accessibility
echo "🌐 Step 5: Verifying Tomcat is accessible..."
sleep 10  # Give LoadBalancer time to initialize
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "200"; then
    print_success "Tomcat is accessible at http://localhost:8080"
else
    print_info "Tomcat may take a few more seconds to be fully ready"
fi
echo ""

# Step 6: Create monitoring namespace
echo "📊 Step 6: Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
print_success "Monitoring namespace ready"
echo ""

# Step 7: Deploy Prometheus Config
echo "📈 Step 7: Deploying Prometheus configuration..."
kubectl apply -f kubernetes-manifests/prometheus-config.yaml
print_success "Prometheus config created"
echo ""

# Step 8: Deploy Prometheus
echo "📈 Step 8: Deploying Prometheus..."
kubectl apply -f kubernetes-manifests/prometheus-deployment.yaml
sleep 5
print_success "Prometheus deployment created"
echo ""

# Step 9: Deploy kube-state-metrics
echo "📊 Step 9: Deploying kube-state-metrics..."
kubectl apply -f kubernetes-manifests/kube-state-metrics.yaml
sleep 5
print_success "kube-state-metrics deployment created"
echo ""

# Step 10: Deploy Grafana
echo "📊 Step 10: Deploying Grafana..."
kubectl apply -f kubernetes-manifests/grafana-deployment.yaml
sleep 5
print_success "Grafana deployment created"
echo ""

# Step 11: Wait for monitoring stack
echo "⏳ Step 11: Waiting for monitoring stack to be ready..."
wait_for_pods "monitoring" "app=prometheus"
wait_for_pods "monitoring" "app=kube-state-metrics"
wait_for_pods "monitoring" "app=grafana"
print_success "Monitoring stack is ready"
echo ""

# Step 12: Verify Prometheus
echo "🔍 Step 12: Verifying Prometheus..."
sleep 10
if curl -s http://localhost:30090/-/healthy | grep -q "Prometheus is Healthy"; then
    print_success "Prometheus is healthy at http://localhost:30090"
else
    print_info "Prometheus may take a few more seconds to be fully ready"
fi
echo ""

# Step 13: Install Python dependencies
echo "🐍 Step 13: Installing Python dependencies..."
cd ai-scaler-v3
if pip3 install -q -r requirements.txt; then
    print_success "Python dependencies installed"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi
cd ..
echo ""

# Step 14: Make scripts executable
echo "🔧 Step 14: Making scripts executable..."
chmod +x ai-scaler-v3/start_v3.sh
chmod +x ai-scaler-v3/stop_v3.sh
print_success "Scripts are executable"
echo ""

# Summary
echo ""
echo "============================================"
echo "✅ Setup Complete! AI Scaler V3 is Ready"
echo "============================================"
echo ""
echo "📍 Access Points:"
echo "   Tomcat:     http://localhost:8080"
echo "   Prometheus: http://localhost:30090"
echo "   Grafana:    http://localhost:30300 (admin/admin123)"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1️⃣  Start AI Scaler V3:"
echo "   cd ai-scaler-v3"
echo "   ./start_v3.sh"
echo ""
echo "2️⃣  Open Grafana Dashboard:"
echo "   open http://localhost:30300"
echo "   Login: admin/admin123"
echo "   Import dashboard from: grafana/dashboards/autoscaler-dashboard.json"
echo ""
echo "3️⃣  Generate Load with JMeter (in new terminal):"
echo "   cd /Users/nabanish/Desktop/apache-jmeter-5.6.3/bin"
echo "   ./jmeter -n -t /Users/nabanish/Desktop/LocalHost_Tomcat.jmx -l results.jtl"
echo ""
echo "4️⃣  Watch Autoscaling:"
echo "   - AI Scaler V3 terminal: See scaling decisions"
echo "   - Grafana dashboard: Visual metrics"
echo "   - kubectl get pods -w: Watch pods scale"
echo ""
echo "📖 Full documentation: START_V3_COMPLETE.md"
echo ""
echo "Happy autoscaling! 🎉"

# Made by Nabanish with Bob's assistance
