# D

This repository contains the U3 project and its checkpoints.

## Overview

This project's goal is to perform ETL and ELT processes by orchestrating each one with Apache Airflow, using Confluent Kafka as the event straming platform, where we handle how the data is extract it.

## Infrastructure

Docker is used to build all the necessary platforms.

## Considerations and project status

The project is currently under development. The Kafka and Airflow services run successfully, however, the DAG instance for the ETL process is experiencing issues. The ELT process has not been implemented yet.