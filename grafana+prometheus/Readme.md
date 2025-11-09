📊 Monitoring Project: Prometheus + Grafana + Exporters

This project provides a complete monitoring stack using Docker Compose, Prometheus, Grafana, and three exporters.
All dashboards are supplied as JSON files and can be imported directly into Grafana.

📁 Project Structure
├── grafana+prometheus/
│   ├── docker-compose.yml           # Main orchestration file
│   ├── custom_exporter.py           # Python-based exporter
│
├── config/
│   ├── prometheus.yml               # Prometheus job configuration
│
├── jsons/
│   ├── node_exporter.json           # Dashboard: System metrics
│   ├── database_exporter.json       # Dashboard: Database metrics
│   ├── custom_exporter.json         # Dashboard: Custom metrics

🧩 Technologies Used
Tool / Component	Purpose
Docker Compose	Run full monitoring stack
Grafana	Metrics visualization
Prometheus	Metrics storage & scraping
Node Exporter	System/resource monitoring
Database Exporter	Application DB monitoring
Custom Exporter (Python)	Custom app / business metrics
▶️ Quick Start

Requirement: Docker & Docker Compose must be installed

From inside the grafana+prometheus/ folder:

docker-compose up -d


Check running services:

docker ps

🌐 Service Access
Service	URL
Grafana UI	http://localhost:3000

Prometheus UI	http://localhost:9090

Node Exporter	http://localhost:9100/metrics

Custom Exporter	http://localhost:8000/metrics

Database exporter URL depends on your DB configuration

⚙️ Prometheus Configuration

Path: ./config/prometheus.yml

Example scrape targets included:

scrape_configs:
  - job_name: "node_exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "custom_exporter"
    static_configs:
      - targets: ["custom-exporter:8000"]

  - job_name: "database_exporter"
    static_configs:
      - targets: ["db-exporter:port"]


(Adjust db-exporter:port for your actual DB exporter)

📊 Dashboards Overview

All dashboards are stored in /jsons

File	Dashboard Purpose
node_exporter.json	CPU, RAM, Disk, Network — system-level monitoring
database_exporter.json	Performance, query metrics, DB health
custom_exporter.json	Project-specific business/application metrics
How to Import Dashboards in Grafana

1️⃣ Login: http://localhost:3000
2️⃣ Go to: Dashboards → Import
3️⃣ Upload a .json from /jsons
4️⃣ Select Prometheus data source ✅

🧹 Stop / Cleanup

Stop:

docker-compose down


Remove containers + volumes:

docker-compose down -v

✅ What This Project Demonstrates

✔ Infrastructure monitoring
✔ Application monitoring
✔ Custom metric tracking
✔ Fully automated deployment using Docker
✔ Grafana dashboards ready for evaluation / defense