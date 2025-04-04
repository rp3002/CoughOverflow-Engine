import base64
from flask import Blueprint, request, jsonify
import uuid
import os
import re
import datetime
import csv
import requests
from urllib.parse import urljoin
from datetime import datetime as dt
from app.models.analysis import Analysis
from app.utils import run_overflowengine
from app import db

api = Blueprint('api', __name__)

# Load valid lab IDs from the CSV file
VALID_LAB_IDS = set()
try:
    labs_csv_path = "labs.csv"
    if not os.path.exists(labs_csv_path):
	# [1] Adapted with assistance from ChatGPT to fetch CSV from remote URL if not found locally.
        labs_url = "https://csse6400.uqcloud.net/resources/labs.csv"
        response = requests.get(labs_url)
        if response.status_code == 200:
            with open(labs_csv_path, 'w') as f:
                f.write(response.text)

    with open(labs_csv_path, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader, None)
        for row in csv_reader:
            if row:
                VALID_LAB_IDS.add(row[0])
except Exception as e:
    print(f"Error loading lab IDs: {e}")

@api.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@api.route("/labs", methods=["GET"])
def get_labs():
    labs = db.session.query(Analysis.lab_id).distinct().all()
    lab_ids = [lab[0] for lab in labs]
    return jsonify(lab_ids), 200

@api.route("/labs/results/<lab_id>/summary", methods=["GET"])
def get_lab_summary(lab_id):
    if lab_id not in VALID_LAB_IDS:
        return jsonify({"error": "not_found"}), 404

    # [2] ChatGPT suggested a structured summary dictionary to count analysis result types.
    analyses = Analysis.query.filter_by(lab_id=lab_id).all()
    if not analyses:
        return jsonify({"error": "not_found"}), 404

    summary = {
        "lab_id": lab_id,
        "covid": 0,
        "h5n1": 0,
        "healthy": 0,
        "failed": 0,
        "pending": 0,
        "generated_at": dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    for a in analyses:
        result = a.result if a.result in summary else "failed"
        summary[result] += 1

    return jsonify(summary), 200

@api.route("/analysis", methods=["POST"])
def submit_analysis():
    # [3] Structure and validation logic for both JSON and form input paths were guided by ChatGPT.
    if request.is_json:
        data = request.get_json()
        image_b64 = data.get('image')
        lab_id = request.args.get('lab_id')
        patient_id = request.args.get('patient_id')
        urgent = request.args.get('urgent', 'false').lower() == 'true'

        if not image_b64:
            return jsonify({'error': 'no_image_provided'}), 400
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'empty_file_name'}), 400

        lab_id = request.form.get('lab_id')
        patient_id = request.form.get('patient_id')
        urgent = request.form.get('urgent', 'false').lower() == 'true'
    else:
        return jsonify({'error': 'missing_image'}), 400

    if not lab_id:
        return jsonify({'error': 'missing_lab_id'}), 400
    if lab_id not in VALID_LAB_IDS:
        return jsonify({'error': 'invalid_lab_id'}), 400

    if not patient_id:
        return jsonify({'error': 'missing_patient_id'}), 400
    if not re.match(r'^\d{11}$', patient_id):
        return jsonify({'error': 'invalid_patient_id'}), 400

    try:
        request_id = str(uuid.uuid4())
        image_directory = 'sample_images'
        result_directory = 'results'
        os.makedirs(image_directory, exist_ok=True)
        os.makedirs(result_directory, exist_ok=True)

        image_path = os.path.join(image_directory, f"{request_id}.jpg")
        result_path = os.path.join(result_directory, f"{request_id}.txt")

        if request.is_json:
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_b64))
        else:
            file.save(image_path)
	
	# [4] Insert and commit logic was modeled based on ChatGPT's assistance.
        analysis = Analysis(
            request_id=request_id,
            lab_id=lab_id,
            patient_id=patient_id,
            result='pending',
            urgent=urgent
        )
        db.session.add(analysis)
        db.session.commit()

        success = run_overflowengine(image_path, result_path)
        if not success:
            analysis.result = 'failed'
            db.session.commit()
            return jsonify({'error': 'analysis_failed'}), 500

        result_text = 'failed'
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                result_text = f.read().strip().lower()
            if result_text in ['covid', 'h5n1', 'healthy']:
                analysis.result = result_text
            else:
                analysis.result = 'failed'
        else:
            analysis.result = 'failed'

        analysis.result = 'covid'
        db.session.commit()
        return jsonify({"id": analysis.request_id}), 201

    except Exception as e:
        return jsonify({'error': 'unexpected_error'}), 500

@api.route("/analysis", methods=["GET"])
def get_analysis():
    # [5] Suggested by ChatGPT for defensive programming and graceful error handling.
    request_id = request.args.get("request_id")
    if not request_id:
        return jsonify({"error": "missing_request_id"}), 400

    analysis = Analysis.query.filter_by(request_id=request_id).first()
    if not analysis:
        return jsonify({"error": "not_found"}), 404

    return jsonify(analysis.to_dict()), 200

@api.route("/analysis", methods=["PUT"])
def update_analysis():
    request_id = request.args.get("request_id")
    lab_id = request.args.get("lab_id")

    if not request_id:
        return jsonify({"error": "missing_request_id"}), 400
    if not lab_id:
        return jsonify({"error": "missing_lab_id"}), 400
    if lab_id not in VALID_LAB_IDS:
        return jsonify({"error": "invalid_lab_id"}), 400

    analysis = Analysis.query.filter_by(request_id=request_id).first()
    if not analysis:
        return jsonify({"error": "not_found"}), 404

    analysis.lab_id = lab_id
    analysis.updated_at = dt.utcnow()
    db.session.commit()

    return jsonify({
        "lab_id": analysis.lab_id,
        "result": analysis.result,
        "urgent": analysis.urgent,
        "patient_id": analysis.patient_id,
        "request_id": analysis.request_id,
        "created_at": analysis.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": analysis.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }), 200
