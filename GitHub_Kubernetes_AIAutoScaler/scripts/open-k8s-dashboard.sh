#!/bin/bash

# Open Kubernetes Dashboard Script
# This script starts the kubectl proxy and provides the dashboard URL with token

set -e

echo "🚀 Starting Kubernetes Dashboard Access..."
echo ""

# Get the admin token (72 hours validity)
echo "📋 Creating admin token (valid for 72 hours)..."
TOKEN=$(kubectl -n kubernetes-dashboard create token admin-user --duration=72h 2>/dev/null || kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}")

echo ""
echo "✅ Token retrieved successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 KUBERNETES DASHBOARD ACCESS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Dashboard URL:"
echo "   http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
echo ""
echo "🔑 Access Token (valid for 72 hours - copy this):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$TOKEN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏰ Token Validity: 72 hours from now"
echo ""
echo "📝 Instructions:"
echo "   1. The kubectl proxy will start in a moment"
echo "   2. Open the URL above in your browser"
echo "   3. Select 'Token' authentication method"
echo "   4. Paste the token shown above"
echo "   5. Click 'Sign In'"
echo ""
echo "💡 Tip: The proxy will keep running. Press Ctrl+C to stop it."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Starting kubectl proxy..."
echo ""

# Start kubectl proxy
kubectl proxy

# Made by Nabanish with Bob's assistance
