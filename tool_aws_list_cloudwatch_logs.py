import boto3
from datetime import datetime, timedelta
import pytz
from langchain.tools import tool
import pandas as pd

@tool
def list_all_log_groups_as_table(region: str) -> str:
    """
    Lists all CloudWatch log groups and returns them as a markdown table.

    Args:
        region (str): The AWS region to list log groups in.

    Returns:
        str: A markdown table of all the log groups
    """
    logs_client = boto3.client('logs', region)

    # Get all log groups
    log_groups = []
    paginator = logs_client.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        log_groups.extend(page['logGroups'])

    # Convert to DataFrame
    df = pd.DataFrame(log_groups)

    # Select and rename columns
    columns_to_display = {
        'logGroupName': 'Log Group Name',
        'creationTime': 'Creation Time',
        'metricFilterCount': 'Metric Filter Count',
        'arn': 'ARN',
        'storedBytes': 'Stored Bytes'
    }

    df = df.rename(columns=columns_to_display)
    df = df[[col for col in columns_to_display.values() if col in df.columns]]

    # Convert creation time to readable format
    if 'Creation Time' in df.columns:
        df['Creation Time'] = pd.to_datetime(df['Creation Time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convert stored bytes to MB
    if 'Stored Bytes' in df.columns:
        df['Stored Bytes'] = (df['Stored Bytes'] / (1024 * 1024)).round(2).astype(str) + ' MB'

    # Convert DataFrame to markdown table
    markdown_table = df.to_markdown(index=False)

    return markdown_table

@tool
def list_log_groups_with_content(until_hours_ago: int = 1) -> str:
    """
    Lists all CloudWatch logs until n hours ago, defaults to 1 hour

    Args:
        args (int): The number of hours ago to list all logs

    Returns:
        str: A summary report of all CloudWatch logs of all cloudwatch log groups

    """
    logs_client = boto3.client('logs', 'eu-west-1')

    # Get all log groups
    log_groups = []
    paginator = logs_client.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        log_groups.extend(page['logGroups'])

    # Get current time and time an hour ago
    now = datetime.now(pytz.UTC)
    one_hour_ago = now - timedelta(hours=1)

    result = ""
    # Fetch and print logs for each group
    for group in log_groups:
        result += f"Log Group: {group['logGroupName']}\n"
        try:
            response = logs_client.filter_log_events(
                logGroupName=group['logGroupName'],
                startTime=int(one_hour_ago.timestamp() * 1000),
                endTime=int(now.timestamp() * 1000)
            )
            for event in response['events']:
                result += f"  Timestamp: {datetime.fromtimestamp(event['timestamp']/1000, pytz.UTC)}\n"
                result += f"  Message: {event['message']}\n\n"
        except Exception as e:
            result += f"  Error fetching logs: {str(e)}\n"
        result += "-" * 50

    return result
