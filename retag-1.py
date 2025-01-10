import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_resource_arns_by_name(resource_name):
    """
    Get AWS resource ARNs for a specific resource name.

    :param resource_name: The name of the AWS resource (e.g., 'ec2', 's3', 'efs', 'lambda').
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

def tag_individual_resource(resource_arn, tags):
    """
    Tag an individual AWS resource with specific tags.

    :param resource_arn: The ARN of the resource to tag.
    :param tags: Dictionary of tags to apply.
    """
    try:
        client = boto3.client('resourcegroupstaggingapi')
        response = client.tag_resources(
            ResourceARNList=[resource_arn],
            Tags=tags
        )

        if response.get('FailedResourcesMap'):
            print(f"Failed to tag resource: {resource_arn}")
        else:
            print(f"Successfully tagged resource: {resource_arn}")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred while tagging resource: {e}")

if __name__ == "__main__":
    # Prompt user for resource name
    resource_name = input("Enter the AWS resource name (e.g., 'ec2', 's3', 'efs', 'lambda'): ")

    # Get ARNs for the specified resource name
    resource_arns = get_resource_arns_by_name(resource_name)

    if resource_arns:
        print(f"Retrieved ARNs for {resource_name}:")
        for arn in resource_arns:
            print(arn)

        # Prompt user to select a resource ARN
        selected_arn = input("Enter the ARN of the resource you want to tag: ")

        if selected_arn in resource_arns:
            # List existing tags for the selected ARN
            existing_tags = list_existing_tags(selected_arn)
            print("Existing tags:")
            for key, value in existing_tags.items():
                print(f"  {key}: {value}")

            # Prompt user for new tags
            tags_input = input("Enter new tags as key=value pairs separated by commas: ")
            tags = dict(tag.split('=') for tag in tags_input.split(','))

            # Tag the selected resource
            tag_individual_resource(selected_arn, tags)
        else:
            print("Invalid ARN selected.")
    else:
        print(f"No ARNs found for the resource name: {resource_name}.")
