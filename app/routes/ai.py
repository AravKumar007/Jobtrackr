import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.job import Job

ai_bp = Blueprint("ai", __name__, url_prefix="/api/jobs")


@ai_bp.route("/<int:job_id>/analyze", methods=["POST"])
@jwt_required()
def analyze_job(job_id):
    """
    AI-powered analysis of a job — resume tips, skill gaps, interview prep
    ---
    tags: [AI]
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
            resume_summary:
              type: string
              description: Paste a short summary of your skills/experience
              example: "2 years Python, built 3 Flask APIs, knows SQL and Docker"
    responses:
      200:
        description: AI analysis with tips
      400:
        description: Job has no description to analyze
      503:
        description: AI service not configured
    """
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if not job.job_description:
        return jsonify({"error": "This job has no description. Add one first via PUT /api/jobs/<id>"}), 400

    api_key = current_app.config.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY not set in .env"}), 503

    data = request.get_json() or {}
    resume_summary = data.get("resume_summary", "No resume summary provided.")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are a career coach helping a college student land their first job or internship.

Job Details:
- Company: {job.company}
- Role: {job.role}
- Job Description: {job.job_description}

Candidate's background:
{resume_summary}

Give a concise, practical analysis in this exact format:

**Match Score:** X/10

**Top 3 strengths for this role:**
1. ...
2. ...
3. ...

**Top 3 skill gaps to address:**
1. ...
2. ...
3. ...

**3 resume bullet points to add:**
1. ...
2. ...
3. ...

**2 likely interview questions:**
1. ...
2. ...

Keep it actionable and specific. No fluff."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )

        analysis = message.content[0].text
        return jsonify({
            "job": job.to_dict(),
            "analysis": analysis,
        }), 200

    except Exception as e:
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500
