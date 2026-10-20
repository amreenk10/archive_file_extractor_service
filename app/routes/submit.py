import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.db import db
from app.models import ExtractionLog
from app.services.task_pool import submit_extraction_task

logger=logging.getLogger(__name__)

submit_bp=Blueprint('submit', __name__)

UPLOAD_FOLDER="/tmp/extractor_uploads"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

@submit_bp.route('/extractions',methods=['POST'])
def create_job():
    if 'archive' not in request.files or 'pattern' not in request.form:
        return jsonify({"error": "Missing archive file or pattern parameter"}), 400
    
    file =request.files['archive']
    pattern= request.form['pattern']
    
    if file.filename == '':
        return jsonify({"error":"No file selected for upload"}), 400
    
    safe_filename = secure_filename(file.filename)
    if not safe_filename:
        safe_filename="archive.bin"

    job_id=str(uuid.uuid4())
    saved_path=os.path.join(UPLOAD_FOLDER,f"{job_id}_{safe_filename}")
    
    try:
        file.save(saved_path)
    except Exception as e:
        logger.error(f"Failed to persist uploaded payload onto scratch disk: {str(e)}")
        return jsonify({"error":"Internal server disk write error"}),500


    new_job = ExtractionLog(
        id=job_id,
        status="PENDING",
        pattern=pattern,
        source_name=safe_filename
    )
    
    try:
        db.session.add(new_job)
        db.session.commit()
    except Exception as e:
        logger.error(f"Database tracking commit failed for job {job_id}: {str(e)}")
        if os.path.exists(saved_path):
            os.remove(saved_path)
        return jsonify({"error": "Database persistence failure"}), 500
    app_instance =current_app._get_current_object()
    submit_extraction_task(
        app=app_instance, 
        job_id=job_id,
        upload_path=saved_path,
        original_filename=safe_filename,
        glob_pattern=pattern
    )

    logger.info(f"Asynchronous task safely initialized. Job ID: {job_id}")
    return jsonify({"job_id": job_id}), 202