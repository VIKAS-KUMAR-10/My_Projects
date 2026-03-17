# codeScanner 🛡️

**codeScanner** is a language-agnostic Software Supply Chain Security tool designed to identify vulnerable third-party components, analyze dependency exposure, and reduce false positives using reachability heuristics.

Positioned as a **Security & Risk Analysis Utility**, codeScanner provides deep visibility into the actual attack surface of a project, rather than just listing theoretical vulnerabilities.

---

## 🔒 Primary Security Objectives

**codeScanner** helps security analysts and researchers answer critical risk questions:
- **Visibility**: What third-party components exist in this software asset?
- **Exposure**: Which components contain known vulnerabilities (CVEs)?
- **Relevance**: Which vulnerabilities are realistically reachable from the source code?
- **Prioritization**: What is the actual risk-weighted attack surface?

---

## 🛠️ Functional Security Workflow

1. **Ecosystem Fingerprinting**: Dynamically detects project languages (**Python, Node.js, Ruby, Go, Java, Rust**).
2. **Component Enumeration**: Automatically parses dependency manifests like `package.json`, `requirements.txt`, and `Gemfile.lock`.
3. **Vulnerability Intelligence**: Maps components against the **OSV.dev (Google Open Source Vulnerability Database)** for high-fidelity CVE data.
4. **Reachability Analysis**: Applies language-specific heuristics to determine if vulnerable code is actually imported or referenced.
5. **Static Site Security**: Scans HTML files for insecure CDN links (jsDelivr, Unpkg).

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- Git

### Setup

#### 💻 Windows (Recommended)
```powershell
# 1. Clone the repository
git clone https://github.com/VIKAS-KUMAR-10/My_Projects.git

# 2. Navigate to the code-scanner project
cd My_Projects\code-scanner

# 3. Run the setup script (creates virtual environment & installs dependencies)
.\setup.ps1

# 4. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

#### 🍎 macOS / 🐧 Linux
```bash
# 1. Clone the repository
git clone https://github.com/VIKAS-KUMAR-10/My_Projects.git

# 2. Navigate to the code-scanner project
cd My_Projects/code-scanner

# 3. Run the setup script (creates virtual environment & installs dependencies)
chmod +x setup.sh && ./setup.sh

# 4. Activate the virtual environment
source .venv/bin/activate
```

#### 🛠️ Manual Setup (any OS)
```bash
cd My_Projects/code-scanner
pip install -e .
```

---

### Running a Scan
```bash
codescanner scan /path/to/your/project --severity HIGH
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

| Component | Description |
|-----------|-------------|
| **Ecosystem Detector** | Fingerprints projects based on marker files |
| **Dependency Parser** | Native parsers for `npm`, `PyPI`, and `RubyGems` |
| **Reachability Engine** | Language-specific heuristic analysis (regex & string pattern) |
| **Intelligence Layer** | Direct integration with OSV.dev REST API |
| **Reporting Layer** | Professional, high-signal CLI experience via Rich |

---

## 🤝 Contributing

Designed for extensibility. See [`DESIGN.md`](./DESIGN.md) for information on adding new language analyzers or integration feeds.
