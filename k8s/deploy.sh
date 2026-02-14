#!/bin/bash

echo "🚀 Deploying Job Hunter AI to Kubernetes..."

# Apply manifests in order
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres-deployment.yaml

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n job-hunter --timeout=120s

# Deploy backend
kubectl apply -f backend-deployment.yaml

# Optional: Apply ingress
# kubectl apply -f ingress.yaml

echo "✅ Deployment complete!"
echo ""
echo "📊 Check status:"
echo "  kubectl get pods -n job-hunter"
echo "  kubectl get services -n job-hunter"
echo ""
echo "🌐 Get backend URL:"
echo "  kubectl get service backend-service -n job-hunter"
