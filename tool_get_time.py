import time
from langchain.tools import tool

@tool
def get_current_time(ignored: str = '') -> str:
    """
    Retrieves the current time in RFC 3339 format.
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")
