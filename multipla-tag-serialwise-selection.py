import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def list_supported_resources():
    return [
        "ec2", "s3", "efs", "lambda", "ecs-cluster", "ecs-service", "ecs-task",
        "dms", "vpc", "elb", "logs", "redis"
    ]

def get_resource_arns_by_name(resource_name):
    """
    Get AWS resource ARNs for a specific resource name.
    """
    try:
        arns = []

        if resource_name == "ec2":
            ec2_client = boto3.client('ec2')
            instances = ec2_client.describe_instances()
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    arns.append(f"arn:aws:ec2:{boto3.session.Session().region_name}::instance/{instance['InstanceId']}")

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
            arns.extend(clusters['clusterArns'])

        elif resource_name == "ecs-service":
            ecs_client = boto3.client('ecs')
            clusters = ecs_client.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                services = ecs_client.list_services(cluster=cluster_arn)
                arns.extend(services['serviceArns'])

        elif resource_name == "ecs-task":
            ecs_client = boto3.client('ecs')
            clusters = ecs_client.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                tasks = ecs_client.list_tasks(cluster=cluster_arn)
                arns.extend(tasks['taskArns'])

        elif resource_name == "dms":
            dms_client = boto3.client('dms')
            tasks = dms_client.describe_replication_tasks()
            for task in tasks['ReplicationTasks']:
                arns.append(task['ReplicationTaskArn'])

        elif resource_name == "vpc":
            ec2_client = boto3.client('ec2')
            vpcs = ec2_client.describe_vpcs()['Vpcs']
            for vpc in vpcs:
                arns.append(f"arn:aws:ec2:{boto3.session.Session().region_name}::vpc/{vpc['VpcId']}")

        elif resource_name == "elb":
            elb_client = boto3.client('elbv2')
            load_balancers = elb_client.describe_load_balancers()['LoadBalancers']
            for lb in load_balancers:
                arns.append(lb['LoadBalancerArn'])

        elif resource_name == "logs":
            logs_client = boto3.client('logs')
            log_groups = logs_client.describe_log_groups()['logGroups']
            for log_group in log_groups:
                arns.append(f"arn:aws:logs:{boto3.session.Session().region_name}:{log_group['logGroupName']}")

        elif resource_name == "redis":
            elasticache_client = boto3.client('elasticache')
            clusters = elasticache_client.describe_cache_clusters()['CacheClusters']
            for cluster in clusters:
                arns.append(cluster['ARN'])

        else:
            print(f"Resource name {resource_name} is not supported.")

        return arns

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found or incomplete. Please configure your credentials.")
    except ClientError as e:
        print(f"AWS ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def tag_multiple_resources(resource_arns, tags):
    """
    Tag multiple AWS resources with specific tags.
    """
    try:
        client = boto3.client('resourcegroupstaggingapi')
        response = client.tag_resources(
            ResourceARNList=resource_arns,
            Tags=tags
        )
        if response.get('FailedResourcesMap'):
            print("Failed to tag some resources.")
        else:
            print(f"Successfully tagged resources: {resource_arns}")

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found or incomplete. Please configure your credentials.")
    except ClientError as e:
        print(f"AWS ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An error occurred while tagging resources: {e}")

if __name__ == "__main__":
    resource_types = list_supported_resources()
    print("Select the AWS resource type:")
    for i, res_type in enumerate(resource_types, 1):
        print(f"{i}. {res_type}")

    selected_index = int(input("Enter the serial number of the resource type: ").strip())
    if 1 <= selected_index <= len(resource_types):
        resource_name = resource_types[selected_index - 1]
    else:
        print("Invalid selection.")
        exit()

    resource_arns = get_resource_arns_by_name(resource_name)

    if resource_arns:
        print(f"Retrieved ARNs for {resource_name}:")
        for i, arn in enumerate(resource_arns, 1):
            print(f"{i}. {arn}")

        selected_indices = input("Enter the serial numbers of the ARNs to tag, separated by commas: ")
        selected_indices = [int(idx.strip()) for idx in selected_indices.split(',') if idx.strip().isdigit()]
        selected_arns = [resource_arns[i-1] for i in selected_indices if 1 <= i <= len(resource_arns)]

        if selected_arns:
            tags_input = input("Enter new tags as key=value pairs separated by commas: ")
            try:
                tags = dict(tag.split('=') for tag in tags_input.split(','))
                tag_multiple_resources(selected_arns, tags)
            except ValueError:
                print("Invalid tag format. Use key=value pairs.")
        else:
            print("Invalid selection.")
    else:
        print(f"No ARNs found for {resource_name}.")
