#!/bin/bash

echo "🛑 Stopping AI Autoscaler and Cleaning Up"
echo "=========================================="
echo ""

# Stop any running autoscaler processes
echo "1️⃣  Stopping autoscaler processes..."
pkill -9 -f "python3 ai_scaler" 2>/dev/null && echo "   ✓ Stopped autoscaler" || echo "   ℹ️  No autoscaler running"
sleep 2

# Scale deployment to 1 pod
echo ""
echo "2️⃣  Scaling deployment to 1 pod..."
kubectl scale deployment tomcat-sample-app --replicas=1
sleep 5

# Delete any failed/pending pods
echo ""
echo "3️⃣  Cleaning up failed/pending pods..."
kubectl delete pods -l app=tomcat-sample --field-selector=status.phase!=Running 2>/dev/null && echo "   ✓ Cleaned up pods" || echo "   ℹ️  No pods to clean"

# Wait for stabilization
echo ""
echo "4️⃣  Waiting for system to stabilize..."
sleep 10

# Show final state
echo ""
echo "5️⃣  Final state:"
kubectl get deployment tomcat-sample-app
echo ""
kubectl get pods -l app=tomcat-sample

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 System is now stable with 1 pod running"
echo ""

# Made by Nabanish with the help of Bob
