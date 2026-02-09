#!/bin/bash

echo "🔄 Resetting AI Autoscaler to V2"
echo "================================"
echo ""

# Stop any running autoscaler
echo "🛑 Stopping any running autoscaler processes..."
pkill -f "python3 ai_scaler" 2>/dev/null || true
sleep 2

# Backup old files
echo "💾 Backing up old metrics and model..."
if [ -f "metrics_history.json" ]; then
    mv metrics_history.json metrics_history_v1_backup.json
    echo "   ✓ Backed up metrics_history.json"
fi

if [ -f "scaler_model.pkl" ]; then
    mv scaler_model.pkl scaler_model_v1_backup.pkl
    echo "   ✓ Backed up scaler_model.pkl"
fi

# Scale deployment to 1 pod to start fresh
echo ""
echo "📉 Scaling deployment to 1 pod (baseline)..."
kubectl scale deployment tomcat-sample-app --replicas=1
sleep 5

# Check current state
echo ""
echo "📊 Current deployment state:"
kubectl get deployment tomcat-sample-app
kubectl get pods -l app=tomcat-sample

echo ""
echo "✅ Reset complete!"
echo ""
echo "🚀 To start the improved AI Autoscaler V2:"
echo "   cd ~/Desktop/Kubernetes/ai-scaler"
echo "   source venv/bin/activate"
echo "   python3 ai_scaler_v2.py"
echo ""
echo "📝 Key improvements in V2:"
echo "   ✓ No feedback loop - predicts based on CPU load, not current pods"
echo "   ✓ Target-based scaling - aims for 500m CPU per pod"
echo "   ✓ Dampening - prevents rapid oscillations"
echo "   ✓ Better features - includes total CPU and trends"
echo ""

# Made by Nabanish with the help of Bob
