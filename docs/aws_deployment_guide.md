# AWS Cloud Deployment & Infrastructure Blueprint — FinSight AI

This guide details how to deploy **FinSight AI** onto Amazon Web Services (AWS) using production-grade enterprise cloud architecture.

---

## 1. AWS Target Architecture Overview

```
                      +-------------------+
                      |   AWS Route 53    |
                      +---------+---------+
                                |
                      +---------v---------+
                      |   AWS CloudFront  |
                      +---------+---------+
                                |
                   +------------v------------+
                   | Application Load Balancer|
                   +------------+------------+
                                |
         +----------------------+----------------------+
         |                                             |
+--------v--------+                           +--------v--------+
| AWS ECS Fargate |                           | AWS ECS Fargate |
| (API Service)   |                           | (API Service)   |
| Availability A  |                           | Availability B  |
+--------+--------+                           +--------+--------+
         |                                             |
         +----------------------+----------------------+
                                |
                 +--------------+--------------+
                 |                             |
       +---------v--------+          +---------v--------+
       | Amazon RDS       |          | Amazon S3        |
       | (PostgreSQL Multi-AZ)       | (Data & Reports) |
       +------------------+          +------------------+
```

---

## 2. Step-by-Step AWS Provisioning Guide

### Step 1: Database Provisioning (Amazon RDS PostgreSQL)
```bash
aws rds create-db-instance \
  --db-instance-identifier finsight-db-prod \
  --db-instance-class db.t4g.medium \
  --engine postgres \
  --allocated-storage 50 \
  --master-username finsight_admin \
  --master-user-password "ComplexSecurePass2026!" \
  --multi-az \
  --publicly-accessible false
```

### Step 2: Storage Setup (Amazon S3)
```bash
aws s3api create-bucket --bucket finsight-reports-prod --region us-east-1
aws s3api put-bucket-encryption --bucket finsight-reports-prod --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
```

### Step 3: Container Registry (Amazon ECR) & Push
```bash
aws ecr create-repository --repository-name finsight-backend

# Authenticate & Push Docker Image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t finsight-backend -f docker/Dockerfile.backend .
docker tag finsight-backend:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/finsight-backend:latest
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/finsight-backend:latest
```

### Step 4: Serverless Container Deployment (AWS ECS Fargate)
1. Create an ECS Cluster: `aws ecs create-cluster --cluster-name finsight-cluster`
2. Register Task Definition with environment variables pointing to Amazon RDS and S3.
3. Deploy Fargate Service behind an Application Load Balancer with HTTPS (AWS ACM SSL certificate).

### Step 5: Monitoring & Alerting (AWS CloudWatch)
1. Configure CloudWatch Container Insights for memory/CPU alarms.
2. Set up CloudWatch Logs metric filter for high risk fraud alerts (`fraud_risk_score > 85.0`) to fire SNS email notifications to Security Operations.
