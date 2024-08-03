import boto3
from datetime import datetime, timedelta
import pandas as pd
from langchain.tools import tool

def get_bedrock_token_counts(start_time, end_time, model_id, region: str):
    cloudwatch = boto3.client('cloudwatch', region)

    metrics = [
        {'Name': 'InputTokenCount', 'Stat': 'Sum'},
        {'Name': 'OutputTokenCount', 'Stat': 'Sum'}
    ]

    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': f'm{i}',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Bedrock',
                        'MetricName': metric['Name'],
                        'Dimensions': [
                            {'Name': 'ModelId', 'Value': model_id}
                        ]
                    },
                    'Period': 3600,
                    'Stat': metric['Stat']
                }
            } for i, metric in enumerate(metrics)
        ],
        StartTime=start_time,
        EndTime=end_time
    )

    results = []
    timestamps = response['MetricDataResults'][0]['Timestamps']
    for i in range(len(timestamps)):
        results.append({
            'timestamp': timestamps[i],
            'InputTokenCount': response['MetricDataResults'][0]['Values'][i],
            'OutputTokenCount': response['MetricDataResults'][1]['Values'][i]
        })

    return results

def calculate_cost(input_tokens, output_tokens):
    input_cost = (input_tokens / 1_000_000) * 3
    output_cost = (output_tokens / 1_000_000) * 15
    total_cost = input_cost + output_cost
    return input_cost, output_cost, total_cost

def generate_report(days, model_id, region: str):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    token_counts = get_bedrock_token_counts(start_time, end_time, model_id, region)

    df = pd.DataFrame(token_counts)
    df['input_cost'], df['output_cost'], df['total_cost'] = zip(*df.apply(lambda row: calculate_cost(row['InputTokenCount'], row['OutputTokenCount']), axis=1))

    df = df.sort_values('timestamp')
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    df.set_index('timestamp', inplace=True)

    return df

@tool
def bedrock_token_counts_tool(days: int, model_id: str, region: str) -> str:
    """
    Generates an Amazon Bedrock token usage and cost report for the last N days for the given model.

    Args:
        days (int): Number of days (integer)
        model_id (str): Model ID choice from the list of valid models 'anthropic.claude-3-sonnet-20240229-v1:0', 'anthropic.claude-3-5-sonnet-20240620-v1:0' or 'amazon.titan-embed-text-v2:0'
        region (str): The AWS region of Bedrock.

    Returns:
        str: A summary report of the token usage and cost.
    """
    try:
        # Validate model_id
        valid_models = [
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "amazon.titan-embed-text-v2:0"
        ]
        if model_id not in valid_models:
            return f"Error: Invalid model_id. Please use one of: {', '.join(valid_models)}"

        report = generate_report(days, model_id, region)
        return f"""Token usage and cost for model {model_id} for the last {days} days.
        {report}
        Total cost for the last {days} days: ${report["total_cost"].sum():.2f}
        """
    except ValueError:
        return "Error: Days must be an integer."
    except Exception as e:
        return f"Error generating report: {e}"
