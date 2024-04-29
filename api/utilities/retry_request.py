"""Utility functions to handle requests"""
import time
import requests
from report.log_and_report import (write_logging_error,
                                   write_logging_simple_message)

MAX_RETRIES = 3


def retry_request(function):
    """
    Decorator function that retries a given function a maximum number of times 
    in case of exceptions.

    Args:
        function: The function to be retried.

    Returns:
        The result of the function if successful.

    Raises:
        TimeoutError: If the maximum number of retries is reached without success.
    """
    def wrapper(*args, **kwargs):
        for i in range(MAX_RETRIES):
            try:
                result = function(*args, **kwargs)
                return result
            except requests.exceptions.RequestException as e:
                write_logging_error(f"Error making request: {e}")
                if i == MAX_RETRIES - 1:
                    print("Reached max number of retries. Aborting...")
                    raise e
                write_logging_simple_message(f"Retrying request in {2 ** i} seconds...")
                time.sleep(2**i)
        raise TimeoutError("Max request retries reached")

    return wrapper
