# =========================
# PostgreSQL via RDS Setup
# =========================

resource "aws_db_subnet_group" "coughoverflow_db_subnet_group" {
  name       = "coughoverflow-db-subnet-group"
  subnet_ids = data.aws_subnets.public.ids
}

resource "aws_security_group" "postgres_sg" {
  name        = "coughoverflow-postgres-sg"
  description = "Allow Postgres access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL from ECS"
    from_port   = 5432
    to_port     = 5432
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

resource "aws_db_instance" "postgres" {
  identifier         = "coughoverflow-db"
  allocated_storage  = 20
  engine             = "postgres"
  engine_version     = "17"
  instance_class     = "db.t3.micro"
  db_name               = "coughoverflow"
  username           = "postgresuser"
  password           = "Password123!"
  db_subnet_group_name = aws_db_subnet_group.coughoverflow_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.postgres_sg.id]
  skip_final_snapshot = true
  publicly_accessible = true
}

output "postgres_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
