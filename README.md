# 🔍 Data Quality Auditor

[![CI](https://github.com/Bestard15/data-quality-package/actions/workflows/ci.yml/badge.svg)](https://github.com/Bestard15/data-quality-package/actions)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![DVC](https://img.shields.io/badge/data--versioning-DVC-945DD6.svg?logo=dvc&logoColor=white)](https://dvc.org)

**A pip-installable Python CLI that automatically audits dataset quality and consistency.** Detects nulls, duplicates, and validates configurable business rules defined in YAML. Outputs structured CSV reports for integration with downstream data pipelines.

---

## ✨ Features

- **Automated Quality Metrics** — calculates null count/percentage and duplicate count/percentage per column
- **Configurable Business Rules** — define validation rules (not-null, uniqueness, numeric ranges, non-empty strings) in `rules.yml`
- **Structured CSV Reports** — outputs `quality_metrics.csv` and `business_rules.csv` for pipeline integration
- **Installable CLI** — `pip install .` and run `audit_data` from anywhere
- **CI/CD Pipeline** — automated testing via GitHub Actions on every push
- **Data Versioning** — dataset tracking with DVC (Data Version Control)
- **Docker Support** — containerized execution for reproducible environments

---

## 🏗️ Architecture

```
data-quality-package/
├── scripts/
│   └── audit.py              # Core auditing logic
├── templates/                 # Report templates
├── tests/                     # Unit tests
├── data/                      # Sample datasets (DVC-tracked)
├── .github/workflows/         # CI/CD pipeline
├── Dockerfile                 # Container setup
├── setup.py                   # Package configuration
├── rules.yml.dvc              # Business rules (DVC-tracked)
├── schema.yml.dvc             # Schema definition (DVC-tracked)
└── requirements.txt           # Dependencies
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Bestard15/data-quality-package.git
cd data-quality-package

# Install as a Python package
pip install .

# Or install in development mode
pip install -e .
```

### Usage

```bash
# Run the auditor on a CSV file
audit_data --input data/sample.csv --rules rules.yml

# Output reports will be generated in the current directory:
#   → quality_metrics.csv
#   → business_rules.csv
```

### Docker

```bash
# Build the image
docker build -t data-quality-auditor .

# Run the auditor
docker run -v $(pwd)/data:/app/data data-quality-auditor
```

---

## 📏 Business Rules (YAML)

Define custom validation rules in `rules.yml`:

```yaml
columns:
  customer_id:
    - not_null
    - unique
  age:
    - not_null
    - range: [0, 120]
  email:
    - not_null
    - non_empty_string
```

The auditor checks each rule and flags violations in the output report.

---

## 🧪 Testing

```bash
# Run the test suite
python -m pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.7+ |
| Config | PyYAML |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Data Versioning | DVC |
| Containerization | Docker |

---

## 📄 License

This project is open source and available for educational and professional use.

---

## 👤 Author

**Juan Bestard** — [LinkedIn](https://www.linkedin.com/in/juan-bestard-barrio-74ba60269) · [GitHub](https://github.com/Bestard15)

