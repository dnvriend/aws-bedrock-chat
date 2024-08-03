import boto3
from langchain.tools import tool

@tool
def list_glue_databases_and_tables(region: str) -> str:
    """
    Lists all AWS Glue databases, tables, schemas, and last crawler runs

    Args:
        region (str): The AWS region to list databases and tables

    Returns:
        str: A formatted report containing the list of databases, tables, schemas, and last crawler runs.
    """
    try:
        glue_client = boto3.client('glue', region)
        
        # Get all databases
        databases = glue_client.get_databases()['DatabaseList']
        
        report = f'AWS Glue Report:\n\n'
        
        for db in databases:
            db_name = db['Name']
            report += f'Database: {db_name}\n'
            
            # Get tables for each database
            tables = glue_client.get_tables(DatabaseName=db_name)['TableList']
            
            for table in tables:
                table_name = table['Name']
                report += f'  Table: {table_name}\n'
                
                # Get schema
                if 'StorageDescriptor' in table and 'Columns' in table['StorageDescriptor']:
                    columns = table['StorageDescriptor']['Columns']
                    report += '    Schema:\n'
                    for column in columns:
                        report += f"      {column['Name']} ({column['Type']})\n"
                
                # Get last crawler run
                crawlers = glue_client.get_crawlers()['Crawlers']
                for crawler in crawlers:
                    if db_name in crawler['Targets'].get('CatalogTargets', []) or \
                       table_name in crawler['Targets'].get('S3Targets', []):
                        last_run = crawler.get('LastCrawl', {}).get('StartTime', 'N/A')
                        report += f'    Last Crawler Run: {last_run}\n'
                        break
                
                report += '\n'
            
            report += '\n'
        
        return report
    
    except Exception as e:
        return f'Error accessing AWS Glue: {str(e)}'
