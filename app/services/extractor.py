import os
import shutil
from datetime import datetime, timezone
import logging
from app.db import db
from app.models import ExtractionLog, ExtractedFile
from app.services.zip_handler import handle_zip
from app.services.tar_handler import handle_tar

logger=logging.getLogger(__name__)

def archive_router(file_path, display_chain, depth, pattern, workspace_dir, matches, job_id, source_archive_name=None):

    if depth >5:
        logger.warning(f"Job {job_id}: Exceeded arbitrary depth safety threshold limit at chain {display_chain}")
        return
    
    file_lower = file_path.lower()
    if file_lower.endswith('.zip'):
        handle_zip(
            file_path=file_path,
            display_chain=display_chain,
            depth=depth,
            pattern=pattern,
            workspace_dir=workspace_dir,
            matches=matches,
            job_id=job_id,
            recursive_trigger=archive_router,
            source_archive_name=source_archive_name
        )
    elif file_lower.endswith(('.tar', '.tar.gz', '.tgz')):
        handle_tar(
            file_path=file_path,
            display_chain=display_chain,
            depth=depth,
            pattern=pattern,
            workspace_dir=workspace_dir,
            matches=matches,
            job_id=job_id,
            recursive_trigger=archive_router,
            source_archive_name=source_archive_name
        )

def process_archive_job(app, job_id, upload_path, original_filename, glob_pattern):
    with app.app_context():
        job = db.session.get(ExtractionLog, job_id)
        if not job:
            if os.path.exists(upload_path):
                os.remove(upload_path)
            return
        
        job.status='RUNNING'
        db.session.commit()

        base_dir =os.path.dirname(upload_path)
        job_workspace = os.path.join(base_dir, f"workspace_{job_id}")
        os.makedirs(job_workspace, exist_ok=True)

        raw_matches=[]
        try:
            archive_router(
                file_path=upload_path,
                display_chain=original_filename,
                depth=0,
                pattern=glob_pattern,
                workspace_dir=job_workspace,
                matches=raw_matches,
                job_id=job_id,
                source_archive_name=original_filename
            )
            
            if raw_matches:
                db_objects=[ExtractedFile(**m) for m in raw_matches]
                db.session.bulk_save_objects(db_objects)
                
            job.status ="COMPLETED"
            job.completed_at=datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"Job {job_id} completed successfully with {len(raw_matches)} matches.")

        except Exception as e:
            db.session.rollback()
            job.status="FAILED"
            job.error_message = str(e)
            job.completed_at=datetime.now(timezone.utc)
            db.session.commit()
            logger.error(f"Job {job_id} failed:{str(e)}",exc_info=True)

        finally:
            if os.path.exists(upload_path):
                try:
                    os.remove(upload_path)
                except OSError:
                    pass
            if os.path.exists(job_workspace):
                try:
                    shutil.rmtree(job_workspace)
                except OSError:
                    pass
