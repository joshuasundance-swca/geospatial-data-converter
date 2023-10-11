#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Deploy to Kubernetes
kubectl apply -f kubernetes/resources.yaml
