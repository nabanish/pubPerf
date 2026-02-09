#!/bin/bash

# Start AI Scaler V3
# Multi-metric optimization with Prometheus integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "Starting AI Scaler V3"
echo "========================================================================"
echo ""

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo "❌ Configuration file not found: config.yaml"
    exit 1
fi

# Check Kubernetes connection
echo "Checking Kubernetes connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "Please ensure your cluster is running (e.g., colima start --kubernetes)"
    exit 1
fi
echo "✓ Kubernetes cluster is accessible"
echo ""

# Check Prometheus
echo "Checking Prometheus connection..."
PROMETHEUS_URL=$(grep -A1 "prometheus:" config.yaml | grep "url:" | awk '{print $2}' | tr -d '"')
if ! curl -s "${PROMETHEUS_URL}/api/v1/query?query=up" > /dev/null; then
    echo "❌ Cannot connect to Prometheus at ${PROMETHEUS_URL}"
    echo "Please ensure Prometheus is running:"
    echo "  kubectl get pods -n monitoring"
    echo "  kubectl port-forward -n monitoring svc/prometheus 30090:9090"
    exit 1
fi
echo "✓ Prometheus is accessible at ${PROMETHEUS_URL}"
echo ""

# Check target deployment
TARGET_NAMESPACE=$(grep -A2 "target:" config.yaml | grep "namespace:" | awk '{print $2}' | tr -d '"')
TARGET_DEPLOYMENT=$(grep -A2 "target:" config.yaml | grep "deployment:" | awk '{print $2}' | tr -d '"')

echo "Checking target deployment..."
if ! kubectl get deployment "$TARGET_DEPLOYMENT" -n "$TARGET_NAMESPACE" &> /dev/null; then
    echo "❌ Target deployment not found: $TARGET_NAMESPACE/$TARGET_DEPLOYMENT"
    echo "Available deployments:"
    kubectl get deployments -n "$TARGET_NAMESPACE"
    exit 1
fi
echo "✓ Target deployment found: $TARGET_NAMESPACE/$TARGET_DEPLOYMENT"
echo ""

# Show current configuration
echo "Configuration:"
echo "  Target: $TARGET_NAMESPACE/$TARGET_DEPLOYMENT"
echo "  Prometheus: $PROMETHEUS_URL"
echo "  Config file: config.yaml"
echo ""

# Start with system Python
echo "Starting AI Scaler V3..."
echo "Press Ctrl+C to stop"
echo ""
echo "========================================================================"
echo ""

python3 ai_scaler_v3.py --config config.yaml

# Made by Nabanish with Bob's assistance
