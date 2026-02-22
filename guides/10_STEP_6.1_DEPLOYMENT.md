# Step 6.1: Production Deployment

**Phase:** 6 - Deployment & Monitoring  
**Goal:** Deploy DIA v2.0 to production environment  
**Status:** ⏳ Not Started

---

## Overview

Production deployment options:
1. **Snowpark Container Services** (Recommended for Snowflake-native)
2. **AWS ECS/Fargate**
3. **Azure Container Instances**
4. **Kubernetes (GKE/AKS/EKS)**

---

## Prerequisites

- [ ] All functionality tested and working
- [ ] Evaluation framework passing (Step 5.1)
- [ ] Production credentials configured
- [ ] Monitoring setup

---

## Option 1: Snowpark Container Services (Recommended)

### Why SPCS?
- Native Snowflake integration
- No data movement
- Simplified security
- Cost-effective for Snowflake workloads

### Setup Steps

#### 1. Create Image Repository

```sql
-- Create compute pool
CREATE COMPUTE POOL dia_pool
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = STANDARD_2;

-- Create image repository
CREATE IMAGE REPOSITORY dia_images;

-- Get repository URL
SHOW IMAGE REPOSITORIES LIKE 'dia_images';
```

#### 2. Build and Push Images

```bash
# Login to Snowflake registry
docker login <your-org>-<account>.registry.snowflakecomputing.com

# Tag images
docker tag dia-orchestrator:latest <registry>/dia-orchestrator:v1.0
docker tag dia-web-app:latest <registry>/dia-web-app:v1.0

# Push to Snowflake
docker push <registry>/dia-orchestrator:v1.0
docker push <registry>/dia-web-app:v1.0
```

#### 3. Create Service

```sql
-- Create service for orchestrator
CREATE SERVICE dia_orchestrator
  IN COMPUTE POOL dia_pool
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: orchestrator
        image: <registry>/dia-orchestrator:v1.0
        env:
          SNOWFLAKE_ACCOUNT: <account>
          SNOWFLAKE_DATABASE: marketing_analytics
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
      endpoints:
      - name: api
        port: 8000
        public: true
  $$;

-- Create service for web app
CREATE SERVICE dia_web_app
  IN COMPUTE POOL dia_pool
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: web-app
        image: <registry>/dia-web-app:v1.0
        env:
          API_URL: http://dia-orchestrator:8000
        resources:
          requests:
            cpu: 0.5
            memory: 1Gi
      endpoints:
      - name: streamlit
        port: 8501
        public: true
  $$;

-- Check status
SHOW SERVICES;
CALL SYSTEM$GET_SERVICE_STATUS('dia_orchestrator');
```

---

## Option 2: AWS ECS/Fargate

### Setup Infrastructure

```bash
# Install AWS CLI and Terraform
terraform init

# Deploy infrastructure
terraform apply -var-file=prod.tfvars
```

### Terraform Configuration

**File:** `infrastructure/aws/main.tf`

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "dia" {
  name = "dia-cluster"
}

# Task Definition - Orchestrator
resource "aws_ecs_task_definition" "orchestrator" {
  family                   = "dia-orchestrator"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  
  container_definitions = jsonencode([{
    name  = "orchestrator"
    image = "${aws_ecr_repository.dia.repository_url}:orchestrator-latest"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      {
        name  = "SNOWFLAKE_ACCOUNT"
        value = var.snowflake_account
      }
    ]
    
    secrets = [
      {
        name      = "SNOWFLAKE_USER"
        valueFrom = aws_secretsmanager_secret.snowflake.arn
      }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/dia-orchestrator"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ECS Service
resource "aws_ecs_service" "orchestrator" {
  name            = "dia-orchestrator"
  cluster         = aws_ecs_cluster.dia.id
  task_definition = aws_ecs_task_definition.orchestrator.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.orchestrator.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.orchestrator.arn
    container_name   = "orchestrator"
    container_port   = 8000
  }
}

# Application Load Balancer
resource "aws_lb" "dia" {
  name               = "dia-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids
}
```

### Deploy to AWS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker build -t dia-orchestrator ./orchestrator
docker tag dia-orchestrator:latest <ecr-url>/dia-orchestrator:latest
docker push <ecr-url>/dia-orchestrator:latest

# Deploy via Terraform
terraform apply
```

---

## Option 3: Azure Container Instances

```bash
# Create resource group
az group create --name dia-rg --location eastus

# Create container registry
az acr create --resource-group dia-rg --name diaregistry --sku Basic

# Push images
az acr login --name diaregistry
docker tag dia-orchestrator diaregistry.azurecr.io/orchestrator:v1
docker push diaregistry.azurecr.io/orchestrator:v1

# Deploy container instances
az container create \
  --resource-group dia-rg \
  --name dia-orchestrator \
  --image diaregistry.azurecr.io/orchestrator:v1 \
  --cpu 2 \
  --memory 4 \
  --registry-login-server diaregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label dia-api \
  --ports 8000 \
  --environment-variables \
    SNOWFLAKE_ACCOUNT=<account> \
  --secure-environment-variables \
    SNOWFLAKE_PASSWORD=<password>
```

---

## Production Configuration

### Environment Variables

**File:** `.env.production`

```bash
# Snowflake
SNOWFLAKE_ACCOUNT=your-prod-account
SNOWFLAKE_USER=dia_prod_user
SNOWFLAKE_PASSWORD=<from-secrets-manager>
SNOWFLAKE_DATABASE=marketing_analytics_prod
SNOWFLAKE_WAREHOUSE=dia_prod_wh
SNOWFLAKE_ROLE=dia_prod_role

# API
API_ENV=production
LOG_LEVEL=INFO
WORKERS=4

# Security
ENABLE_AUTH=true
JWT_SECRET=<random-secret>
ALLOWED_ORIGINS=https://dia.yourdomain.com
```

### Production Dockerfile

**File:** `orchestrator/Dockerfile.prod`

```dockerfile
FROM python:3.11-slim

# Production optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Security: Run as non-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Monitoring & Observability

### Application Monitoring

```python
# Add to main.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
query_counter = Counter('dia_queries_total', 'Total queries')
query_duration = Histogram('dia_query_duration_seconds', 'Query duration')

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

@app.middleware("http")
async def add_metrics(request, call_next):
    with query_duration.time():
        response = await call_next(request)
    query_counter.inc()
    return response
```

### Logging

```python
import structlog

logger = structlog.get_logger()

@router.post("/query")
async def query(request: QueryRequest):
    logger.info("query_received", query=request.query, session_id=request.session_id)
    
    try:
        result = process_query(request)
        logger.info("query_success", execution_time=result.execution_time_ms)
        return result
    except Exception as e:
        logger.error("query_failed", error=str(e))
        raise
```

---

## Security Checklist

- [ ] Use secrets manager (AWS Secrets Manager, Azure Key Vault, Snowflake)
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication (JWT, OAuth)
- [ ] Set up RBAC (Role-Based Access Control)
- [ ] Enable audit logging
- [ ] Regular security scans (Snyk, Trivy)
- [ ] Network security (VPC, security groups, firewall rules)
- [ ] Rate limiting on API
- [ ] Input validation and sanitization

---

## Deployment Checklist

- [ ] All tests passing (unit, integration, evaluation)
- [ ] Production configuration reviewed
- [ ] Secrets configured
- [ ] Infrastructure provisioned
- [ ] Images built and pushed
- [ ] Services deployed
- [ ] Health checks passing
- [ ] Monitoring dashboards set up
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Runbook created

---

## Rollback Plan

```bash
# Snowpark Container Services
ALTER SERVICE dia_orchestrator 
  FROM SPECIFICATION USING '@specs/dia_orchestrator_v0.9.yaml';

# AWS ECS
aws ecs update-service \
  --cluster dia-cluster \
  --service dia-orchestrator \
  --task-definition dia-orchestrator:previous-revision

# Azure
az container create \
  --name dia-orchestrator \
  --image diaregistry.azurecr.io/orchestrator:v0.9
```

---

## Success Criteria

✅ Services deployed and accessible  
✅ Health checks passing  
✅ Monitoring and alerts working  
✅ Performance meets SLAs  
✅ Security hardening complete  

---

**Congratulations!** 🎉 DIA v2.0 is now in production!

**Estimated Time:** 3-5 days
