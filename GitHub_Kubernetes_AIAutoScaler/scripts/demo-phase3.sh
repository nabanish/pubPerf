#!/bin/bash

# Demo script for Phase 3 components
# Shows what's currently working

set -e

echo "=========================================="
echo "Phase 3 Demo - What's Working Now"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}1. Checking Monitoring Stack...${NC}"
echo "-------------------------------------------"
kubectl get pods -n monitoring
echo ""

echo -e "${BLUE}2. Checking Prometheus Health...${NC}"
echo "-------------------------------------------"
PROM_HEALTH=$(curl -s http://localhost:30090/-/healthy)
if [ "$PROM_HEALTH" == "Prometheus is Healthy." ]; then
    echo -e "${GREEN}✓ Prometheus is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Prometheus may not be accessible${NC}"
fi
echo ""

echo -e "${BLUE}3. Checking Tomcat Application...${NC}"
echo "-------------------------------------------"
kubectl get pods -n default | grep tomcat
echo ""

echo -e "${BLUE}4. Testing Feature Engineering...${NC}"
echo "-------------------------------------------"
cd "$PROJECT_DIR/ai-scaler-v3"
source venv/bin/activate
python3 -c "
from prometheus_client import PrometheusClient
from feature_engineering import FeatureEngineer

prom = PrometheusClient('http://localhost:30090')
fe = FeatureEngineer(prom)

print('Extracting features...')
features = fe.extract_features()

print(f'✓ Extracted {len(features)} features')
print(f'✓ Pod count: {features[\"pod_count\"]:.0f}')
print(f'✓ Hour of day: {features[\"hour_of_day\"]}')
print(f'✓ Is business hours: {\"Yes\" if features[\"is_business_hours\"] else \"No\"}')
print(f'✓ CPU trend: {features[\"cpu_trend\"]:.2f}')
print(f'✓ DataFrame ready: {fe.features_to_dataframe(features).shape}')
"
echo ""

echo -e "${BLUE}5. Querying Prometheus Metrics...${NC}"
echo "-------------------------------------------"
echo "Pod count:"
curl -s 'http://localhost:30090/api/v1/query?query=count(kube_pod_info{namespace="default",pod=~"tomcat-sample-app.*"})' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  {data['data']['result'][0]['value'][1] if data['data']['result'] else '0'} pods\")"
echo ""

echo -e "${BLUE}6. Access Points${NC}"
echo "-------------------------------------------"
echo "Prometheus UI: http://localhost:30090"
echo "Grafana UI: http://localhost:30300"
echo "  Username: admin"
echo "  Password: admin123"
echo ""

echo -e "${BLUE}7. Phase 3 Status${NC}"
echo "-------------------------------------------"
echo -e "${GREEN}✓ Architecture designed (485 lines)${NC}"
echo -e "${GREEN}✓ Feature engineering working (37 features)${NC}"
echo -e "${GREEN}✓ Prometheus monitoring operational${NC}"
echo -e "${GREEN}✓ Grafana dashboards ready${NC}"
echo ""
echo -e "${YELLOW}🔄 Time-series forecasting (pending)${NC}"
echo -e "${YELLOW}🔄 Multi-metric optimization (pending)${NC}"
echo -e "${YELLOW}🔄 Cost optimization (pending)${NC}"
echo -e "${YELLOW}🔄 Anomaly detection (pending)${NC}"
echo ""

echo -e "${BLUE}8. To Run Full Autoscaler (V2)${NC}"
echo "-------------------------------------------"
echo "cd /Users/nabanish/Desktop/Kubernetes/ai-scaler"
echo "source venv/bin/activate"
echo "python ai_scaler_v2.py"
echo ""

echo "=========================================="
echo "Demo Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. View Grafana: http://localhost:30300"
echo "2. Import dashboard from: grafana/dashboards/autoscaler-dashboard.json"
echo "3. Read architecture: docs/PHASE3_ARCHITECTURE.md"
echo "4. Test features: cd ai-scaler-v3 && python feature_engineering.py"
echo ""

# Made by Nabanish with Bob's assistance
