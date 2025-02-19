import boto3
import re

# Initialize boto3 client
ecs_client = boto3.client("ecs")

def extract_info_from_name(name):
    """Extract 'cust', 'env', and 'appname' from the cluster name using the naming convention."""
    match = re.match(r"([a-zA-Z0-9]+)-([a-zA-Z0-9]+)-([a-zA-Z0-9]+)-\d{4}-\d+-\d+-\d+", name)
    if match:
        return {"cust": match.group(1), "env": match.group(2), "appname": match.group(3)}
    return {}

def get_existing_tags(resource_arn):
    """Fetch existing tags for a given resource ARN."""
    try:
        response = ecs_client.list_tags_for_resource(resourceArn=resource_arn)
        return {tag['key']: tag['value'] for tag in response.get('tags', [])}
    except Exception as e:
        print(f"Error fetching tags for {resource_arn}: {e}")
        return {}

def add_missing_tags(resource_arn, existing_tags, inferred_tags):
    """Add missing tags inferred from the cluster name if they are not already present."""
    missing_tags = [
        {"key": key, "value": inferred_tags[key]}
        for key in inferred_tags if key not in existing_tags
    ]

    if missing_tags:
        try:
            ecs_client.tag_resource(resourceArn=resource_arn, tags=missing_tags)
            print(f"Added missing tags to {resource_arn}: {missing_tags}")
        except Exception as e:
            print(f"Error tagging {resource_arn}: {e}")
    else:
        print(f"All required tags are present for {resource_arn}, skipping update.")

def process_ecs_clusters():
    """Process ECS clusters for missing tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        cluster_name = cluster_arn.split("/")[-1]
        inferred_tags = extract_info_from_name(cluster_name)

        if not inferred_tags:
            print(f"Skipping {cluster_name}: Unable to infer 'cust', 'env', or 'appname' from name.")
            continue

        existing_tags = get_existing_tags(cluster_arn)
        add_missing_tags(cluster_arn, existing_tags, inferred_tags)

def process_ecs_services():
    """Process ECS services and update missing tags using cluster tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        cluster_name = cluster_arn.split("/")[-1]
        inferred_tags = extract_info_from_name(cluster_name)

        if not inferred_tags:
            print(f"Skipping services in {cluster_name}: Unable to infer tags.")
            continue

        services = ecs_client.list_services(cluster=cluster_name).get("serviceArns", [])
        for service_arn in services:
            existing_tags = get_existing_tags(service_arn)
            add_missing_tags(service_arn, existing_tags, inferred_tags)

def process_ecs_tasks():
    """Process ECS tasks and update missing tags using cluster tags."""
    clusters = ecs_client.list_clusters().get("clusterArns", [])
    for cluster_arn in clusters:
        cluster_name = cluster_arn.split("/")[-1]
        inferred_tags = extract_info_from_name(cluster_name)

        if not inferred_tags:
            print(f"Skipping tasks in {cluster_name}: Unable to infer tags.")
            continue

        tasks = ecs_client.list_tasks(cluster=cluster_name).get("taskArns", [])
        for task_arn in tasks:
            existing_tags = get_existing_tags(task_arn)
            add_missing_tags(task_arn, existing_tags, inferred_tags)

if __name__ == "__main__":
    print("Checking ECS Clusters...")
    process_ecs_clusters()

    print("Checking ECS Services...")
    process_ecs_services()

    print("Checking ECS Tasks...")
    process_ecs_tasks()
