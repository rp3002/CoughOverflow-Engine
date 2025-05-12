# terraform Configuration and AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["./credentials"]

  default_tags {
    tags = {
      Environment = "Dev"
      Course      = "6400"
      StudentID   = "47324000"
    }
  }
}

data "aws_caller_identity" "current" {}

# ========================
# VPC, Subnets, IAM, SGs
# ========================

data "aws_iam_role" "lab" {
  name = "LabRole"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_security_group" "alb_sg" {
  name        = "coughoverflow-alb-sg"
  description = "Allow HTTP from internet"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "coughoverflow-ecs-sg"
  description = "Allow traffic from ALB to ECS task on port 8080"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# =======================
# Load Balancer + ECS
# =======================

resource "aws_lb" "coughoverflow_lb" {
  name               = "coughoverflow-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = data.aws_subnets.public.ids
  security_groups    = [aws_security_group.alb_sg.id]
}

resource "aws_lb_target_group" "coughoverflow_tg" {
  name        = "coughoverflow-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/api/v1/health"
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "coughoverflow_listener" {
  load_balancer_arn = aws_lb.coughoverflow_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.coughoverflow_tg.arn
  }
}

resource "aws_ecs_cluster" "coughoverflow_cluster" {
  name = "coughoverflow-cluster"
}

resource "aws_cloudwatch_log_group" "coughoverflow_logs" {
  name              = "/ecs/coughoverflow-service"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "coughoverflow_task" {
  family                   = "coughoverflow-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = data.aws_iam_role.lab.arn

  container_definitions = jsonencode([
    {
      name      = "coughoverflow",
      image     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/coughoverflow:latest",
      essential = true,
      portMappings = [
        {
          containerPort = 8080,
          hostPort      = 8080,
          protocol      = "tcp"
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/coughoverflow-service",
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  depends_on = [aws_cloudwatch_log_group.coughoverflow_logs]
}

resource "aws_ecs_service" "coughoverflow_service" {
  name            = "coughoverflow-service"
  cluster         = aws_ecs_cluster.coughoverflow_cluster.id
  task_definition = aws_ecs_task_definition.coughoverflow_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = data.aws_subnets.public.ids
    assign_public_ip = true
    security_groups  = [aws_security_group.ecs_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.coughoverflow_tg.arn
    container_name   = "coughoverflow"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.coughoverflow_listener]
}

output "coughoverflow_url" {
  value       = aws_lb.coughoverflow_lb.dns_name
  description = "Public Load Balancer DNS for COUGHOVERFLOW API"
}
