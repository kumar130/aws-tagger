import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_resource_arns_by_name(resource_name):
    """
    Get AWS resource ARNs for a specific resource name.

    :param resource_name: The name of the AWS resource (e.g., 'ec2', 's3', 'lambda').
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

if __name__ == "__main__":
    # Prompt user for resource name
    resource_name = input("Enter the AWS resource name (e.g., 'ec2', 's3', 'lambda'): ")

    # Get ARNs for the specified resource name
    resource_arns = get_resource_arns_by_name(resource_name)

    if resource_arns:
        print(f"Retrieved ARNs for {resource_name}:")
        for arn in resource_arns:
            print(arn)
    else:
        print(f"No ARNs found for the resource name: {resource_name}.")
