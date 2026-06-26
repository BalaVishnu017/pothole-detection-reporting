# Contributing to InfraVision AI

Thank you for considering contributing to **InfraVision AI**! 🚧

We welcome bug reports, feature requests, documentation improvements, and code contributions.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branch Naming Convention](#branch-naming-convention)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Running Tests](#running-tests)
- [Pull Request Guidelines](#pull-request-guidelines)

---

## Code of Conduct

Be respectful and constructive. This is an academic project — all contributors are expected to maintain a professional and collaborative tone.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/infravision-ai.git
   cd infravision-ai
   ```
3. Add the **upstream** remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/infravision-ai.git
   ```

---

## Development Setup

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install all dependencies (including dev tools)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

---

## Branch Naming Convention

| Type        | Format                          | Example                        |
|-------------|----------------------------------|--------------------------------|
| Feature     | `feature/<short-description>`   | `feature/admin-dashboard`      |
| Bug Fix     | `fix/<short-description>`       | `fix/email-attachment-error`   |
| Refactor    | `refactor/<short-description>`  | `refactor/detection-module`    |
| Docs        | `docs/<short-description>`      | `docs/update-readme`           |
| Test        | `test/<short-description>`      | `test/gps-service-coverage`    |

---

## Making Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes.
3. Write or update tests as needed.
4. Commit using a clear, conventional message:
   ```bash
   git commit -m "feat: add reverse geocoding to GPS service"
   ```

### Commit Message Format

```
<type>: <short summary>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

---

## Code Style

We use [Black](https://black.readthedocs.io/) for formatting and [isort](https://pycqa.github.io/isort/) for import ordering.

```bash
# Format code
black app/ config/ tests/ app.py --line-length=100

# Sort imports
isort app/ config/ tests/ app.py

# Lint
flake8 app/ config/ tests/ app.py --max-line-length=100
```

All docstrings should follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_detection.py -v
```

All tests must pass before submitting a PR.

---

## Pull Request Guidelines

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a **Pull Request** against `main` in the upstream repository.
3. Fill in the PR template:
   - **What** changes were made?
   - **Why** were they made?
   - **How** were they tested?
4. Ensure all **CI checks** pass (lint, tests, security scan).
5. Request a review from a maintainer.

---

## Reporting Bugs

Open a [GitHub Issue](../../issues/new) with:
- A clear title
- Steps to reproduce
- Expected vs actual behaviour
- Python version and OS

---

*Thank you for helping improve InfraVision AI! 🙏*
