# Tomcat Deployment File Comparison

## Issue Found
You correctly identified that we were using the wrong Tomcat deployment file!

## The Two Files

### ❌ tomcat-deployment.yaml (WRONG - Newly Created)
- **Location**: `kubernetes-manifests/tomcat-deployment.yaml`
- **Labels**: `app: tomcat-sample-app`
- **Image**: `tomcat:9.0`
- **Resources**: Lower (256Mi-512Mi memory)
- **Startup**: Complex (removes IP restrictions)
- **Problem**: Label mismatch with V2's working configuration

### ✅ tomcat-with-sample-app.yaml (CORRECT - From V2)
- **Location**: `kubernetes-manifests/tomcat-with-sample-app.yaml`
- **Labels**: `app: tomcat-sample` ← **Consistent with V2**
- **Image**: `tomcat:10.1-jdk17` ← **Newer version**
- **Resources**: Higher (512Mi-1Gi memory) ← **Better for load testing**
- **Startup**: Simple (just copies webapps)
- **Proven**: Already tested and working with V2

## Why This Matters

### V3 Config Expectations
The `ai-scaler-v3/config.yaml` expects:
```yaml
target:
  namespace: "default"
  deployment: "tomcat-sample-app"  # ✅ Deployment name
```

### Label Consistency
- **V2 uses**: `app: tomcat-sample`
- **V3 should use**: `app: tomcat-sample` (same as V2)
- **Wrong file had**: `app: tomcat-sample-app` (inconsistent)

## What Was Fixed

### 1. Copied Working V2 File
```bash
cp /Users/nabanish/Desktop/Kubernetes_AIAutoScaler/kubernetes-manifests/tomcat-with-sample-app.yaml \
   /Users/nabanish/Desktop/Prometheus_Kubernetes_Scaler/kubernetes-manifests/
```

### 2. Updated quick-start-v3.sh
Changed line 97:
```bash
# Before (WRONG)
kubectl apply -f kubernetes-manifests/tomcat-deployment.yaml

# After (CORRECT)
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml
```

Changed line 98:
```bash
# Before (WRONG)
wait_for_pods "default" "app=tomcat-sample-app"

# After (CORRECT)
wait_for_pods "default" "app=tomcat-sample"
```

### 3. Updated START_V3_COMPLETE.md
- Step 2.2: Use `tomcat-with-sample-app.yaml`
- Step 9.3: Delete using correct file
- Quick Reference: Use correct label `app=tomcat-sample`

## Correct Commands for V3

### Deploy Tomcat
```bash
kubectl apply -f kubernetes-manifests/tomcat-with-sample-app.yaml
```

### Check Tomcat Pods
```bash
kubectl get pods -l app=tomcat-sample
```

### Delete Tomcat
```bash
kubectl delete -f kubernetes-manifests/tomcat-with-sample-app.yaml
```

## Summary
✅ **Fixed**: Now using the proven V2 Tomcat deployment
✅ **Consistent**: Labels match between V2 and V3
✅ **Better**: Higher resources for load testing
✅ **Tested**: Already working with V2 autoscaler

---

**Made by Nabanish with Bob's assistance**