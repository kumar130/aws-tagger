import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_resource_arns_by_name(resource_name):
    """
    Get AWS resource ARNs for a specific resource name.

    :param resource_name: The name of the AWS resource (e.g., 'ec2', 's3', 'efs', 'lambda', 'ecs-cluster', 'ecs-service', 'ecs-task', 'dms').
    :return: List of ARNs for the specified resource name.
    """
    try:
        arns = []

        if resource_name == "ec2":
            ec2_client = boto3.client('ec2')
            instances = ec2_client.describe_instances()
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    arns.append(instance['InstanceId'])

        elif resource_name == "s3":
            s3_client = boto3.client('s3')
            buckets = s3_client.list_buckets()
            for bucket in buckets['Buckets']:
                arns.append(f"arn:aws:s3:::{bucket['Name']}")

        elif resource_name == "efs":
            efs_client = boto3.client('efs')
            file_systems = efs_client.describe_file_systems()
            for fs in file_systems['FileSystems']:
                arns.append(fs['FileSystemArn'])

        elif resource_name == "lambda":
            lambda_client = boto3.client('lambda')
            functions = lambda_client.list_functions()
            for function in functions['Functions']:
                arns.append(function['FunctionArn'])

        elif resource_name == "ecs-cluster":
            ecs_client = boto3.client('ecs')
            clusters = ecs_client.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                arns.append(cluster_arn)

        elif resource_name == "ecs-service":
            ecs_client = boto3.client('ecs')
            clusters = ecs_client.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                services = ecs_client.list_services(cluster=cluster_arn)
                for service_arn in services['serviceArns']:
                    arns.append(service_arn)

        elif resource_name == "ecs-task":
            ecs_client = boto3.client('ecs')
            clusters = ecs_client.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                tasks = ecs_client.list_tasks(cluster=cluster_arn)
                for task_arn in tasks['taskArns']:
                    arns.append(task_arn)

        elif resource_name == "dms":
            dms_client = boto3.client('dms')
            tasks = dms_client.describe_replication_tasks()
            for task in tasks['ReplicationTasks']:
                arns.append(task['ReplicationTaskArn'])

        else:
            print(f"Resource name {resource_name} is not supported.")

        return arns

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def list_existing_tags(resource_arn):
    """
    List the existing tags for a specific AWS resource.

    :param resource_arn: The ARN of the resource to list tags for.
    :return: Dictionary of existing tags.
    """
    try:
        client = boto3.client('resourcegroupstaggingapi')
        response = client.get_resources(
            ResourceARNList=[resource_arn]
        )
        tags = {}
        for resource in response.get('ResourceTagMappingList', []):
            if resource['ResourceARN'] == resource_arn:
                tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                break

        return tags

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred while retrieving tags: {e}")
        return {}

def tag_multiple_resources(resource_arns, tags):
    """
    Tag multiple AWS resources with specific tags.

    :param resource_arns: The list of ARNs of the resources to tag.
    :param tags: Dictionary of tags to apply.
    """
    try:
        client = boto3.client('resourcegroupstaggingapi')
        response = client.tag_resources(
            ResourceARNList=resource_arns,
            Tags=tags
        )

        if response.get('FailedResourcesMap'):
            print(f"Failed to tag some resources.")
        else:
            print(f"Successfully tagged resources: {resource_arns}")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred while tagging resources: {e}")

if __name__ == "__main__":
    # Prompt user for resource name
    resource_name = input("Enter the AWS resource name (e.g., 'ec2', 's3', 'efs', 'lambda', 'ecs-cluster', 'ecs-service', 'ecs-task', 'dms'): ")

    # Get ARNs for the specified resource name
    resource_arns = get_resource_arns_by_name(resource_name)

    if resource_arns:
        print(f"Retrieved ARNs for {resource_name}:")
        for arn in resource_arns:
            print(arn)

        # Prompt user to select multiple resource ARNs
        selected_arns = input("Enter the ARNs of the resources you want to tag, separated by commas: ").split(',')
        selected_arns = [arn.strip() for arn in selected_arns if arn.strip() in resource_arns]

        if selected_arns:
            # Prompt user for new tags
            tags_input = input("Enter new tags as key=value pairs separated by commas: ")
            tags = dict(tag.split('=') for tag in tags_input.split(','))

            # Tag the selected resources
            tag_multiple_resources(selected_arns, tags)
        else:
            print("Invalid ARNs selected.")
    else:
        print(f"No ARNs found for the resource name: {resource_name}.")
