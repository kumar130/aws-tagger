import boto3
import re
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def get_resource_arns_by_name(resource_name):
    """Retrieve AWS resource ARNs by resource name."""
    try:
        arns = []
        if resource_name == "ec2":
            ec2_client = boto3.client('ec2')
            for vpc in ec2_client.describe_vpcs().get('Vpcs', []):
                arns.append(vpc['VpcId'])

        elif resource_name == "s3":
            s3_client = boto3.client('s3')
            for bucket in s3_client.list_buckets().get('Buckets', []):
                arns.append(f"arn:aws:s3:::{bucket['Name']}")

        elif resource_name == "efs":
            efs_client = boto3.client('efs')
            for fs in efs_client.describe_file_systems().get('FileSystems', []):
                arns.append(fs['FileSystemArn'])

        elif resource_name == "lambda":
            lambda_client = boto3.client('lambda')
            for function in lambda_client.list_functions().get('Functions', []):
                arns.append(function['FunctionArn'])

        elif resource_name == "ecs-cluster":
            ecs_client = boto3.client('ecs')
            arns = ecs_client.list_clusters().get('clusterArns', [])

        elif resource_name == "ecs-service":
            ecs_client = boto3.client('ecs')
            for cluster_arn in ecs_client.list_clusters().get('clusterArns', []):
                arns.extend(ecs_client.list_services(cluster=cluster_arn).get('serviceArns', []))

        elif resource_name == "ecs-task":
            ecs_client = boto3.client('ecs')
            for cluster_arn in ecs_client.list_clusters().get('clusterArns', []):
                arns.extend(ecs_client.list_tasks(cluster=cluster_arn).get('taskArns', []))

        elif resource_name == "dms":
            dms_client = boto3.client('dms')
            for task in dms_client.describe_replication_tasks().get('ReplicationTasks', []):
                arns.append(task['ReplicationTaskArn'])

        elif resource_name == "vpc":
            ec2_client = boto3.client('ec2')
            for vpc in ec2_client.describe_vpcs().get('Vpcs', []):
                arns.append(f"arn:aws:ec2:{boto3.session.Session().region_name}:{boto3.client('sts').get_caller_identity().get('Account')}:vpc/{vpc['VpcId']}")

        elif resource_name == "elb":
            elb_client = boto3.client('elb')
            for lb in elb_client.describe_load_balancers().get('LoadBalancerDescriptions', []):
                arns.append(f"arn:aws:elasticloadbalancing:{boto3.session.Session().region_name}:{boto3.client('sts').get_caller_identity().get('Account')}:loadbalancer/{lb['LoadBalancerName']}")

            elbv2_client = boto3.client('elbv2')
            for lb in elbv2_client.describe_load_balancers().get('LoadBalancers', []):
                arns.append(lb['LoadBalancerArn'])

        elif resource_name == "cloudwatch-log-group":
            logs_client = boto3.client('logs')
            for log_group in logs_client.describe_log_groups().get('logGroups', []):
                arns.append(f"arn:aws:logs:{boto3.session.Session().region_name}:{boto3.client('sts').get_caller_identity().get('Account')}:log-group:{log_group['logGroupName']}")

        elif resource_name == "redis":
            redis_client = boto3.client('elasticache')
            for cluster in redis_client.describe_cache_clusters().get('CacheClusters', []):
                arns.append(cluster['ARN'])

        else:
            print(f"Resource name {resource_name} is not supported.")

        return arns

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found or incomplete. Please configure them properly.")
    except ClientError as e:
        print(f"AWS ClientError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return []

def tag_individual_resource(resource_arn, tags):
    """Apply tags to an AWS resource."""
    try:
        tagging_client = boto3.client('resourcegroupstaggingapi')
        response = tagging_client.tag_resources(ResourceARNList=[resource_arn], Tags=tags)

        if response.get('FailedResourcesMap'):
            print(f"Failed to tag resource: {resource_arn}")
        else:
            print(f"Successfully tagged resource: {resource_arn}")

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found or incomplete.")
    except ClientError as e:
        print(f"An error occurred while tagging resource: {e}")
