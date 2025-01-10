import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def retag_resources(resource_arns, new_tags):
    """
    Retag multiple AWS resources.

    :param resource_arns: List of ARNs of the resources to retag.
    :param new_tags: Dictionary of new tags to apply.
    """
    client = boto3.client('resourcegroupstaggingapi')

    try:
        # Convert tags dictionary to required format
        tags = [{"Key": k, "Value": v} for k, v in new_tags.items()]

        for arn in resource_arns:
            print(f"Updating tags for resource: {arn}")
            response = client.tag_resources(
                ResourceARNList=[arn],
                Tags=new_tags
            )
            if response.get('FailedResourcesMap'):
                print(f"Failed to update tags for resource: {arn}")
            else:
                print(f"Successfully updated tags for resource: {arn}")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example resource ARNs
    resource_arns = [
        "arn:aws:s3:::test-81211"
    ]

    # Example tags to apply
    new_tags = {
        "Environment": "Production",
        "Project": "ProjectX"
        "cust": "mt"
        "env": "prvl"
    }

    retag_resources(resource_arns, new_tags)
