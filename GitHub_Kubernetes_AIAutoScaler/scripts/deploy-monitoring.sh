#!/bin/bash

# Deploy Prometheus and Grafana monitoring stack
# Usage: ./deploy-monitoring.sh

set -e

echo "=========================================="
echo "Deploying Prometheus & Grafana Monitoring"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MANIFESTS_DIR="$PROJECT_DIR/kubernetes-manifests"

# Check if monitoring namespace exists
if ! kubectl get namespace monitoring &> /dev/null; then
    echo "Creating monitoring namespace..."
    kubectl create namespace monitoring
else
    echo "Monitoring namespace already exists"
fi

# Deploy Prometheus
echo ""
echo "Deploying Prometheus..."
kubectl apply -f "$MANIFESTS_DIR/prometheus-config.yaml"
kubectl apply -f "$MANIFESTS_DIR/prometheus-deployment.yaml"

# Deploy Grafana
echo ""
echo "Deploying Grafana..."
kubectl apply -f "$MANIFESTS_DIR/grafana-deployment.yaml"

# Wait for deployments
echo ""
echo "Waiting for Prometheus to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/prometheus -n monitoring

echo ""
echo "Waiting for Grafana to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/grafana -n monitoring

# Get service info
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Prometheus UI: http://localhost:30090"
echo "Grafana UI: http://localhost:30300"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "To check status:"
echo "  kubectl get all -n monitoring"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/prometheus -n monitoring"
echo "  kubectl logs -f deployment/grafana -n monitoring"
echo ""

# Made by Nabanish with Bob's assistance
