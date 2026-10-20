import logging
from app.config import Config
from concurrent.futures import ThreadPoolExecutor
from app.services.extractor import process_archive_job

logger=logging.getLogger(__name__)

_executor=None

def get_task_pool():
    global _executor

    if _executor is None:
        _executor=ThreadPoolExecutor(
            max_workers=Config.CONCURRENCY,
            thread_name_prefix="worker_thread"
        )
        logger.info(f"Background worker pool started with {Config.CONCURRENCY} workers.")

    return _executor


def submit_extraction_task(app,job_id,upload_path,original_filename,glob_pattern):
    pool=get_task_pool()
    pool.submit(process_archive_job,app,job_id,upload_path,original_filename, glob_pattern)
    logger.info(f"Job {job_id} successfully handed over to a background worker thread.")

def shutdown_task_pool():
    global _executor
    if _executor is not None:
        logger.info("Shutdown signal received. Waiting for active extraction threads to finish...")
        _executor.shutdown(wait=True)

        _executor=None
        logger.info("All Background threads have stopped safely.")

       

