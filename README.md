# Enterprise Observability & Incident Response Dashboard

A production-grade cloud monitoring and observability solution designed to enforce proactive system visibility and automated incident response across multi-tier enterprise applications. Built entirely as Infrastructure as Code (IaC) using **AWS CDK (Python)**, this stack provisions a centralized monitoring infrastructure aligned with the **AWS Well-Architected Framework (Operational Excellence pillar)**.

## 🏗️ Architecture & Observability Overview

Instead of relying on static thresholds, this project implements a dynamic, modern Operations Dashboard that independent infrastructure stacks can feed metrics into.

*   **Centralized CloudWatch Dashboard:** A fully coded telemetry panel layout (`Enterprise-Core-Infrastructure-Status`) that structures infrastructure health widgets side-by-side for rapid cross-system diagnostics.
*   **AI-Powered Anomaly Detection:** Leverages AWS built-in machine learning algorithms (`AnomalyDetectionAlarm`) to monitor Amazon ECS Fargate CPU utilization. The alarm dynamically calculates normal behavior bands (3 standard deviations), mitigating alert fatigue by only triggering when real operational anomalies occur.
*   **Data Lake Pipeline Monitoring:** Monitors the ingestion layer from the streaming architecture, triggering immediate alarms on any `DeliveryToS3.Failure` events within the Kinesis Firehose streams [3.1].
*   **Automated Incident Routing:** Integrates directly with **Amazon SNS (Simple Notification Service)** to establish low-latency alert paths, delivering real-time cryptographic notifications to operations engineers via email subscriptions upon alarm states.

## 🚀 Tech Stack & Core Services
*   **Infrastructure as Code:** AWS CDK (Python)
*   **Observability Platform:** Amazon CloudWatch (Dashboards, Metrics, Alarms, Anomaly Detection)
*   **Incident Notification:** Amazon SNS (Simple Notification Service)
*   **CI/CD & DevSecOps:** GitHub Actions, OpenID Connect (OIDC) Federation [2.1]

---

## 🔒 FinOps & DevSecOps Best Practices

### 1. Cost-Optimized Telemetry (FinOps)
Monitoring can easily become a major hidden cloud expense. This infrastructure implements strict **Log Retention Policies** (`RetentionDays.ONE_WEEK`) on all logging layers, ensuring metrics are available for immediate operational review while automatically pruning old log chunks to maintain a near-zero cost overhead.

### 2. Zero-Trust Deployment via OIDC
The GitHub Actions workflow configuration enforces cryptographic **OIDC Federation** with AWS STS [2.1]. The runner assumes transient IAM roles using short-lived identity tokens tailored strictly to the deployment lifecycle, completely eliminating the need for hardcoded, static AWS Access Keys in the repository [2.1].

---

## 🛠️ Deployment & Local Setup

### Prerequisites
*   Python 3.11+
*   Node.js & AWS CDK CLI (`npm install -g aws-cdk`)
*   An active AWS account with OIDC trust configured for your GitHub repository [2.1]

### Manual Validation
1. Clone the repository and enter the project directory.
2. Activate your virtual environment and install requirements:
   ```bash
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate # Mac/Linux
   pip install -r requirements.txt
   ```
3. Synthesize the stack to check for valid Python CDK syntax and compile CloudFormation models:
   ```bash
   cdk synth
   ```

### Automated CI/CD Lifecycle
Pushing code changes directly to the `main` branch fires the automated GitHub Actions runner (`deploy.yml`). The process securely completes the AWS OIDC handshake, compiles your dashboard widgets, wires the statistical anomaly thresholds, and pushes the production stack live to the `eu-north-1` region [2.1].
