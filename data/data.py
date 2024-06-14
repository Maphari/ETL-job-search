import requests
import json
from dotenv import load_dotenv
from globals.globals import write_logs, file_exists, mkdir, URL, headers, query_string, error_logger_path, \
    target_file_path_json, success_logger_path, target_file_directory, log_process_directory, target_db_file_directory

load_dotenv()


def request_jobs_data() -> None:
    try:
        response: requests.Response = requests.get(URL, headers=headers, params=query_string)
        response.raise_for_status()
        jobs_json = response.json()
    except requests.exceptions.HTTPError as http_err:
        write_logs('failed', error_logger_path, f'Http error occurred: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        write_logs('failed', error_logger_path, f'Connection error occurred: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        write_logs('failed', error_logger_path, f'Timeout error occurred: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        write_logs('failed', error_logger_path, f'Request error occurred: {req_err}')
    else:
        jobs_list: list[dict] = [job for job in jobs_json.get('data', [])]

        with open(target_file_path_json, 'w') as f:
            json.dump(jobs_list, f, indent=5)

        write_logs('success', success_logger_path, 'Data fetched successfully!!')


def make_jobs_request() -> None:
    if not file_exists(target_file_directory):
        mkdir(target_file_directory)
    if not file_exists(log_process_directory):
        mkdir(log_process_directory)
    if not file_exists(target_db_file_directory):
        mkdir(target_db_file_directory)
        # with open(target_db_file_path, 'w') as db_file:
        #     pass

    request_jobs_data()
