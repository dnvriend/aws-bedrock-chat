from tool_cloudtrail_list import list_cloudtrail_events
from tool_aws_list_cloudwatch_logs import list_all_log_groups_as_table
from tool_aws_athena_execute_query import execute_athena_query
from tool_aws_glue_list_databases_and_tables import list_glue_databases_and_tables
from tool_ecr_repositories import list_ecr_repositories_and_versions
from tool_aws_bedrock_get_token_usage import bedrock_token_counts_tool
from tool_aws_list_rds_instances import list_rds_instances
from tool_get_time import get_current_time

from langchain_experimental.tools import PythonREPLTool
python_repl_tool = PythonREPLTool()

list_of_tools = [
    python_repl_tool,
    get_current_time,
    list_cloudtrail_events,
    list_all_log_groups_as_table,
    list_glue_databases_and_tables,
    list_rds_instances,
    execute_athena_query,
    bedrock_token_counts_tool,
    list_ecr_repositories_and_versions,
]