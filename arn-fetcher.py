import boto3

def get_arns_from_aws(resource_names_file, resource_type, region="us-east-1"):
    """
    Fetches ARNs of AWS resources listed in a text file.

    Args:
        resource_names_file (str): Path to the text file containing resource names.
        resource_type (str): The AWS resource type (e.g., 'ec2', 's3', 'dms').
        region (str): AWS region (default: 'us-east-1').

    Returns:
        dict: A dictionary mapping resource names to ARNs.
    """
    # Initialize boto3 client
    client = boto3.client(resource_type, region_name=region)

    # Read resource names from file
    try:
        with open(resource_names_file, "r") as file:
            resource_names = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File '{resource_names_file}' not found.")
        return {}

    arns = {}

    # Process based on resource type
    try:
        if resource_type == "s3":
            buckets = client.list_buckets()
            for bucket in buckets.get("Buckets", []):
                bucket_name = bucket["Name"]
                if bucket_name in resource_names:
                    arn = f"arn:aws:s3:::{bucket_name}"
                    arns[bucket_name] = arn

        elif resource_type == "ec2":
            response = client.describe_instances()
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    if instance_id in resource_names:
                        arn = f"arn:aws:ec2:{region}::{instance_id}"
                        arns[instance_id] = arn

        elif resource_type == "dms":
            response = client.describe_replication_tasks()
            for task in response["ReplicationTasks"]:
                task_name = task["ReplicationTaskIdentifier"]
                if task_name in resource_names:
                    arn = task["ReplicationTaskArn"]
                    arns[task_name] = arn

        else:
            print(f"Resource type '{resource_type}' not yet supported.")
    except Exception as e:
        print(f"Error fetching ARNs: {e}")

    return arns


if __name__ == "__main__":
    # Input: Path to the text file containing resource names
    resource_names_file = "resources.txt"  # Replace with your file name
    resource_type = "dms"  # Replace with the resource type (e.g., 'ec2', 's3', 'dms')

    region = "us-east-1"  # Set your AWS region
    result = get_arns_from_aws(resource_names_file, resource_type, region)

    if result:
        print("Fetched ARNs:")
        for resource, arn in result.items():
            print(f"{resource}: {arn}")
    else:
        print("No ARNs found or an error occurred.")
