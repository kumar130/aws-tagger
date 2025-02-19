#!/bin/bash

# Function to get user input for ECS Cluster
read -p "Enter ECS Cluster Name: " ECS_CLUSTER

# Fetch list of services in the cluster
echo "Fetching services for ECS cluster: $ECS_CLUSTER ..."
SERVICES_JSON=$(aws ecs list-services --cluster "$ECS_CLUSTER" --query "serviceArns" --output json)

# Extract services into an array
SERVICES=($(echo "$SERVICES_JSON" | jq -r '.[]'))
if [ ${#SERVICES[@]} -eq 0 ]; then
  echo "No services found in cluster: $ECS_CLUSTER"
  exit 1
fi

# Display Service Selection Menu
echo "Select a Service:"
select ECS_SERVICE in "${SERVICES[@]}"; do
  if [[ -n "$ECS_SERVICE" ]]; then
    echo "Selected Service: $ECS_SERVICE"
    break
  else
    echo "Invalid selection. Try again."
  fi
done

# Fetch running tasks for the selected service
echo "Fetching running tasks for service '$ECS_SERVICE'..."
TASKS_JSON=$(aws ecs list-tasks --cluster "$ECS_CLUSTER" --service-name "$ECS_SERVICE" --query "taskArns" --output json)

# Extract tasks into an array
TASKS=($(echo "$TASKS_JSON" | jq -r '.[]'))
if [ ${#TASKS[@]} -eq 0 ]; then
  echo "No running tasks found for service: $ECS_SERVICE"
  exit 1
fi

# Display Task Selection Menu
echo "Select a Task ID:"
select TASK_ID in "${TASKS[@]}"; do
  if [[ -n "$TASK_ID" ]]; then
    echo "Selected Task: $TASK_ID"
    break
  else
    echo "Invalid selection. Try again."
  fi
done

# Get Task Details
TASK_DESC=$(aws ecs describe-tasks --cluster "$ECS_CLUSTER" --tasks "$TASK_ID")

# Extract Container Instance ID
CONTAINER_INSTANCE_ID=$(echo "$TASK_DESC" | jq -r '.tasks[0].containerInstanceArn')

# Get EC2 Instance ID for the container
EC2_INSTANCE_ID=$(aws ecs describe-container-instances --cluster "$ECS_CLUSTER" --container-instances "$CONTAINER_INSTANCE_ID" --query "containerInstances[0].ec2InstanceId" --output text)

echo "Task is running on EC2 Instance: $EC2_INSTANCE_ID"

# Get Public IP of the EC2 instance
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$EC2_INSTANCE_ID" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

if [ -z "$PUBLIC_IP" ]; then
  echo "Error: Could not retrieve public IP. Ensure the instance has a public IP or use SSM."
  exit 1
fi

# SSH into the instance and find the Java Process ID
echo "Connecting to instance ($PUBLIC_IP) to find Java process..."
JAVA_PID=$(ssh -o StrictHostKeyChecking=no ec2-user@"$PUBLIC_IP" "pgrep -f java")

if [ -z "$JAVA_PID" ]; then
  echo "No Java process found in the ECS task."
  exit 1
fi

echo "Java Process ID found: $JAVA_PID"

# Get S3 Bucket Name from User
read -p "Enter the S3 Bucket Name to upload the heap dump: " S3_BUCKET

# Generate Heap Dump using jmap
DUMP_PATH="/tmp/heapdump_$(date +%F_%H-%M-%S).hprof"
echo "Generating heap dump at $DUMP_PATH ..."
ssh -o StrictHostKeyChecking=no ec2-user@"$PUBLIC_IP" "jmap -dump:live,format=b,file=$DUMP_PATH $JAVA_PID"

# Copy heap dump to S3
echo "Uploading heap dump to S3: s3://$S3_BUCKET/"
ssh -o StrictHostKeyChecking=no ec2-user@"$PUBLIC_IP" "aws s3 cp $DUMP_PATH s3://$S3_BUCKET/"

echo "Heap dump uploaded successfully to s3://$S3_BUCKET/"
