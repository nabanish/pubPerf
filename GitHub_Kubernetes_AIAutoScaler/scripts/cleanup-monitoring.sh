#!/bin/bash

# Cleanup Prometheus and Grafana monitoring stack
# Usage: ./cleanup-monitoring.sh

set -e

echo "=========================================="
echo "Cleaning up Prometheus & Grafana"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MANIFESTS_DIR="$PROJECT_DIR/kubernetes-manifests"

# Delete Grafana
echo ""
echo "Deleting Grafana..."
kubectl delete -f "$MANIFESTS_DIR/grafana-deployment.yaml" --ignore-not-found=true

# Delete Prometheus
echo ""
echo "Deleting Prometheus..."
kubectl delete -f "$MANIFESTS_DIR/prometheus-deployment.yaml" --ignore-not-found=true
kubectl delete -f "$MANIFESTS_DIR/prometheus-config.yaml" --ignore-not-found=true

# Optional: Delete namespace (uncomment if you want to remove the namespace)
# echo ""
# echo "Deleting monitoring namespace..."
# kubectl delete namespace monitoring --ignore-not-found=true

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "To verify:"
echo "  kubectl get all -n monitoring"
echo ""

# Made by Nabanish with Bob's assistance
