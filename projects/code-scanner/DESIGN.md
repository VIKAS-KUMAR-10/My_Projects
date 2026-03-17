# codeScanner: Design Specification 🛡️

## Overview
**codeScanner** is a language-agnostic Software Supply Chain Security tool designed for security analysts and researchers. It identifies vulnerable third-party components, analyzes dependency exposure, and reduces false positives using lightweight reachability heuristics.

Unlike DevSecOps automation tools, **codeScanner** is positioned as a **Security & Risk Analysis Utility**, focusing on deep visibility into the actual risk surface introduced by dependencies.

## Core Philosophy
- **Risk Visibility**: Answer exactly which components exist and which ones are exploitable.
- **Noise Reduction**: Use heuristics to separate "theoretical" vulnerabilities from "reachable" ones.
- **Language Agnostic**: Dynamically detect ecosystems and apply relevant analysis.
- **Professional Aesthetic**: Clean, high-signal reporting designed for security context.

---

## 1. Architectural Components

### A. Ecosystem Detector (Fingerprinting)
The first stage of analysis. It identifies the target project's primary ecosystems by searching for marker files:
- **Python**: `requirements.txt`, `pyproject.toml`, `setup.py`
- **Node.js**: `package.json`
- **Java**: `pom.xml`, `build.gradle`
- **Go**: `go.mod`
- **Rust**: `Cargo.toml`
- **PHP**: `composer.json`
- **.NET**: `*.csproj`, `*.sln`

### B. Dependency Enumeration (SBOM)
Conceptually integrates SBOM generation to create a complete dependency inventory.
- **Tooling**: Uses `Syft` (or equivalent logic) to generate a CycloneDX JSON SBOM.
- **Perspective**: The SBOM is treated as a **Software Asset Visibility Artifact**, providing a snapshot of the attack surface.

### C. Vulnerability Intelligence
Maps detected components against global vulnerability databases.
- **Tooling**: Uses `Trivy` for high-fidelity CVE mapping.
- **Focus**: Extracts CVE IDs, EPSS scores (if available), severity, and affected versions.
- **Framing**: This stage is defined as **Threat & Exposure Detection**.

### D. Reachability Heuristics Engine
The "Intelligence Layer" that evaluates if a vulnerable package is actually "Reachable" (likely used in source code).
- **Heuristic Strategy**: Lightweight regex-based or string-pattern matching for imports/references.
- **Classification**:
    - **Reachable / Likely Relevant**: Components explicitly imported or referenced in source files.
    - **Possibly Unused / Noise**: Components present in the supply chain but with no detected footprint in the source.

### E. Risk-Focused Reporting
Constructs a professional security analysis report.
- **Signal-to-Noise**: Clearly highlights high-risk findings while muting theoretical noise.
- **Security Metrics**: Prioritization improvement percentage and attack surface metrics.

---

## 2. Security Data Flow

Target Codebase
  ↓
[ Fingerprinting ] -> Identify Language Ecosystems
  ↓
[ Enumeration ]   -> Generate CycloneDX SBOM
  ↓
[ Mapping ]       -> Enrich with CVEs and Threat Intel
  ↓
[ Heuristics ]    -> Apply Reachability Analysis
  ↓
[ Risk Findings ] -> Generate Professional Security Report

---

## 3. CLI Interaction Model

### Commands
- `codescanner scan <path>`: Run the full multi-stage security analysis.
- `codescanner analyze <package>`: Deep dive into a specific component's risk footprint.
- `codescanner export`: Export findings in CycloneDX or JSON format.

### Analysis Experience
The tool provides real-time feedback using a professional "Security Analysis" tone:
`[+] Identifying project ecosystem...`
`[+] Enumerating software components...`
`[+] Mapping vulnerability intelligence...`
`[+] Evaluating reachability heuristics...`

---

## 4. Visual Philosophy
The tool avoids "hacker" tropes (neon greens, matrix effects). Instead, it uses:
- **Muted Grays/Slates**: For background and noise.
- **Status Colors**: Clear Emerald for reachable risks, Orange for high severity, Red for critical threat.
- **Typography**: Clean, monospace-focused structure for readability.

---

## 5. Extensibility
- **Plugins**: Interface for adding custom language analyzers (e.g., Ruby, Swift).
- **Feeds**: Support for private vulnerability databases or OSV.dev.
- **Scoring**: Future integration of CVSS combined with reachability-weighted risk scores.
