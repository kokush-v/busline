#!/usr/bin/env bash

set -e

# ===== CONFIG =====
INSTANCE_ID="i-0123456789abcdef0"
RDS_HOST="db.example.internal"
REMOTE_PORT="5432"
LOCAL_PORT="5432"
AWS_PROFILE="nix-dev" 
AWS_REGION="us-east-1"
# ==================

echo "🔌 Opening SSM tunnel to RDS..."
echo "EC2: $INSTANCE_ID"
echo "RDS: $RDS_HOST:$REMOTE_PORT -> localhost:$LOCAL_PORT"
echo ""

aws ssm start-session \
  --profile "$AWS_PROFILE" \
  --region "$AWS_REGION" \
  --target "$INSTANCE_ID" \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters "host=$RDS_HOST,portNumber=$REMOTE_PORT,localPortNumber=$LOCAL_PORT"
