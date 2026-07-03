provider "aws" {
  region = var.aws_region
}

# 1. Isolated Virtual Private Cloud (VPC) Topology
resource "aws_vpc" "mesh_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "guardian-mesh-vpc"
    Environment = "Production"
  }
}

# 2. Hardened Security Group Grid
resource "aws_security_group" "db_security_grid" {
  name        = "guardian-mesh-db-sg"
  description = "Enforces isolated inbound access strictly targeting database clusters"
  vpc_id      = aws_vpc.mesh_vpc.id

  ingress {
    description = "Allow stateful connections from the active container fabric"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.1.0/24"] # Points securely to the compute private subnet
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Enterprise PostgreSQL Relational Database Instance (AWS RDS)
resource "aws_db_instance" "postgres_pool" {
  identifier             = "guardian-mesh-production-db"
  allocated_storage      = 20
  max_allocated_storage  = 100 # Auto-scales disk allocation to handle heavy logging traffic
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = "db.t4g.medium" # High-efficiency ARM Graviton profile
  db_name                = "guardian_mesh_ledger"
  username               = var.db_username
  password               = var.db_password
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.db_security_grid.id]

  # Production Multi-AZ resilience flags
  multi_az            = true 
  storage_encrypted   = true
  deletion_protection = false # Set to true for production freeze environments
}

# --- ARCHITECTURAL INPUT VARIABLES ---
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "db_username" {
  type    = string
  default = "mesh_admin"
}

variable "db_password" {
  type      = string
  sensitive = true # Prevents sensitive database passwords from leaking into plaintext CI/CD terminal logs
}