import boto3
import pandas as pd
import time
from langchain.tools import tool

@tool
def execute_athena_query(database: str, query: str, s3_output_location: str, region: str = 'eu-west-1') -> str:
    """
    Execute an Athena query on AWS Glue tables and format the results as a markdown table.

    Args:
        database (str): the name of the database eg. my-database
        query (str): the SQL query to execute
        s3_output_location (str): The S3 location where the query results should be stored in format s3://<bucket>/<path>
        region (str): the AWS region where the Athena query should be executed defaults to 'eu-west-1'

    Returns:
        str: A markdown-formatted table containing the query results, or an error message
"""
    try:
        athena_client = boto3.client('athena', region)
        s3_client = boto3.client('s3', region)

        # Start the query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': s3_output_location}
        )
        query_execution_id = response['QueryExecutionId']

        # Wait for the query to complete
        while True:
            query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = query_status['QueryExecution']['Status']['State']
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(1)

        if status == 'FAILED':
            error_message = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
            return f"Query execution failed: {error_message}"
        elif status == 'CANCELLED':
            return "Query was cancelled"

        # Get the results
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)

        # Process the results
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        for row in results['ResultSet']['Rows'][1:]:  # Skip the header row
            rows.append([field.get('VarCharValue', '') for field in row['Data']])

        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=columns)

        # Convert DataFrame to markdown
        markdown_table = df.to_markdown(index=False)

        return markdown_table
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

