# RG Storage

> **Part of the [ResonantGenesis](https://resonant.dev-swat.com) platform** — File storage and asset management service.

[![Status: Production](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()
[![Port: 8000](https://img.shields.io/badge/Port-8000-orange.svg)]()
[![License: RG Source Available](https://img.shields.io/badge/License-RG%20Source%20Available-blue.svg)](LICENSE.txt)

Handles file uploads, downloads, and asset management for the platform. Used by Rabbit for post images, by AST analysis for scan artifacts, and by other services for general file storage.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment Status

- **Extracted from**: `genesis2026_production_backend/storage_service/`
- **Server path**: `/home/deploy/RG_Storage`
- **Docker service**: `storage_service`

---
**Organization**: [DevSwat-ResonantGenesis](https://github.com/DevSwat-ResonantGenesis) | **Platform**: [resonant.dev-swat.com](https://resonant.dev-swat.com)
