# VMI Project 3: Data Streaming with Airflow and Kafka

<div style="text-align: center; margin: 20px 0;">
  <h3>Event-Driven ETL Pipeline with Real-time Data Processing</h3>
  <p><strong>University:</strong> Universidad Politécnica de Yucatán</p>
  <p><strong>Course:</strong> Visual Modeling for Information - 9th Quarter</p>
  <p><strong>Student:</strong> Ariel Buenfil</p>
</div>

## Table of Contents

1. [Overview](#overview)
2. [Technologies & Versions](#technologies--versions)
3. [Project Architecture](#project-architecture)
4. [Project Organization](#project-organization)
5. [Services Description](#services-description)
6. [Installation & Setup](#installation--setup)
7. [Running the Project](#running-the-project)
8. [Data Pipelines](#data-pipelines)
9. [Web Dashboards](#web-dashboards)
10. [Troubleshooting](#troubleshooting)
11. [Project Status](#project-status)

---

## Overview

This project implements a **comprehensive event-driven ETL (Extract, Transform, Load) pipeline** that demonstrates modern data engineering practices. The system orchestrates multiple data pipelines using Apache Airflow, streams real-time events through Confluent Kafka, processes diverse data sources, and provides interactive web-based visualizations.

### Key Features
- 🚀 **Real-time Event Streaming**: Apache Kafka for event ingestion
- 📊 **Workflow Orchestration**: Apache Airflow for task scheduling and monitoring
- 🔄 **Multiple ETL Pipelines**: Urban sensors, transportation, and product event tracking
- 📈 **Interactive Dashboards**: Web-based visualizations with Bokeh
- 🐳 **Containerized Architecture**: Docker Compose for service orchestration
- 🗄️ **Data Persistence**: PostgreSQL for metadata and workflow state
- 📝 **Schema Management**: Confluent Schema Registry for data contracts

---

## Technologies & Versions

### Core Technologies
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Core runtime environment |
| Apache Airflow | 3.1.3 | Workflow orchestration & scheduling |
| Confluent Kafka | latest | Event streaming platform |
| PostgreSQL | 16 | Metadata database & state management |
| Flask | 3.1.2 | Web dashboard framework |
| Bokeh | 3.8.1 | Interactive visualization library |
| Pandas | 2.3.3 | Data manipulation & analysis |
| Docker | - | Container orchestration |
| Docker Compose | - | Multi-container orchestration |

### Python Libraries
```
apache-airflow==3.1.3
kafka-python==2.3.0
pandas==2.3.3
flask==3.1.2
bokeh==3.8.1
matplotlib==3.10.7
numpy==2.3.5
celery==5.5.3
```

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE NETWORK                   │
│                      (airflow-net)                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Kafka      │  │  Schema      │  │  Kafka       │       │
│  │  Broker      │→→│  Registry    │  │  Connect     │       │
│  │  (9092)      │  │  (8081)      │  │  (8083)      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         ↑                                                      │
│         │                                                      │
│  ┌──────────────────────────────────────────────────┐        │
│  │       AIRFLOW ORCHESTRATION LAYER               │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │        │
│  │  │Scheduler │  │ API      │  │ DAG          │  │        │
│  │  │          │  │ Server   │  │ Processor    │  │        │
│  │  └──────────┘  └──────────┘  └──────────────┘  │        │
│  │  ┌──────────────────────────────────────────┐  │        │
│  │  │  Triggerer   │  PostgreSQL   │  Redis    │  │        │
│  │  └──────────────────────────────────────────┘  │        │
│  └──────────────────────────────────────────────────┘        │
│         ↓                                                      │
│  ┌──────────────────────────────────────────────────┐        │
│  │       DATA PROCESSING LAYER (DAGs)              │        │
│  │  • Urban Sensors ELT (VMI_URBAN_SENSORS_ELT)   │        │
│  │  • Product Events ETL (VMI_PRODUCT_EVENTS_ETL) │        │
│  │  • Transportation ETL (VMI_001)                 │        │
│  └──────────────────────────────────────────────────┘        │
│         ↓                                                      │
│  ┌──────────────────────────────────────────────────┐        │
│  │       DATA STORAGE & VISUALIZATION LAYER        │        │
│  │  ┌──────────────────────────────────────────┐  │        │
│  │  │      Shared Data Volume (/data)          │  │        │
│  │  │  • Raw Data (raw/)                       │  │        │
│  │  │  • Processed Data (processed/)           │  │        │
│  │  │  • Analytics (analytics/)                │  │        │
│  │  └──────────────────────────────────────────┘  │        │
│  │                    ↓                            │        │
│  │  ┌──────────────────────────────────────────┐  │        │
│  │  │   Flask Web Dashboard (Port 5200)        │  │        │
│  │  │  • Transportation Dashboard               │  │        │
│  │  │  • Urban Sensors Dashboard               │  │        │
│  │  └──────────────────────────────────────────┘  │        │
│  └──────────────────────────────────────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Organization

### Directory Structure

```
U3_preview/
├── docker-compose.yml          # Multi-container orchestration configuration
├── Dockerfile                  # Web service container image
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── README.md                   # This file
│
├── airflow/                    # Apache Airflow configuration
│   ├── .env                    # Airflow-specific environment variables
│   ├── dags/                   # Directed Acyclic Graphs (workflow definitions)
│   │   ├── dag.py             # Base/legacy DAG
│   │   ├── urban_sensors_etl.py      # Urban sensors ETL pipeline
│   │   ├── product_events_dag.py     # Product events ETL pipeline
│   │   └── __pycache__/
│   ├── config/                 # Airflow configuration files
│   │   └── airflow.cfg        # Airflow configuration
│   ├── logs/                   # DAG execution logs
│   │   └── dag_id=*/          # Logs organized by DAG ID
│   └── plugins/                # Custom Airflow plugins
│       ├── utils/             # Utility functions
│       └── my_kafka/          # Kafka integration module
│
├── data/                       # Shared data volume
│   ├── raw/                   # Raw data from sources
│   │   └── urban_sensors_raw*.csv
│   │   └── events*.csv
│   ├── processed/             # Processed & transformed data
│   │   ├── urban_sensors_processed.csv
│   │   └── urban_sensors_processed_aggregated.csv
│   ├── processed_product/     # Product event processed data
│   │   ├── product_events_clean.csv
│   │   ├── product_events_clean_kpi_category.csv
│   │   └── product_events_clean_kpi_funnel.csv
│   ├── analytics/             # Aggregated analytics data
│   └── *.csv                  # Generated reports & exports
│
├── my_kafka/                   # Kafka producer/consumer modules
│   ├── .env                    # Kafka-specific environment variables
│   ├── producer/
│   │   ├── producer.py        # Event producer implementation
│   │   └── __pycache__/
│   └── consumer/
│       ├── consumer.py        # Event consumer implementation
│       └── __pycache__/
│
├── utils/                      # Shared utilities
│   ├── transformer.py         # Data transformation logic
│   ├── preprocessing.ipynb    # Data preprocessing notebook
│   └── __pycache__/
│
├── web/                        # Flask web dashboard application
│   ├── app.py                 # Main Flask application
│   ├── templates/             # HTML templates
│   │   ├── index.html         # Main landing page
│   │   ├── main.html          # Transportation dashboard
│   │   └── urban.html         # Urban sensors dashboard
│   └── static/                # Static assets
│       ├── css/               # Stylesheets
│       ├── js/                # JavaScript files
│       └── icons/             # Icon assets
│
└── docs/                       # Additional documentation (if any)
```

---

## Services Description

### 1. **Kafka (Confluent Kafka)**
**Container:** `kafka`  
**Port:** `9092` (internal), `29092` (external)

**Purpose:** Message broker for event streaming
- Handles real-time event ingestion from multiple sources
- Maintains event topics: `urban-sensors`, `product-events`, `transportation-stats`
- Auto-creates topics on first message
- Stores events with persistence

**Configuration:**
- Single broker setup (Kraft mode)
- 1 partition per topic
- Auto-cleanup policy

---

### 2. **Schema Registry**
**Container:** `schema-registry`  
**Port:** `8081`

**Purpose:** Data contract management
- Manages Avro schemas for event topics
- Ensures data consistency across producers and consumers
- Provides schema versioning

---

### 3. **Kafka Connect**
**Container:** `kafka-connect`  
**Port:** `8083`

**Purpose:** Data integration framework
- Connects Kafka to external systems
- Enables distributed data movement
- Ready for source/sink connector deployment

---

### 4. **PostgreSQL**
**Container:** `postgres`  
**Port:** `5432` (internal only)

**Purpose:** Metadata and workflow state management
- Stores Airflow DAG metadata and execution history
- Maintains task state and scheduling information
- Database credentials: `airflow:airflow`
- Database name: `airflow`

---

### 5. **Apache Airflow**
**Image:** `apache/airflow:3.1.3-python3.11`

#### 5.1 **Airflow API Server**
**Container:** `airflow-apiserver`  
**Port:** `8080`

**Purpose:** REST API for workflow management
- Provides programmatic access to DAGs and task instances
- Enables external monitoring and triggering
- Required for scheduler operations

#### 5.2 **Airflow Scheduler**
**Container:** `airflow-scheduler`

**Purpose:** Workflow orchestration engine
- Schedules DAG runs according to defined schedules
- Manages task dependencies and execution order
- Monitors task health and retries

#### 5.3 **Airflow DAG Processor**
**Container:** `airflow-dag-processor`

**Purpose:** DAG parsing and validation
- Parses DAG files from the `dags/` directory
- Validates DAG structure and dependencies
- Updates DAG metadata in PostgreSQL

#### 5.4 **Airflow Triggerer**
**Container:** `airflow-triggerer`

**Purpose:** Async event trigger management
- Manages asynchronous task triggers
- Handles deferred task execution
- Reduces resource consumption for waiting tasks

#### 5.5 **Airflow Initialization**
**Container:** `airflow-init` (runs once)

**Purpose:** Initial setup and configuration
- Creates necessary directories
- Sets up default users and connections
- Initializes the Airflow database

---

### 6. **Flask Web Dashboard**
**Container:** `web-dashboard`  
**Port:** `5200`

**Purpose:** Interactive data visualization
- Displays real-time analytics and KPIs
- Provides multiple dashboard views
- Reads processed data from shared volume

**Features:**
- **Transportation Dashboard** (`/dashboard`): 
  - Total revenue KPI
  - Daily passenger trends (time series)
  - Top 5 busiest boarding areas

- **Urban Sensors Dashboard** (`/urban`):
  - Average pollution index KPI
  - Traffic vs. pollution correlation scatter plot
  - Noise pollution by zone bar chart
  - AI-generated insights

- **Home Page** (`/`): Project overview and navigation

**Technology Stack:**
- Flask 3.1.2 (Python web framework)
- Bokeh 3.8.1 (interactive visualization library)
- Pandas (data manipulation)

---

## Installation & Setup

### Prerequisites

**System Requirements:**
- Docker & Docker Compose installed
- 4GB+ RAM available
- 10GB+ disk space
- Windows, macOS, or Linux

**Required Files:**
- `.env` file with Mockaroo API key (optional)
- All configuration files (included in repo)

### Step 1: Clone/Prepare the Project

```bash
cd /path/to/U3_preview
```

### Step 2: Configure Environment Variables

Create or update `.env` file in the project root:

```env
# Airflow Configuration
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
_PIP_ADDITIONAL_REQUIREMENTS=kafka-python==2.3.0

# Mockaroo API (optional - for data generation)
MOCKAROO_API=your_api_key_here
```

Create `airflow/.env`:

```env
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
```

### Step 3: Verify Docker Installation

```bash
docker --version
docker compose --version
```

---

## Running the Project

### Start All Services

```bash
# Navigate to project directory
cd /path/to/U3_preview

# Start all containers in detached mode
docker compose up -d

# Check service status
docker compose ps
```

**Expected Output:**
```
NAME                  COMMAND                  SERVICE             STATUS
kafka                 "/etc/confluent/d..."   kafka               Up (healthy)
schema-registry       "/etc/confluent/d..."   schema-registry     Up (healthy)
kafka-connect         "/etc/confluent/d..."   kafka-connect       Up (healthy)
postgres              "docker-entrypoint..."  postgres            Up (healthy)
airflow-apiserver     "airflow api-server"    airflow-apiserver   Up (healthy)
airflow-scheduler     "airflow scheduler"     airflow-scheduler   Up (healthy)
airflow-dag-processor "airflow dag-processor" airflow-dag-processor Up
airflow-triggerer     "airflow triggerer"     airflow-triggerer   Up
web-dashboard         "bash -c 'pip inst..."  web                 Up
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | airflow / airflow |
| Airflow API | http://localhost:8080/api/v1 | Basic auth |
| Schema Registry | http://localhost:8081 | No auth |
| Kafka (local) | localhost:29092 | No auth |
| Web Dashboard | http://localhost:5200 | No auth |

### Stop All Services

```bash
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f airflow-scheduler

# Web service
docker compose logs -f web-dashboard
```

### Remove All Data and Start Fresh

```bash
docker compose down -v
docker system prune -a
docker compose up -d
```

---

## Data Pipelines

### Pipeline 1: Urban Sensors ETL

**DAG ID:** `VMI_URBAN_SENSORS_ETL`  
**Schedule:** `@hourly` (every hour)  
**Owner:** Ariel  
**Status:** ✅ Operational

**Pipeline Stages:**
1. **Extract**: Produces mock urban sensor events to Kafka topic `urban-sensors`
2. **Consume**: Reads events from Kafka using KafkaConsumer
3. **Transform**: Processes sensor data using `UrbanSensorTransformer`
   - Aggregates readings by location and time
   - Calculates pollution indices
   - Computes noise levels
4. **Load**: Writes processed data to `data/processed/urban_sensors_processed.csv`

**Input:** Mock urban sensor data (vehicle count, noise, pollution)  
**Output:** Aggregated sensor statistics

---

### Pipeline 2: Product Events ETL

**DAG ID:** `VMI_PRODUCT_EVENTS_ETL`  
**Schedule:** `@hourly` (every hour)  
**Owner:** Student  
**Status:** ✅ Operational

**Pipeline Stages:**
1. **Extract**: Generates simulated e-commerce product events
2. **Consume**: Reads events from Kafka topic `product-events`
3. **Transform**: Applies `ProductEventTransformer`
   - Classifies user actions (view, add to cart, purchase)
   - Builds user journey funnels
   - Calculates category KPIs
4. **Load**: Produces three output files:
   - `product_events_clean.csv` - Cleaned raw events
   - `product_events_clean_kpi_category.csv` - Category-level KPIs
   - `product_events_clean_kpi_funnel.csv` - Funnel conversion metrics

**Input:** Mock e-commerce event stream  
**Output:** Clean events + KPI aggregations

---

### Pipeline 3: Transportation/Product Events ETL

**DAG ID:** `VMI_001`  
**Schedule:** Manual trigger  
**Status:** ✅ Operational

**Features:**
- Generates transportation events via Mockaroo API
- Produces events to Kafka
- Consumes and processes transportation data
- Exports processed data to CSV

---

## Web Dashboards

### Dashboard Access

Navigate to `http://localhost:5200` to access the web dashboards.

### Transportation Dashboard (`/dashboard`)

**Data Source:** `data/processed_big.csv`

**Visualizations:**

1. **KPI: Total Revenue**
   - Calculates sum of all fare amounts in MXN
   - Displayed prominently at the top

2. **Daily Passenger Trends** (Line Chart)
   - Shows passenger count by transaction date
   - Interactive hover tooltips
   - X-axis: Transaction date
   - Y-axis: Passenger count

3. **Top 5 Busiest Boarding Areas** (Bar Chart)
   - Ranks boarding areas by trip frequency
   - Color-coded bars (Spectral5 palette)
   - Interactive tooltips with trip counts

**Technology:** Bokeh interactive charts with hover tools and zoom

---

### Urban Sensors Dashboard (`/urban`)

**Data Source:** `data/processed/urban_sensors_processed.csv`

**Visualizations:**

1. **KPI: Average Pollution Index (AQI)**
   - Displays average air quality index
   - Indicates environmental health

2. **Traffic vs. Pollution Impact** (Scatter Plot)
   - X-axis: Vehicle count per hour
   - Y-axis: Pollution index
   - Points colored by location/zone
   - Shows correlation between traffic and air quality
   - Interactive legend by zone

3. **Noise Pollution by Zone** (Bar Chart)
   - Ranks zones by average noise levels (dB)
   - Identifies high-noise areas
   - Consistent color coding with scatter plot

4. **AI-Generated Insights**
   - Identifies loudest zone
   - Analyzes traffic-air quality correlation
   - Provides actionable observations

**Technology:** Bokeh with grouped legends and multi-series visualization

---

### Home Page (`/`)

- Project overview
- Navigation links to dashboards
- Project metadata

---

## Troubleshooting

### Issue: Containers fail to start

**Solution:**
```bash
# Check logs
docker compose logs

# Verify Docker daemon is running
docker ps

# Restart Docker service
# (Platform-specific instructions)
```

### Issue: Airflow UI not accessible (localhost:8080)

**Solution:**
```bash
# Check if service is healthy
docker compose ps airflow-apiserver

# View API server logs
docker compose logs airflow-apiserver

# Restart the service
docker compose restart airflow-apiserver
```

### Issue: Web dashboard shows "Error: Could not load data"

**Solution:**
```bash
# Verify data files exist
ls -la data/processed*

# Check web container logs
docker compose logs web-dashboard

# Ensure data volume is mounted correctly
docker exec web-dashboard ls -la /web/../data

# Trigger a DAG run to generate data
# Visit http://localhost:8080, unpause a DAG, click "Trigger DAG"
```

### Issue: Kafka topics not created

**Solution:**
```bash
# Check Kafka health
docker compose logs kafka | grep -i healthy

# Manually create topics
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic urban-sensors \
  --partitions 1 \
  --replication-factor 1
```

### Issue: PostgreSQL connection refused

**Solution:**
```bash
# Check if Postgres is healthy
docker compose ps postgres

# View Postgres logs
docker compose logs postgres

# Verify credentials in environment
docker compose exec postgres psql -U airflow -d airflow -c "\dt"
```

### Issue: DAG not appearing in Airflow UI

**Solution:**
```bash
# Verify DAG file syntax
python -m py_compile airflow/dags/your_dag.py

# Check DAG processor logs
docker compose logs airflow-dag-processor

# Restart DAG processor
docker compose restart airflow-dag-processor
```

### Issue: Out of memory or disk space

**Solution:**
```bash
# Clean up Docker system
docker system prune -a

# Remove unused volumes
docker volume prune

# Clear Airflow logs (backup first!)
rm -rf airflow/logs/*

# Monitor disk usage
docker compose logs | tail -100
```

---

## Project Status

### ✅ Completed Features
- [x] Kafka infrastructure setup with Confluent Platform
- [x] Apache Airflow orchestration layer
- [x] Urban Sensors ETL pipeline
- [x] Product Events ETL pipeline
- [x] Transportation ETL pipeline
- [x] Data transformation and aggregation logic
- [x] Flask web dashboard with interactive visualizations
- [x] PostgreSQL metadata storage
- [x] Docker Compose multi-container orchestration
- [x] Web service integration with data volume sharing
- [x] Health checks for all services
- [x] Comprehensive logging and monitoring

### 📝 Current Implementation
- Real-time event streaming using Kafka
- Hourly scheduled ETL processes
- Mock data generation via Mockaroo API
- Interactive Bokeh visualizations
- Multiple dashboard views
- Schema management via Schema Registry

### 🚀 Future Enhancements
- [ ] Real-time dashboard updates (WebSockets)
- [ ] Advanced analytics (machine learning models)
- [ ] Data quality checks and validation
- [ ] Extended retention policies
- [ ] Alert/notification system
- [ ] API layer for programmatic data access
- [ ] Time-series database (InfluxDB/TimescaleDB) integration
- [ ] Advanced security (SSL/TLS, RBAC)

### 📊 Data Volumes
- **Raw Data:** ~1-5 KB per event × event frequency
- **Processed Data:** ~250 KB to 1 MB per pipeline run
- **Airflow Logs:** ~1-2 MB per DAG execution
- **Total Storage:** ~1-2 GB (including Docker images)

---

## Performance Considerations

### Resource Allocation
- **CPU:** Minimum 2 cores recommended
- **RAM:** 4GB minimum (6GB+ recommended)
- **Storage:** 10GB for all containers and data

### Optimization Tips
1. Reduce Kafka retention policy for old messages
2. Archive old Airflow logs regularly
3. Use LocalExecutor for small-scale deployments
4. Implement data compression in Kafka topics
5. Monitor container memory usage regularly

---

## Developer Quick Reference

### Common Commands

```bash
# Start services
docker compose up -d

# View all running containers
docker compose ps

# View service logs
docker compose logs -f <service_name>

# Execute command in container
docker exec <container_name> <command>

# Trigger a DAG manually
docker exec airflow-apiserver airflow dags trigger <dag_id>

# List all DAGs
docker exec airflow-apiserver airflow dags list

# Stop all services
docker compose down

# Remove all services and volumes
docker compose down -v
```

### Environment Variables

Key variables in `.env`:
- `AIRFLOW_UID`: User ID for file permissions
- `MOCKAROO_API`: API key for mock data generation
- `_AIRFLOW_WWW_USER_PASSWORD`: Airflow UI password

### File Locations

- **DAGs:** `airflow/dags/`
- **Logs:** `airflow/logs/`
- **Data:** `data/`
- **Configuration:** `airflow/config/airflow.cfg`
- **Kafka Plugins:** `airflow/plugins/my_kafka/`
- **Web Templates:** `web/templates/`

---

## References

- [Apache Airflow Documentation](https://airflow.apache.org/)
- [Confluent Kafka Documentation](https://docs.confluent.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bokeh Documentation](https://docs.bokeh.org/)

---

## License & Attribution

Author: [Ariel-Buenfil](https://github.com/Areo-17)

---

**Last Updated:** December 6, 2025  
**Project Status:** Active Development  
**Version:** 1.0