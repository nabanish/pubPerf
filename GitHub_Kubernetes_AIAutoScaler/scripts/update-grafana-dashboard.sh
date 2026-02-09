#!/bin/bash

# Update Grafana Dashboard Script
# This script updates the Grafana dashboard with the fixed queries

set -e

echo "🔄 Updating Grafana Dashboard..."

# Get Grafana pod name
GRAFANA_POD=$(kubectl get pods -n monitoring -l app=grafana -o jsonpath='{.items[0].metadata.name}')

if [ -z "$GRAFANA_POD" ]; then
    echo "❌ Error: Grafana pod not found"
    exit 1
fi

echo "📊 Found Grafana pod: $GRAFANA_POD"

# Copy the updated dashboard to Grafana pod
echo "📤 Uploading updated dashboard..."
kubectl cp grafana/dashboards/autoscaler-dashboard.json monitoring/$GRAFANA_POD:/tmp/dashboard.json

# Import the dashboard using Grafana API
echo "🔧 Importing dashboard via API..."
kubectl exec -n monitoring $GRAFANA_POD -- sh -c '
DASHBOARD_JSON=$(cat /tmp/dashboard.json)
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"dashboard\": $DASHBOARD_JSON, \"overwrite\": true}" \
  http://admin:admin123@localhost:3000/api/dashboards/db
'

echo "✅ Dashboard updated successfully!"
echo ""
echo "🌐 Access Grafana at: http://localhost:30300"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 The dashboard should now show CPU, Memory, and Network metrics!"

# Made by Nabanish with Bob's assistance
