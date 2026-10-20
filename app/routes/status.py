from flask import Blueprint, request, jsonify
from app.models import ExtractionLog, ExtractedFile

status_bp=Blueprint('status',__name__)

@status_bp.route('/extractions/<job_id>',methods=['GET'])
def get_status(job_id):
    job=ExtractionLog.query.get(job_id)
    if not job:
        return jsonify({"error": f"Job {job_id} not found"}),404
        
    match_count= ExtractedFile.query.filter_by(job_id=job_id).count()
    
    data=job.to_dict()
    data["match_count"]=match_count
    return jsonify(data),200


@status_bp.route('/extractions/<job_id>/results',methods=['GET'])
def get_results(job_id):
    job=ExtractionLog.query.get(job_id)
    if not job:
        return jsonify({"error": f"Job {job_id} not found"}), 404

    limit=request.args.get('limit',default=10,type=int)
    offset= request.args.get('offset',default=0,type=int)

    files=ExtractedFile.query.filter_by(job_id=job_id) \
                               .order_by(ExtractedFile.id.asc()) \
                               .limit(limit) \
                               .offset(offset) \
                               .all()
    return jsonify({
        "results":[f.to_dict() for f in files],
        "limit":limit,
        "offset":offset
    }), 200
