#!/bin/bash

echo "🤖 AI-Driven Kubernetes Autoscaler Setup"
echo "========================================"
echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

echo "✅ kubectl found"
echo ""

# Check cluster access
echo "🔍 Checking Kubernetes cluster access..."
if ! kubectl get nodes &> /dev/null; then
    echo "❌ Cannot access Kubernetes cluster. Please check your cluster is running."
    exit 1
fi

echo "✅ Kubernetes cluster accessible"
echo ""

# Check metrics-server
echo "🔍 Checking metrics-server..."
if ! kubectl top nodes &> /dev/null; then
    echo "❌ metrics-server is not working. Please ensure metrics-server is running."
    exit 1
fi

echo "✅ metrics-server is working"
echo ""

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Make ai_scaler.py executable
chmod +x ai_scaler.py

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the AI Autoscaler:"
echo ""
echo "   cd ~/Desktop/Kubernetes/ai-scaler"
echo "   source venv/bin/activate"
echo "   python3 ai_scaler.py"
echo ""
echo "📖 For more information, see README.md"
echo ""

# Made by Nabanish with the help of Bob
