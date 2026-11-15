#!/usr/bin/env bash

set -e

# ===== CONFIG =====
INSTANCE_ID="${INSTANCE_ID:?set INSTANCE_ID}"
RDS_HOST="${RDS_HOST:?set RDS_HOST}"
REMOTE_PORT="5432"
LOCAL_PORT="5432"
AWS_PROFILE="${AWS_PROFILE:-default}"
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
