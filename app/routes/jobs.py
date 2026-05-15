from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.job import Job, VALID_STATUSES

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@jobs_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    """
    Add a new job application
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required: [company, role]
          properties:
            company: {type: string, example: "Google"}
            role: {type: string, example: "Backend Engineer"}
            status: {type: string, example: "applied"}
            job_description: {type: string}
            notes: {type: string}
            location: {type: string, example: "Bangalore"}
            salary: {type: string, example: "12 LPA"}
            applied_date: {type: string, example: "2026-05-10"}
    responses:
      201:
        description: Job created
    """
    data = request.get_json()
    user_id = int(get_jwt_identity())

    if not data or not all(k in data for k in ("company", "role")):
        return jsonify({"error": "company and role are required"}), 400

    status = data.get("status", "applied")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    applied_date = None
    if data.get("applied_date"):
        try:
            applied_date = date.fromisoformat(data["applied_date"])
        except ValueError:
            return jsonify({"error": "applied_date must be YYYY-MM-DD format"}), 400

    job = Job(
        user_id=user_id,
        company=data["company"],
        role=data["role"],
        status=status,
        job_description=data.get("job_description"),
        notes=data.get("notes"),
        location=data.get("location"),
        salary=data.get("salary"),
        applied_date=applied_date,
    )

    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job added", "job": job.to_dict()}), 201


@jobs_bp.route("", methods=["GET"])
@jwt_required()
def get_jobs():
    """
    Get all job applications (with optional filters)
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        description: Filter by status (applied/interview/offer/rejected/withdrawn)
      - in: query
        name: company
        type: string
        description: Filter by company name (partial match)
    responses:
      200:
        description: List of jobs
    """
    user_id = int(get_jwt_identity())
    query = Job.query.filter_by(user_id=user_id)

    # Optional filters
    status = request.args.get("status")
    company = request.args.get("company")

    if status:
        if status not in VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Use: {', '.join(VALID_STATUSES)}"}), 400
        query = query.filter_by(status=status)

    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))

    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify({"total": len(jobs), "jobs": [j.to_dict() for j in jobs]}), 200


@jobs_bp.route("/<int:job_id>", methods=["GET"])
@jwt_required()
def get_job(job_id):
    """
    Get a single job application
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
    responses:
      200:
        description: Job details
      404:
        description: Job not found
    """
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job.to_dict()), 200


@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    """
    Update a job application
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          properties:
            company: {type: string}
            role: {type: string}
            status: {type: string}
            notes: {type: string}
            job_description: {type: string}
            location: {type: string}
            salary: {type: string}
            applied_date: {type: string}
    responses:
      200:
        description: Job updated
    """
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updatable = ["company", "role", "status", "job_description", "notes", "location", "salary"]
    for field in updatable:
        if field in data:
            if field == "status" and data[field] not in VALID_STATUSES:
                return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400
            setattr(job, field, data[field])

    if "applied_date" in data:
        try:
            job.applied_date = date.fromisoformat(data["applied_date"]) if data["applied_date"] else None
        except ValueError:
            return jsonify({"error": "applied_date must be YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify({"message": "Job updated", "job": job.to_dict()}), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    """
    Delete a job application
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
    responses:
      200:
        description: Job deleted
    """
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": f"Job at {job.company} deleted"}), 200


@jobs_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    """
    Get application statistics for the logged-in user
    ---
    tags: [Jobs]
    security:
      - Bearer: []
    responses:
      200:
        description: Stats breakdown by status
    """
    user_id = int(get_jwt_identity())
    jobs = Job.query.filter_by(user_id=user_id).all()

    breakdown = {s: 0 for s in VALID_STATUSES}
    for job in jobs:
        if job.status in breakdown:
            breakdown[job.status] += 1

    return jsonify({
        "total": len(jobs),
        "breakdown": breakdown,
        "interview_rate": (
            round(breakdown["interview"] / len(jobs) * 100, 1) if jobs else 0
        ),
    }), 200
