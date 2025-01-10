#!/bin/bash

# Variables
CLUSTER_NAME=$1
SERVICE_NAME=$2
CONTAINER_NAME=$3  # Name of the container in the task

if [ -z "$CLUSTER_NAME" ] || [ -z "$SERVICE_NAME" ] || [ -z "$CONTAINER_NAME" ]; then
  echo "Usage: $0 <cluster-name> <service-name> <container-name>"
  exit 1
fi

# Get the task ARNs for the specified ECS service
TASK_ARNS=$(aws ecs list-tasks --cluster "$CLUSTER_NAME" --service-name "$SERVICE_NAME" --query 'taskArns[*]' --output text)

if [ -z "$TASK_ARNS" ]; then
  echo "No tasks found for service $SERVICE_NAME in cluster $CLUSTER_NAME"
  exit 1
fi

for TASK_ARN in $TASK_ARNS; do
  TASK_ID=$(basename "$TASK_ARN")

  echo "Checking Java processes in task: $TASK_ID"

  # Use ecs execute-command to run pgrep within the container
  OUTPUT=$(aws ecs execute-command \\\n    --cluster "$CLUSTER_NAME" \\\n    --task "$TASK_ID" \\\n    --container "$CONTAINER_NAME" \\\n    --interactive \\\n    --command "pgrep -fl java" 2>&1)

  if [[ $? -ne 0 ]]; then
    echo "Failed to execute command on task $TASK_ID. Error: $OUTPUT"
  else
    echo "Java processes in task $TASK_ID:"
    echo "$OUTPUT"
  fi
done
