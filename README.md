<div align="center">

# 🚧 InfraVision AI

### AI-Powered Road Defect Detection & Automated Reporting System

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00BFFF?style=for-the-badge)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/infravision-ai/ci.yml?branch=main&style=for-the-badge&label=CI)](../../actions)
[![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/infravision-ai?style=for-the-badge)](../../issues)

<br/>

> **InfraVision AI** detects potholes in real time using YOLOv8, classifies their severity,
> and automatically files a GPS-tagged evidence report to road authorities — all from a
> single Streamlit web app.

<br/>

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [🏗️ Architecture](#️-architecture) · [📖 API Reference](#-module-reference) · [🧪 Testing](#-testing) · [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Module Reference](#-module-reference)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Severity Classification](#-severity-classification)
- [Technologies](#-technologies)
- [Team](#-team)
- [License](#-license)

---

## 🔍 Problem Statement

Road maintenance remains inefficient due to:

| Problem | Impact |
|---|---|
| Manual inspection methods | Slow, labor-intensive, expensive |
| Reactive systems | Damage detected only after incidents |
| No automation in reporting | Delays in authority response |
| Prohibitive hardware costs | LiDAR systems beyond budget of municipalities |

**InfraVision AI** solves this with a low-cost, AI-driven, fully automated pipeline that
detects, classifies, geo-tags, and reports road defects without human intervention.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **YOLOv8 Detection** | Real-time pothole detection with configurable confidence threshold |
| 📊 **Severity Classification** | 4-level system: Low / Medium / High / Critical |
| 📧 **HTML Email Reports** | Branded email with severity badge, GPS coords, and photo evidence |
| 🗺️ **GPS Geotagging** | Google Maps link for every detected defect |
| 🔐 **Secure Auth** | bcrypt password hashing, `.env`-based secrets — no hardcoded credentials |
| 🎨 **Premium Dark UI** | Glassmorphism theme with animations, custom fonts, and severity color-coding |
| 🧪 **Test Suite** | pytest with coverage across auth, detection, GPS, and email modules |
| 🚀 **GitHub Actions CI** | Lint → Test → Security scan on every push |
| 📁 **Modular Architecture** | Clean package structure — easy to extend and maintain |
| 📷 **Image & Video Modes** | Tab-based UI supporting both upload modes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         InfraVision AI                          │
├──────────────┬───────────────────────┬──────────────────────────┤
│  INPUT LAYER │   PROCESSING LAYER    │      OUTPUT LAYER        │
├──────────────┼───────────────────────┼──────────────────────────┤
│              │                       │                          │
│  📷 Image    │  ┌─────────────────┐  │  🖥️  Streamlit Dashboard │
│  🎥 Video    │  │  YOLOv8 Engine  │  │  📧 HTML Email Report    │
│  📡 GPS Log  │  │  (best.pt)      │  │  🗺️  Google Maps Link    │
│              │  └────────┬────────┘  │  🗃️  SQLite Database     │
│              │           │           │  📁 Evidence Archive     │
│              │  ┌────────▼────────┐  │                          │
│              │  │ Severity Engine │  │                          │
│              │  │ Low/Med/High/   │  │                          │
│              │  │ Critical        │  │                          │
│              │  └─────────────────┘  │                          │
└──────────────┴───────────────────────┴──────────────────────────┘
```

---

## 📂 Project Structure

```
infravision-ai/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions: lint → test → security
├── app/                        # Core application package
│   ├── __init__.py
│   ├── auth.py                 # bcrypt auth, session management
│   ├── database.py             # SQLite abstraction layer
│   ├── detection.py            # YOLOv8 detection + severity engine
│   ├── email_service.py        # HTML email reporting
│   ├── gps_service.py          # GPS utilities, Coordinates dataclass
│   └── ui_components.py        # Reusable Streamlit components
├── assets/
│   └── style.css               # Premium dark glassmorphism CSS
├── config/
│   └── settings.py             # Pydantic settings (reads .env)
├── data/                       # Runtime data (gitignored)
│   └── .gitkeep
├── models/                     # YOLO model weights (gitignored)
│   └── .gitkeep
├── outputs/                    # Detection evidence (gitignored)
│   └── .gitkeep
├── scripts/
│   └── generate_gps.py         # CLI tool to generate GPS route logs
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_detection.py
│   ├── test_email_service.py
│   └── test_gps_service.py
├── .env.example                # Template — copy to .env and fill in
├── .gitignore                  # Excludes secrets, binaries, outputs
├── app.py                      # Streamlit entrypoint
├── CONTRIBUTING.md
├── LICENSE                     # MIT
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- `pip` (Python package manager)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) generated

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/infravision-ai.git
cd infravision-ai
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the template
cp .env.example .env

# Open .env and fill in your credentials
# Required: SENDER_EMAIL, SENDER_PASSWORD, ROAD_DEPT_EMAIL
```

> **Important:** Never commit `.env` to Git. It is already excluded via `.gitignore`.

### 5. Download the YOLO Model

Place the trained `best.pt` file in the `models/` directory:

```bash
# Download from GitHub Releases (or Google Drive link — see project page)
# Then:
mv best.pt models/best.pt
```

### 6. Run the Application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501** 🎉

---

## ⚙️ Configuration

All configuration is managed via environment variables. Copy `.env.example` to `.env` and set:

| Variable | Description | Default |
|---|---|---|
| `SENDER_EMAIL` | Gmail address for sending reports | — |
| `SENDER_PASSWORD` | Gmail App Password (16 chars) | — |
| `ROAD_DEPT_EMAIL` | Recipient email for reports | — |
| `CONFIDENCE_THRESHOLD` | YOLO detection confidence | `0.5` |
| `CRITICAL_AREA_RATIO` | Area fraction to trigger email | `0.05` |
| `DATABASE_PATH` | SQLite file path | `data/users.db` |
| `DEFAULT_LATITUDE` | Fallback GPS latitude | `17.3913` |
| `DEFAULT_LONGITUDE` | Fallback GPS longitude | `78.3206` |

> 💡 Generate a Gmail App Password at: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## 📖 Usage

### Image Detection

1. Sign in or create an account
2. Select the **📸 Image Detection** tab
3. Upload a road image (JPG/PNG)
4. Click **Analyze Image**
5. View severity classification and annotated output
6. For High/Critical detections — an email report is automatically sent

### Video Detection

1. Select the **🎥 Video Detection** tab
2. Upload a road video (MP4/MOV)
3. Click **Analyze Video** — frames are processed in real time
4. The worst-case frame is extracted as evidence
5. Report is automatically filed for High/Critical severity

### Generate GPS Log

```bash
python scripts/generate_gps.py --points 1000 --speed 30 --output data/gps_log.csv
```

---

## 📦 Module Reference

### `app.detection`

```python
from app.detection import load_model, detect_image, detect_video, Severity

model = load_model("models/best.pt")
result = detect_image(model, image_array, confidence=0.5)
print(result.severity)      # Severity.CRITICAL
print(result.total_potholes) # 3
```

### `app.auth`

```python
from app.auth import hash_password, verify_password, signup, login

hashed = hash_password("MyPassword")
verify_password("MyPassword", hashed)  # True
```

### `app.email_service`

```python
from app.email_service import send_report
from app.gps_service import Coordinates
from app.detection import Severity

success, msg = send_report(
    evidence_path="outputs/evidence_frame.jpg",
    coordinates=Coordinates(17.3913, 78.3206),
    severity=Severity.CRITICAL,
    reported_by="user123",
)
```

### `app.gps_service`

```python
from app.gps_service import Coordinates, parse_coordinates

coords = Coordinates(17.3913, 78.3206)
print(coords.to_google_maps_url())  # Google Maps link
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific module
pytest tests/test_detection.py -v
```

### Test Coverage

| Module | Tests |
|---|---|
| `app/auth.py` | Password hashing, bcrypt verification, signup validation, duplicate check |
| `app/detection.py` | Severity thresholds, boundary conditions, multi-detection worst-case |
| `app/email_service.py` | HTML body content, mocked SMTP, auth errors, missing evidence |
| `app/gps_service.py` | Coordinate parsing, range validation, route summary |

---

## 🔄 CI/CD Pipeline

Every push to `main` or `develop` triggers a 3-job pipeline:

```
Push → Lint (flake8 + isort + black)
            ↓
       Test (Python 3.10, 3.11, 3.12)
            ↓
       Security Scan (bandit)
```

---

## 🎯 Severity Classification

| Level | Area Ratio | Colour | Action |
|---|---|---|---|
| ✅ **None** | 0% | Green | No action |
| 🟡 **Low** | < 3% | Yellow | Logged only |
| 🟠 **Medium** | 3–8% | Amber | Logged only |
| 🔴 **High** | 8–15% | Red | Email filed |
| 🚨 **Critical** | > 15% | Deep Red | Email filed (urgent) |

---

## 🛠️ Technologies

| Layer | Technology |
|---|---|
| **AI / CV** | YOLOv8 (Ultralytics), OpenCV, PyTorch |
| **Web Framework** | Streamlit |
| **Database** | SQLite (via `app/database.py`) |
| **Security** | bcrypt, python-dotenv, pydantic-settings |
| **Email** | smtplib (SMTP SSL, MIME multipart HTML) |
| **Testing** | pytest, pytest-mock, pytest-cov |
| **Linting** | flake8, black, isort |
| **CI/CD** | GitHub Actions |
| **Language** | Python 3.10+ |

---

## 👥 Team

| Name | Role |
|---|---|
| **Tanisha Mandal** | Project Lead & Backend Developer |
| **Dontha Bala Vishnu Vardhan Goud** | AI/ML Engineer |
| **Gottam Anish Reddy** | Frontend & Integration |

**Faculty Guide:** Mr. B. Srinivasulu

**Department:** CSE (AI and ML) — Vidya Jyothi Institute of Technology, Hyderabad

---

## 🔭 Future Scope

- [ ] Centralized municipal dashboard with analytics
- [ ] Mobile app integration for real-time reporting
- [ ] Fleet vehicle integration for crowdsourced data
- [ ] Edge device deployment (Raspberry Pi / Jetson Nano)
- [ ] Night-time & low-light detection enhancement
- [ ] REST API for third-party integrations

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ by the InfraVision AI Team — VJIT, Hyderabad

⭐ Star this repository if you found it helpful!

</div>
