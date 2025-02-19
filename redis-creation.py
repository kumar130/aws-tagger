import boto3

def create_redis_cluster(cluster_id, instance_type, parameter_group, vpc_id, subnet_ids, security_group_id, cluster_mode, multi_az):
    # Initialize the ElastiCache client
    client = boto3.client('elasticache')

    try:
        # Prepare the arguments for the API request
        kwargs = {
            "CacheClusterId": cluster_id,
            "CacheNodeType": instance_type,
            "Engine": "redis",
            "CacheParameterGroupName": parameter_group,
            "SecurityGroupIds": [security_group_id],
            "SubnetGroupName": create_subnet_group(client, cluster_id, subnet_ids),
            "NumCacheNodes": 1,  # Default for standalone Redis
        }

        # Cluster mode (for Redis cluster mode)
        if cluster_mode.lower() == "on":
            kwargs.pop("CacheClusterId")  # Replace CacheClusterId with ReplicationGroupId
            kwargs.pop("NumCacheNodes")
            kwargs["ReplicationGroupId"] = cluster_id
            kwargs["ReplicationGroupDescription"] = f"Replication group for {cluster_id}"
            kwargs["NumNodeGroups"] = 1  # Default to a single shard; you can adjust as needed
            kwargs["NumCacheClusters"] = 2  # Minimum 2 nodes for cluster mode

        # Multi-AZ
        if multi_az.lower() == "yes":
            kwargs["PreferredAvailabilityZones"] = None  # Let AWS handle distribution
            kwargs["MultiAZEnabled"] = True

        # Create the Redis cluster
        if cluster_mode.lower() == "on":
            response = client.create_replication_group(**kwargs)
        else:
            response = client.create_cache_cluster(**kwargs)

        print("Redis cluster creation initiated. Details:")
        print(response)
    except Exception as e:
        print(f"Error creating Redis cluster: {e}")

def create_subnet_group(client, cluster_id, subnet_ids):
    subnet_group_name = f"{cluster_id}-subnet-group"
    try:
        # Create the subnet group
        client.create_cache_subnet_group(
            CacheSubnetGroupName=subnet_group_name,
            CacheSubnetGroupDescription=f"Subnet group for {cluster_id}",
            SubnetIds=subnet_ids,
        )
        print(f"Subnet group '{subnet_group_name}' created successfully.")
        return subnet_group_name
    except Exception as e:
        print(f"Error creating subnet group: {e}")
        raise

if __name__ == "__main__":
    # Take inputs from the user
    cluster_id = input("Enter the Redis cluster ID (e.g., my-redis-cluster): ").strip()
    instance_type = input("Enter the instance type (e.g., cache.t2.micro): ").strip()
    parameter_group = input("Enter the parameter group name (e.g., default.redis6.x): ").strip()
    vpc_id = input("Enter the VPC ID (e.g., vpc-0abcd1234efgh5678): ").strip()

    subnet_ids_input = input("Enter the subnet IDs separated by commas (e.g., subnet-0abcd1234efgh5678,subnet-0ijkl1234mnop5678): ").strip()
    subnet_ids = [subnet.strip() for subnet in subnet_ids_input.split(",")]

    security_group_id = input("Enter the security group ID (e.g., sg-0abcd1234efgh5678): ").strip()
    cluster_mode = input("Enable cluster mode? (on/off): ").strip().lower()
    multi_az = input("Enable Multi-AZ deployment? (yes/no): ").strip().lower()

    # Create the Redis cluster
    create_redis_cluster(cluster_id, instance_type, parameter_group, vpc_id, subnet_ids, security_group_id, cluster_mode, multi_az)
