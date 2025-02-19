import boto3

# Define required tags
REQUIRED_TAGS = {"cust": "default_customer", "appname": "default_app"}

# Initialize boto3 clients
ecs_client = boto3.client("ecs")

def get_existing_tags(resource_arn):
    """Fetch existing tags for a given resource ARN."""
    try:
        response = ecs_client.list_tags_for_resource(resourceArn=resource_arn)
        return {tag['key']: tag['value'] for tag in response.get('tags', [])}
    except Exception as e:
        print(f"Error fetching tags for {resource_arn}: {e}")
        return {}

def add_missing_tags(resource_arn, existing_tags):
    """Add missing required tags to the resource."""
    missing_tags = [
        {"key": key, "value": value} for key, value in REQUIRED_TAGS.items() if key not in existing_tags
    ]

    if missing_tags:
        try:
            ecs_client.tag_resource(resourceArn=resource_arn, tags=missing_tags)
            print(f"Added missing tags to {resource_arn}: {missing_tags}")
        except Exception as e:
            print(f"Error tagging {resource_arn}: {e}")
    else:
        print(f"All required tags are present for {resource_arn}")

def process_ecs_clusters():
    """Process ECS clusters for missing tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        tags = get_existing_tags(cluster_arn)
        add_missing_tags(cluster_arn, tags)

def process_ecs_services():
    """Process ECS services for missing tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        cluster_name = cluster_arn.split("/")[-1]
        services = ecs_client.list_services(cluster=cluster_name).get("serviceArns", [])
        for service_arn in services:
            tags = get_existing_tags(service_arn)
            add_missing_tags(service_arn, tags)

def process_ecs_tasks():
    """Process ECS tasks for missing tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        cluster_name = cluster_arn.split("/")[-1]
        tasks = ecs_client.list_tasks(cluster=cluster_name).get("taskArns", [])
        for task_arn in tasks:
            tags = get_existing_tags(task_arn)
            add_missing_tags(task_arn, tags)

if __name__ == "__main__":
    print("Checking ECS Clusters...")
    process_ecs_clusters()

    print("Checking ECS Services...")
    process_ecs_services()

    print("Checking ECS Tasks...")
    process_ecs_tasks()
