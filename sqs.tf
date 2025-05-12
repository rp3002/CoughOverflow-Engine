# ========================
# SQS Queue for Celery
# ========================

resource "aws_sqs_queue" "coughoverflow_queue" {
  name                        = "coughoverflow-queue"
  visibility_timeout_seconds = 3600
  message_retention_seconds  = 86400

  tags = {
    Environment = "Lab"
    Project     = "CoughOverflow"
  }
}

output "sqs_queue_url" {
  value = aws_sqs_queue.coughoverflow_queue.id
}
