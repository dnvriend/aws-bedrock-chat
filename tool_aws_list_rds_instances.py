import boto3
from langchain.tools import tool

def do_list_rds_instances(region: str):
    rds = boto3.client('rds', region)

    response = rds.describe_db_instances()
    instances = response['DBInstances']

    results = []
    for instance in instances:
        results.append({
            'DBInstanceIdentifier': instance['DBInstanceIdentifier'],
            'Engine': instance['Engine'],
            'DBInstanceStatus': instance['DBInstanceStatus'],
            'DBInstanceClass': instance['DBInstanceClass'],
            'Endpoint': instance.get('Endpoint', {}).get('Address', 'N/A')
        })

    return results

@tool
def list_rds_instances(region: str) -> str:
    """
    Lists all RDS instances in a specified AWS account and region.

    Args:
        region (str): The AWS region to use.

    Returns:
        str: A summary report of all RDS instances in the specified account and region.
    """
    try:
        instances = do_list_rds_instances(region)
        if not instances:
            return f"No RDS instances found in the {region} region."
        
        report = "RDS Instances:\n"
        for instance in instances:
            report += f"\nIdentifier: {instance['DBInstanceIdentifier']}"
            report += f"\n  Engine: {instance['Engine']}"
            report += f"\n  Status: {instance['DBInstanceStatus']}"
            report += f"\n  Instance Class: {instance['DBInstanceClass']}"
            report += f"\n  Endpoint: {instance['Endpoint']}"
            report += "\n"
        
        return report
    except Exception as e:
        return f"Error listing RDS instances: {e}"
