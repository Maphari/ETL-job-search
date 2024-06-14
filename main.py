from etl.etl_process import extract_process, transform_process, load_process
from data.data import make_jobs_request
from globals.globals import log_process, target_file_path_json
import schedule
import time



def main():
    # Extract
    log_process("Extraction data started")
    extract = extract_process(file_to_process=target_file_path_json)
    log_process("Extraction data finished")

    # Transform
    log_process("Transforming data started")
    transform = transform_process(extract)
    log_process("Transforming data finished")

    # Load
    log_process("loading data started")
    load_process(transform)
    log_process("loading data finished")


def do_job():
    make_jobs_request()
    main()

schedule.every().sunday.at('00:00').do(do_job)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)