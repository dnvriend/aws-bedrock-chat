import boto3
from langchain.tools import tool
import pandas as pd

@tool
def list_ecr_repositories_and_versions(region: str) -> str:
    """
    Lists all ECR repositories and returns a short list of versions per repository

    Args:
        region (str): the AWS region to use
    """
    try:
        ecr_client = boto3.client('ecr', region)
        repositories = ecr_client.describe_repositories()['repositories']
    except Exception as e:
        return f"Error: {e}"
    
    result = []
    
    for repo in repositories:
        try:
            repo_name = repo['repositoryName']
            images = ecr_client.describe_images(repositoryName=repo_name)['imageDetails']
            versions = [img['imageTag'] for img in images if 'imageTag' in img]
            result.append({
                'repository': repo_name,
                'versions': versions[:5] if versions else ['No versions found'],
                'error': None,
            })
        except Exception as e: 
            result.append({
                'repository': repo_name,
                'versions': None,
                'error': str(e),
            })

    return pd.DataFrame.from_records(result).to_markdown(index=False)


