# 📁 Repository Structure

This document describes the organization of the Kubernetes AI Autoscaler repository.

## Directory Layout

```
Kubernetes_AIAutoScaler/
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick setup guide
├── LICENSE                        # Apache 2.0 License
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── REPOSITORY_STRUCTURE.md        # This file
│
├── ai_scaler_v2.py               # Main autoscaler application
│
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── TESTING_GUIDE.md          # Testing scenarios
│   └── V1_VS_V2_COMPARISON.md    # Feedback loop analysis
│
├── kubernetes-manifests/          # Kubernetes YAML files
│   ├── tomcat-with-sample-app.yaml    # Main application
│   ├── dashboard-admin.yaml           # Dashboard setup
│   ├── sample-app.yaml                # Sample nginx app
│   ├── tomcat-deployment.yaml         # Basic Tomcat
│   └── hpa-tomcat-sample.yaml         # HPA example
│
└── scripts/                       # Helper scripts
    ├── reset_and_start_v2.sh     # Reset and start autoscaler
    ├── stop_and_cleanup.sh       # Stop and clean up
    └── setup.sh                   # Initial setup
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation with features, setup, and usage |
| `QUICKSTART.md` | 5-minute setup guide for quick start |
| `LICENSE` | Apache 2.0 open source license |
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Files to exclude from Git |
| `ai_scaler_v2.py` | Main AI autoscaler application (V2 - fixed) |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `README.md` | Documentation index and overview |
| `TESTING_GUIDE.md` | Comprehensive testing scenarios and expected behaviors |
| `V1_VS_V2_COMPARISON.md` | Analysis of V1 feedback loop problem and V2 fix |

### Kubernetes Manifests (`kubernetes-manifests/`)

| File | Purpose |
|------|---------|
| `tomcat-with-sample-app.yaml` | **Main deployment** - Tomcat with sample app |
| `dashboard-admin.yaml` | Kubernetes Dashboard admin user setup |
| `sample-app.yaml` | Simple nginx sample application |
| `tomcat-deployment.yaml` | Basic Tomcat deployment (alternative) |
| `hpa-tomcat-sample.yaml` | HPA example (not used with AI scaler) |

### Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| `reset_and_start_v2.sh` | Reset metrics/model and start autoscaler |
| `stop_and_cleanup.sh` | Stop autoscaler and clean up resources |
| `setup.sh` | Initial environment setup |

## Key Components

### 1. AI Autoscaler (`ai_scaler_v2.py`)

**Main Features:**
- Machine Learning with Random Forest
- Feature engineering (time patterns, trends)
- Heuristic validation
- Dampening logic
- Automatic model retraining

**Configuration:**
- Lines 24-32: Scaling parameters
- Lines 355-368: Dampening logic
- Lines 200-250: Feature engineering
- Lines 300-350: ML model training

### 2. Kubernetes Manifests

**Primary Deployment:**
```yaml
# tomcat-with-sample-app.yaml
- Deployment: tomcat-sample-app
- Service: tomcat-sample-service
- Resources: 100m-1000m CPU, 256Mi-512Mi memory
- Replicas: Managed by AI autoscaler
```

**Dashboard Setup:**
```yaml
# dashboard-admin.yaml
- ServiceAccount: admin-user
- ClusterRoleBinding: admin-user
- Token: For dashboard access
```

### 3. Helper Scripts

**Reset and Start:**
```bash
./scripts/reset_and_start_v2.sh
# - Deletes old metrics and model
# - Scales to 1 replica
# - Starts autoscaler
```

**Stop and Cleanup:**
```bash
./scripts/stop_and_cleanup.sh
# - Stops autoscaler
# - Cleans up resources
# - Resets deployment
```

## Usage Workflow

### Initial Setup
```
1. Clone repository
2. Install dependencies (requirements.txt)
3. Start Kubernetes cluster (Colima)
4. Deploy application (kubernetes-manifests/)
5. Run autoscaler (ai_scaler_v2.py)
```

### Testing Cycle
```
1. Start autoscaler (scripts/reset_and_start_v2.sh)
2. Generate load (JMeter or curl)
3. Monitor scaling behavior
4. Observe ML model training
5. Test different scenarios (docs/TESTING_GUIDE.md)
```

### Cleanup
```
1. Stop load generation
2. Stop autoscaler (Ctrl+C)
3. Run cleanup script (scripts/stop_and_cleanup.sh)
4. Optional: Stop Colima
```

## Important Notes

### Files NOT in Repository (`.gitignore`)

- `*.pkl` - ML model files (generated at runtime)
- `*.json` - Metrics history (generated at runtime)
- `venv/` - Python virtual environment
- `.DS_Store` - macOS system files
- `dashboard-token.txt` - Sensitive token

### Generated at Runtime

- `scaler_model_v2.pkl` - Trained Random Forest model
- `metrics_history_v2.json` - Historical metrics data
- `dashboard-token.txt` - Kubernetes Dashboard token

### Prerequisites

- Colima with Kubernetes (k3s)
- Python 3.8+
- kubectl configured
- 4+ CPU cores recommended

## Quick Reference

### Start Everything
```bash
colima start --kubernetes
source venv/bin/activate
./scripts/reset_and_start_v2.sh
```

### Monitor
```bash
# Watch autoscaler (already running)
# In new terminal:
watch kubectl get pods
kubectl top pods
```

### Generate Load
```bash
kubectl port-forward svc/tomcat-sample-service 9091:8080
# Use JMeter or curl
```

### Stop Everything
```bash
# Ctrl+C (autoscaler)
./scripts/stop_and_cleanup.sh
colima stop
```

## Documentation Links

- **Main README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Testing Guide**: [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)
- **V1 vs V2**: [docs/V1_VS_V2_COMPARISON.md](docs/V1_VS_V2_COMPARISON.md)

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review troubleshooting in `README.md`
3. Open a GitHub issue

---

**Repository Version**: 2.0 (Fixed Feedback Loop)
**Last Updated**: 2024