# Apache Flink + Apache Iceberg ETL Demo

A modern data platform demonstrating real-time ETL capabilities with Apache Flink and Apache Iceberg. This project extends the [Flink SQL Demo](https://nightlies.apache.org/flink/flink-docs-master/docs/try-flink/table_api/) with advanced streaming analytics and data lake features.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Apache Flink](https://img.shields.io/badge/flink-1.20.0-brightgreen.svg)](https://flink.apache.org/)
[![Apache Kafka](https://img.shields.io/badge/kafka-3.9.0-black.svg)](https://kafka.apache.org/)
[![Apache Iceberg](https://img.shields.io/badge/iceberg-1.7.1-blue.svg)](https://iceberg.apache.org/)
[![Trino](https://img.shields.io/badge/trino-440-purple.svg)](https://trino.io/)
[![Nessie](https://img.shields.io/badge/nessie-0.99.0-orange.svg)](https://projectnessie.org/)

## Key Features

- Real-time transaction processing with Apache Kafka
- Stream analytics using Flink SQL
- Versioned data lake with Iceberg and Nessie
- SQL analytics via Trino
- Interactive Streamlit dashboards
- Multi-path architecture supporting both open-source and enterprise deployments

## System Requirements

- Docker Desktop 4.27.0+
- 16GB RAM minimum
- 50GB disk space
- 4+ CPU cores
- JDK 17
- Gradle 8.5+
- Python 3.11+

## Technology Stack

### Core Components
- Apache Flink 1.20.0
- Apache Kafka 3.9.0
- Apache Iceberg 1.7.1
- Project Nessie 0.99.0
- MinIO (S3 Compatible)
- Trino 440
- Streamlit

### Enterprise Integration
- Snowflake with Iceberg Tables

## Quick Start

1. Clone and build:
```bash
git clone https://github.com/yourusername/flink-polaris-etl-demo.git
cd flink-polaris-etl-demo
./gradlew clean installShadowDist
```

2. Start platform:
```bash
docker-compose up -d
```

3. Access services:
- Flink Dashboard: http://localhost:8082
- MinIO Console: http://localhost:9001
- Nessie API: http://localhost:19120
- Trino: http://localhost:8080
- Streamlit: http://localhost:8501

## Documentation

- [Docker Services Guide](./docs/docker-readme.md)
- [Development Guide](./docs/development.md)
- [Configuration Reference](./docs/configuration.md)

## License

Licensed under the Apache License, Version 2.0