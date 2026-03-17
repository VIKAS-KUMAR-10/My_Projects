# codeScanner 🛡️

**codeScanner** is a language-agnostic **Software Supply Chain Security** tool that identifies vulnerable third-party components, analyzes dependency exposure, and reduces false positives using reachability heuristics.

> Positioned as a **Security & Risk Analysis Utility**, codeScanner gives you deep visibility into your project's actual attack surface — not just a list of theoretical CVEs.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-Ecosystem Support** | Detects Python, Node.js, Ruby, Go, Java, and Rust projects automatically |
| 📦 **SBOM Generation** | Builds a Software Bill of Materials from your dependency manifests |
| 🗄️ **CVE Intelligence** | Queries the OSV.dev (Google) vulnerability database in real-time |
| 🎯 **Reachability Analysis** | Filters out noise — only flags vulnerabilities actually used in your code |
| 🔐 **Secret Detection** | Scans for hardcoded passwords, API keys, and JWT tokens in source files |
| 🌐 **Static Site Security** | Detects insecure 3rd-party CDN links in HTML files |
| 📊 **Risk Scoring** | Prioritizes findings by severity (CRITICAL, HIGH, MEDIUM, LOW) |
| ⚡ **Fast CLI** | Beautiful, readable terminal output powered by Rich |

---

## 🔒 Primary Security Objectives

- **Visibility** — What third-party components exist in this software asset?
- **Exposure** — Which components contain known vulnerabilities (CVEs)?
- **Relevance** — Which vulnerabilities are realistically reachable from the source code?
- **Prioritization** — What is the actual risk-weighted attack surface?

---

## 🧠 How It Works

```
Your Project
     │
     ▼
┌─────────────────────────────┐
│  1. Ecosystem Fingerprinting │  Detects languages from marker files
│     (package.json, Gemfile,  │  (requirements.txt, go.mod, Cargo.toml...)
│      requirements.txt, etc.) │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  2. SBOM Generation          │  Enumerates ALL dependencies and their
│     (Software Bill of        │  exact versions into a structured inventory
│      Materials)              │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  3. CVE Lookup               │  For each component in the SBOM, queries
│     (OSV.dev API)            │  the Google Open Source Vulnerability DB
│                              │  to find known CVEs (GHSA, CVE IDs)
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  4. Reachability Analysis    │  Checks if the vulnerable package is
│     (Noise Reduction)        │  actually IMPORTED or CALLED in your code
│                              │  using language-specific heuristics
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  5. Secret & Sink Detection  │  Scans source files for hardcoded secrets,
│     (Reconnaissance)         │  dangerous patterns, and insecure CDN links
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  6. Risk Report              │  Produces a prioritized, high-signal report
│     (CLI Output)             │  separating reachable vs noise findings
└─────────────────────────────┘
```

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- Git

---

### Option A — Clone only this tool (Recommended) ✅

You do **not** need to download the entire `My_Projects` repository.
Use **sparse checkout** to clone only the `code-scanner` folder:

#### 💻 Windows
```powershell
# Clone only the code-scanner folder
git clone --filter=blob:none --sparse https://github.com/VIKAS-KUMAR-10/My_Projects.git
cd My_Projects
git sparse-checkout set code-scanner
cd code-scanner

# Run setup
.\setup.ps1

# Activate environment
.\.venv\Scripts\Activate.ps1
```

#### 🍎 macOS / 🐧 Linux
```bash
# Clone only the code-scanner folder
git clone --filter=blob:none --sparse https://github.com/VIKAS-KUMAR-10/My_Projects.git
cd My_Projects
git sparse-checkout set code-scanner
cd code-scanner

# Run setup
chmod +x setup.sh && ./setup.sh

# Activate environment
source .venv/bin/activate
```

---

### Option B — Clone the entire repository
```bash
git clone https://github.com/VIKAS-KUMAR-10/My_Projects.git
cd My_Projects/code-scanner

# Windows
.\setup.ps1
.\.venv\Scripts\Activate.ps1

# macOS / Linux
./setup.sh && source .venv/bin/activate
```

---

### Option C — Manual Install (pip only)
```bash
cd code-scanner
pip install -e .
```

---

### Running a Scan
```bash
# Scan a project for vulnerabilities
codescanner scan /path/to/your/project

# Filter by severity
codescanner scan /path/to/your/project --severity HIGH

# Get help
codescanner --help
```

---

## 📊 Sample Output

```text
╭───────────────────────────────────────────────────────╮
│ codeScanner v0.2.1 - Security & Risk Analysis Utility │
│ Project Target: /home/user/my-project                │
╰───────────────────────────────────────────────────────╯
Detected Ecosystems: Node.js
Analyzed Supply Chain: lodash, express, ...

=== Reachable Vulnerabilities ===
✔ lodash (4.17.15) (HIGH / GHSA-29mw-wpgm-hmr9)
  ↳ Regular Expression Denial of Service (ReDoS) in lodash

=== Lower-Confidence / Noise Findings ===
✘ express (4.16.0) (MEDIUM / GHSA-xxxx-xxxx)

╭─ === Security Analysis Metrics === ───╮
│                                       │
│  Total Found       : 2                │
│  Likely Reachable  : 1                │
│  Noise Filtered    : 1                │
│  -----------------------------------  │
│  Prioritization Gain: 50.0%           │
│                                       │
╰───────────────────────────────────────╯
```

---

## 🏗️ Architecture

| Component | Role |
|-----------|------|
| **Ecosystem Detector** | Fingerprints project type from marker files |
| **Dependency Parser** | Extracts dependencies from `npm`, `PyPI`, `RubyGems` manifests |
| **SBOM Builder** | Constructs a structured Software Bill of Materials |
| **CVE Intelligence** | Queries OSV.dev REST API for vulnerability data |
| **Reachability Engine** | Applies regex & heuristic analysis to filter noise |
| **Recon Scanner** | Detects secrets and dangerous code patterns |
| **Reporting Layer** | Renders professional CLI output via the `Rich` library |

---

## 🤝 Contributing

Designed for extensibility. See [`DESIGN.md`](./DESIGN.md) for information on adding new language analyzers or integration feeds.
