---
title: geospatial-data-converter
emoji: 🌎
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
tags: [geospatial, streamlit, docker]
---

# geospatial-data-converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/joshuasundance-swca/geospatial-data-converter)

[![Push to Docker Hub](https://github.com/joshuasundance-swca/geospatial-data-converter/actions/workflows/docker-hub.yml/badge.svg)](https://github.com/joshuasundance-swca/geospatial-data-converter/actions/workflows/docker-hub.yml)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/joshuasundance/geospatial-data-converter/latest)](https://hub.docker.com/r/joshuasundance/geospatial-data-converter)

[![Push to HuggingFace Space](https://github.com/joshuasundance-swca/geospatial-data-converter/actions/workflows/hf-space.yml/badge.svg)](https://github.com/joshuasundance-swca/geospatial-data-converter/actions/workflows/hf-space.yml)
[![Open HuggingFace Space](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/joshuasundance/geospatial-data-converter)

![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/joshuasundance-swca/geospatial-data-converter)
![Code Climate issues](https://img.shields.io/codeclimate/issues/joshuasundance-swca/geospatial-data-converter)
![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/joshuasundance-swca/geospatial-data-converter)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
![Known Vulnerabilities](https://snyk.io/test/github/joshuasundance-swca/geospatial-data-converter/badge.svg)

This project showcases a simple geospatial data converter using [Streamlit](https://streamlit.io) and [GeoPandas](https://geopandas.org/).

# Features
- User-friendly interface for easy data conversion
- Supports conversion from the following input formats:
  - ArcGIS featurelayer URL
  - Uploaded file: KML, KMZ, GeoJSON, ZIP, etc
- Provides data in the selected output format
- Presents data preview (geometry omitted for display purposes)
- Download button for the converted data

# Deployment
`geospatial-data-converter` is deployed as a [Docker image](https://hub.docker.com/r/<your-dockerhub-username>/geospatial-data-converter) based on the `python:3.11-slim-bookworm` image.

## With Docker (pull from Docker Hub)
1. Run in terminal:
`docker run -p 7860:7860 <your-dockerhub-username>/geospatial-data-converter:latest`
2. Open http://localhost:8501 in your browser

## Docker Compose (build locally)
1. Clone the repo. Navigate to cloned repo directory
2. Run in terminal: `docker compose up`
3. Open http://localhost:7860 in your browser

## Run Tests (with local Docker container)
1. Run in terminal: `docker compose run test`

## Kubernetes
1. Clone the repo. Navigate to cloned repo directory
2. Run bash script: `/bin/bash ./kubernetes/deploy.sh`
3. Get the IP address for your new service: `kubectl get service geospatial-data-converter`

# Links
- [Streamlit](https://streamlit.io)
- [GeoPandas](https://geopandas.org/)
- [Docker Hub](https://hub.docker.com/)
