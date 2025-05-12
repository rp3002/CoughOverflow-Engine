# ========================
# ECS Celery Worker Setup
# ========================

# [ADDED] Fetch AWS account ID dynamically
# data "aws_caller_identity" "current" {}

resource "aws_ecs_task_definition" "celery_worker_task" {
  family                   = "coughoverflow-celery-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = data.aws_iam_role.lab.arn
  task_role_arn            = data.aws_iam_role.lab.arn

  container_definitions = jsonencode([
    {
      name      = "celery-worker",
      image     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/coughoverflow:latest",
      essential = true,

      # Python polling script
      command   = ["python3", "celery_worker.py"],

      environment = [
        {
          name  = "AWS_DEFAULT_REGION"
          value = "us-east-1"
        },
        {
          name  = "SQS_QUEUE_URL"
          value = aws_sqs_queue.coughoverflow_queue.id
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://coughuser:Password123!@${aws_db_instance.postgres.address}:5432/coughoverflow"
        }
      ],

      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.coughoverflow_logs.name,
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "celery"
        }
      }
    }
  ])
}

# ================================
#  EECS Service for Celery Worker
# ================================
resource "aws_ecs_service" "celery_worker_service" {
  name            = "celery-worker-service"
  cluster         = aws_ecs_cluster.coughoverflow_cluster.id
  task_definition = aws_ecs_task_definition.celery_worker_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.public.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  # [DEPENDENCY] Wait for ALB listener (adjust if named differently)
  depends_on = [aws_lb_listener.coughoverflow_listener]
}

