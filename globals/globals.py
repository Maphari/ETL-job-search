import os
from datetime import datetime
from typing import Literal

import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi

JOBS_SEARCH_API_KEY: str | None = os.getenv('X_RAPID_API_KEY')
JOBS_API_HOST: str | None = os.getenv('X_RAPID_API_HOST')
URL: str = 'https://jsearch.p.rapidapi.com/search'

headers: dict[str, str] = {"X-RapidAPI-Key": JOBS_SEARCH_API_KEY, "X-RapidAPI-Host": JOBS_API_HOST}

query_string: dict[str, str] = {'query': 'Data engineering'}

log_process_directory = 'log_process/'
log_process_file: str = 'log_process.log'
log_process_file_path: str = os.path.join(log_process_directory, log_process_file)

target_file_directory: str = 'jobs/'
target_file_json: str = 'jobs_data.json'
target_file_path_json: str = os.path.join(target_file_directory, target_file_json)

success_logger_file: str = 'success_logger.txt'
success_logger_path: str = os.path.join(log_process_directory, success_logger_file)
error_logger_file: str = 'error_logger.txt'
error_logger_path: str = os.path.join(log_process_directory, error_logger_file)

target_db_file = 'Jobs.db'
target_db_file_directory: str = 'db'
target_db_file_path: str = os.path.join(target_db_file_directory, target_db_file)
table_name: str = 'Jobs'


def file_exists(path_: str) -> bool:
    """
    Check if a file or directory exists at the given path.

    :param path_: The path to the file or directory.
    :return: True if the file or directory exists, False otherwise.
    """
    return os.path.exists(path_)


def mkdir(path_: str) -> None:
    """This method takes a path and make a directory"""
    os.makedirs(path_, exist_ok=True)


def to_write(write_: str, basename: str, message_: str, time: datetime) -> str:
    """Format the log message."""
    return f'{write_} message on file: {basename} {message_} at: {time}\n'


def write_logs(success_or_error_: Literal['success', 'failed'], path_: str, message_: str,
               time: datetime = datetime.now()) -> None:
    """
        Logs messages to a specified file.

        :param success_or_error_: Indicates if the message is a success or failure.
        :param path_: The file path where the log should be written.
        :param message_: The log message.
        :param time: The time of the log entry, defaults to the current time.
    """

    if time is None:
        time = datetime.now()

    current_file = __file__
    basename: str = os.path.basename(current_file)

    write_to_file: str
    if success_or_error_ == 'success':
        write_to_file = to_write('Success', basename, message_, time)
    elif success_or_error_ == 'failed':
        write_to_file = to_write('Failed', basename, message_, time)
    else:
        raise ValueError(f'This {success_or_error_} is an invalid valued accepted value [success, failed]')

    with open(path_, 'a') as f:
        f.write(f'{write_to_file}')


def log_process(message_: str) -> None:
    current_time = datetime.now().strftime('%Y-%h-%d-%H:%M:%S')

    if not file_exists(log_process_directory):
        mkdir(log_process_directory)

    with open(log_process_file_path, 'a') as f_logs:
        f_logs.write(f'{message_}, {current_time}\n')


def connect_to_mongodb(mongo_uri: str):
    client = MongoClient(mongo_uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    return client
