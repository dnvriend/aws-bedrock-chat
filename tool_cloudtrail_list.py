from langchain.tools import tool
from datetime import datetime
import boto3

@tool
def list_cloudtrail_events(max_events: int, region: str) -> str:
    """
     Lists the last 100 of cloudtrail events

    Args:
        args (int): the number of events to return, defaults to 100
        region (str): the AWS region to use

    Returns:
        str: a list of cloudwatch events
    """
    cloudtrail = boto3.client('cloudtrail', region)

    try:
        response = cloudtrail.lookup_events(
            MaxResults=max_events
        )

        events = response['Events']
        event_list = []

        for event in events:
            event_info = {
                "EventTime": event.get('EventTime', '').isoformat() if isinstance(event.get('EventTime'), datetime) else event.get('EventTime', ''),
                "EventName": event.get('EventName', ''),
                "Username": event.get('Username', ''),
                "EventSource": event.get('EventSource', ''),
                "AWSRegion": event.get('AWSRegion', '')
            }
            event_list.append(event_info)

        return event_list

    except Exception as e:
        return f"Error retrieving CloudTrail events: {str(e)}"
