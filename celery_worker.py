import os
import boto3
import time
import json
from app import create_app, db
from app.models.analysis import Analysis
from app.utils import run_overflowengine

# Create Flask app context
flask_app = create_app()

# Read from environment
queue_url = os.environ.get("SQS_QUEUE_URL")
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

# Init SQS client
sqs = boto3.client("sqs", region_name=region)

def poll_and_process():
    print("Celery Worker: Polling for messages...")
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            messages = response.get("Messages", [])
            if not messages:
                continue  # long poll timed out

            for message in messages:
                receipt_handle = message["ReceiptHandle"]
                body = json.loads(message["Body"])
                request_id = body.get("request_id")

                if request_id:
                    print(f" Received task for request_id: {request_id}")
                    process_analysis_task(request_id)

                # Remove message from queue
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

        except Exception as e:
            print(f" Error polling SQS: {e}")
            time.sleep(5)

def process_analysis_task(request_id):
    with flask_app.app_context():
        analysis = Analysis.query.filter_by(request_id=request_id).first()
        if not analysis:
            print(f" No analysis found for {request_id}")
            return

        image_path = f"sample_images/{request_id}.jpg"
        result_path = f"results/{request_id}.txt"

        os.makedirs("sample_images", exist_ok=True)
        os.makedirs("results", exist_ok=True)

        print(f" Running overflowengine on {image_path}")
        success = run_overflowengine(image_path, result_path)

        if not success:
            analysis.result = "failed"
        elif os.path.exists(result_path):
            with open(result_path, "r") as f:
                result = f.read().strip().lower()
            analysis.result = result if result in ['covid', 'h5n1', 'healthy'] else 'failed'
        else:
            analysis.result = "failed"

        db.session.commit()
        print(f" Updated result for {request_id}: {analysis.result}")

# Entry point
if __name__ == "__main__":
    poll_and_process()

