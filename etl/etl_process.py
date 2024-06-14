import os
from datetime import datetime
from typing import Any
from pandas import DataFrame
from data.data import error_logger_path, success_logger_path, target_file_path_json
from globals.globals import file_exists, write_logs, connect_to_mongodb
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def extract_process(file_to_process: str):
    """
        Extract specific columns from a JSON file and return as a DataFrame.
        :param file_to_process: Path to the JSON file to process.
        :return: DataFrame with the specified columns, or an empty DataFrame on failure.
    """

    try:
        if not file_exists(file_to_process):
            write_logs('failed', error_logger_path, f'Error occurred cannot find {file_to_process} !!')
            return pd.DataFrame()

        extracted_data = pd.read_json(file_to_process)

    except FileNotFoundError:
        write_logs('failed', error_logger_path,
                   f'Failed to find file: {target_file_path_json}')
    except pd.errors.EmptyDataError:
        write_logs('failed', error_logger_path, f'No data {target_file_path_json} is empty')
    except pd.errors.ParserError:
        write_logs('failed', error_logger_path, f'parsing error: {target_file_path_json} '
                                                f'could not be found')
    except Exception as e:
        write_logs('failed', error_logger_path, f'An error occurred: {e}')
    else:

        write_logs('success', success_logger_path,
                   'Data frame created successfully')
        return extracted_data
    finally:
        write_logs('success', success_logger_path,
                   f'Process finished at {datetime.now()}')


def transform_process(jobs_dataframe: DataFrame) -> dict[str, Any]:

    if jobs_dataframe.empty:
        return {}

    filtered_jobs = (jobs_dataframe[jobs_dataframe['job_id'].notna() & jobs_dataframe['employer_name'].notna() &
                                    jobs_dataframe['employer_logo'].notna() & jobs_dataframe['employer_website'].notna()
                                    & jobs_dataframe['employer_company_type'].notna() &
                                    jobs_dataframe['job_employment_type'].notna() & jobs_dataframe[
                                        'job_title'].notna() &
                                    jobs_dataframe['job_apply_link'].notna() & jobs_dataframe['job_city'].notna()].
                     reset_index(drop=True))

    transformed_doc: dict[str, Any] = {
        "job_id": filtered_jobs["job_id"].tolist(),
        "employer": {
            "name": filtered_jobs["employer_name"].tolist(),
            "logo": filtered_jobs["employer_logo"].tolist(),
            "website": filtered_jobs["employer_website"].tolist(),
            "company_type": filtered_jobs["employer_company_type"].tolist()
        },
        "publisher": filtered_jobs["job_publisher"].tolist(),
        "employment_type": filtered_jobs["job_employment_type"].tolist(),
        "title": filtered_jobs["job_title"].tolist(),
        "apply_link": filtered_jobs["job_apply_link"].tolist(),
        "apply_is_direct": filtered_jobs["job_apply_is_direct"].tolist(),
        "apply_quality_score": filtered_jobs["job_apply_quality_score"].tolist(),
        "apply_options": filtered_jobs["apply_options"].tolist(),
        "description": filtered_jobs["job_description"].tolist(),
        "is_remote": filtered_jobs["job_is_remote"].tolist(),
        "posted_at": filtered_jobs["job_posted_at_datetime_utc"].tolist(),
        "location": {
            "city": filtered_jobs["job_city"].tolist(),
            "state": filtered_jobs["job_state"].tolist(),
            "country": filtered_jobs["job_country"].tolist(),
            "latitude": filtered_jobs["job_latitude"].tolist(),
            "longitude": filtered_jobs["job_longitude"].tolist()
        },
        "highlights": filtered_jobs["job_highlights"].tolist(),
        "job_title": filtered_jobs["job_job_title"].tolist(),
        "posting_language": filtered_jobs["job_posting_language"].tolist(),
        "onet_soc": filtered_jobs["job_onet_soc"].tolist(),
        "onet_job_zone": filtered_jobs["job_onet_job_zone"].tolist(),
        "naics_code": filtered_jobs["job_naics_code"].tolist(),
        "naics_name": filtered_jobs["job_naics_name"].tolist()
    }

    return transformed_doc


def load_process(transformed_data: list[dict[str, Any]]) -> None:
    mongo_uri = os.getenv('MONGO_API_KEY')
    connection = connect_to_mongodb(mongo_uri)
    try:
        ping_db = connection.admin.command('ping')
    except Exception as e:
        print(e)
    else:
        if ping_db['ok'] == 1:
            jobs_database = connection['data-jobs']
            jobs_collection = jobs_database['data-job']
            jobs_collection.insert_one(transformed_data)
    finally:
        print('Process Completed')
