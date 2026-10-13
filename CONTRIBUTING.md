# Contributing to Baby LLM

Thank you for your interest in contributing to **Baby LLM**! We welcome bug fixes, documentation improvements, feature requests, and architectural enhancements.

---

## 🛠️ Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/webdev-hemant/baby-llm.git
   cd baby-llm
   ```

2. **Set Up Python Environment**
   Python 3.11+ is required. We recommend using `uv` for package management:
   ```bash
   uv venv --python 3.12 .venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. **Run the Test Suite**
   Ensure all unit and integration tests pass before making changes:
   ```bash
   pytest
   ```

---

## 📐 Guidelines for Contributions

### Code Style & Standards
- Follow standard Python **PEP 8** conventions.
- Provide descriptive type hints for all public functions and methods.
- Maintain existing docstrings and write clear docstrings for new modules and functions.
- Baby LLM is designed to be **100% self-contained and zero-daemon**. Do not introduce mandatory external cloud services, external background daemons, or telemetry.

### Architectural Rules
- **Fast-Path Latency Budget**: Any changes to `ContextAssembler` or the chat completion path must preserve the <30ms latency budget.
- **Bi-Temporal Graph & WAL**: Modifications to memories must record `valid_from` timestamps and non-blocking WAL writes.
- **Privacy & YMYL**: Do not weaken attribute-level encryption or decay protection for health/financial data.

### Submitting a Pull Request
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Commit your changes with conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`).
3. Run the complete test suite: `pytest`
4. Push your branch to GitHub and open a Pull Request against `main`.
5. Fill out the PR template completely.

---

## 💬 Community & Code of Conduct
Please note that all contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
