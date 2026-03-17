import os
import re
import json
import requests
from typing import List, Dict, Set, Optional
from pydantic import BaseModel
from enum import Enum

class Ecosystem(str, Enum):
    PYTHON = "Python"
    NODEJS = "Node.js"
    JAVA = "Java"
    GO = "Go"
    RUST = "Rust"
    PHP = "PHP"
    DOTNET = ".NET"
    RUBY = "Ruby"
    UNKNOWN = "Unknown"

class Vulnerability(BaseModel):
    id: str
    package: str
    version: str
    severity: str
    is_reachable: bool = False
    files_referenced: List[str] = []
    summary: Optional[str] = None
    vulnerable_functions: List[str] = [] # New: specific function names

class RiskFinding(BaseModel):
    type: str  # 'SECRET' or 'DANGER'
    severity: str
    file: str
    line: int
    content: str
    description: str

class ScanResult(BaseModel):
    ecosystems: List[Ecosystem] = []
    reachable: List[Vulnerability] = []
    noise: List[Vulnerability] = []
    findings: List[RiskFinding] = [] # New: Secrets & Patterns
    metrics: Dict[str, float] = {}

class ReachabilityEngine:
    def __init__(self, project_path: str):
        self.project_path = project_path
        
        # Ecosystem Detection Map (Marker Files)
        self.ecosystem_markers = {
            Ecosystem.PYTHON: ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            Ecosystem.NODEJS: ["package.json", "package-lock.json", "yarn.lock"],
            Ecosystem.JAVA: ["pom.xml", "build.gradle"],
            Ecosystem.GO: ["go.mod", "go.sum"],
            Ecosystem.RUST: ["Cargo.toml", "Cargo.lock"],
            Ecosystem.PHP: ["composer.json", "composer.lock"],
            Ecosystem.DOTNET: [".csproj", ".sln", "packages.config"],
            Ecosystem.RUBY: ["Gemfile", "Gemfile.lock", "Rakefile"],
            Ecosystem.NODEJS: ["package.json", "package-lock.json", "yarn.lock", "index.html"]
        }

        # Language-specific import patterns
        self.import_patterns = {
            Ecosystem.PYTHON: re.compile(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', re.MULTILINE),
            Ecosystem.NODEJS: re.compile(r'(?:import|from|require)\s*\(?[\'"](@?[a-zA-Z0-9\-_/]+)[\'"]', re.MULTILINE),
            Ecosystem.GO: re.compile(r'^\s*[\'"]([a-zA-Z0-9\.\-_/]+)[\'"]', re.MULTILINE),
            Ecosystem.JAVA: re.compile(r'^\s*import\s+([a-zA-Z0-9\._]+)', re.MULTILINE),
            Ecosystem.RUST: re.compile(r'^\s*(?:use|extern crate)\s+([a-zA-Z0-9_]+)', re.MULTILINE),
            Ecosystem.RUBY: re.compile(r'^\s*(?:require|load)\s+[\'"]([a-zA-Z0-9\-_/]+)[\'"]', re.MULTILINE),
            Ecosystem.PHP: re.compile(r'(?:require|include|use)\s+[\'"]?([a-zA-Z0-9\\_\-/]+)[\'"]?', re.IGNORECASE),
            Ecosystem.DOTNET: re.compile(r'using\s+([a-zA-Z0-9\._]+);', re.MULTILINE),
        }

        self.package_map = {
            "PyYAML": ["yaml"],
            "scikit-learn": ["sklearn"],
            "beautifulsoup4": ["bs4"],
            "python-dotenv": ["dotenv"],
            "django-rest-framework": ["rest_framework"],
        }
        
        # Reconnaissance Patterns (Secrets & Dangerous Sinks)
        self.recon_patterns = {
            "SECRET": {
                "AWS Key": r"AKIA[0-9A-Z]{16}",
                "Generic Secret": r"(?i)(password|secret|passwd|token|auth|api_key|private_key)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
                "JWT Token": r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[0-9A-Za-z-_]+",
                "Stripe Key": r"sk_live_[0-9a-zA-Z]{24}"
            },
            "DANGER": {
                "Command Injection Sink": r"(system|exec|spawn|shell_exec|subprocess\.run|popen)\(",
                "Code Evaluation": r"(eval|exec|Function)\(",
                "Insecure Web Sink": r"(\.innerHTML|dangerouslySetInnerHTML|document\.write)\(",
                "SSRF Potential": r"(axios|fetch|requests|urlopen)\(.*?\+.*?\)"
            }
        }

    def detect_ecosystems(self) -> List[Ecosystem]:
        detected = set()
        for root, _, files in os.walk(self.project_path):
            if "node_modules" in root or ".git" in root or "venv" in root:
                continue
            for file in files:
                for eco, markers in self.ecosystem_markers.items():
                    if any(file.endswith(m) if m.startswith(".") else file == m for m in markers):
                        detected.add(eco)
            if len(detected) > 3: break 
        return list(detected) if detected else [Ecosystem.UNKNOWN]

    def parse_dependencies(self) -> List[Dict[str, str]]:
        """Parses real dependencies from manifest files."""
        dependencies = []
        
        # Node.js
        pkg_json = os.path.join(self.project_path, "package.json")
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, 'r') as f:
                    data = json.load(f)
                    all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    for name, ver in all_deps.items():
                        dependencies.append({"package": name, "version": ver.lstrip("^~>=<"), "ecosystem": "npm"})
            except: pass

        # Python
        req_txt = os.path.join(self.project_path, "requirements.txt")
        if os.path.exists(req_txt):
            try:
                with open(req_txt, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = re.split(r'[=<>~!]', line)
                            dependencies.append({"package": parts[0], "version": parts[1] if len(parts)>1 else "0.0.0", "ecosystem": "PyPI"})
            except: pass
            
        # Ruby
        gemfile_lock = os.path.join(self.project_path, "Gemfile.lock")
        if os.path.exists(gemfile_lock):
            try:
                with open(gemfile_lock, 'r') as f:
                    in_specs = False
                    for line in f:
                        if line.strip() == "specs:":
                            in_specs = True
                            continue
                        if in_specs:
                            if not line.startswith("    "): # End of specs section
                                if line.strip() and not line.startswith("  "):
                                    in_specs = False
                                continue
                            
                            # Matches "    packagename (version)"
                            match = re.search(r"^\s{4}([a-zA-Z0-9\-_.]+) \(([0-9a-zA-Z\-_.]+)\)", line)
                            if match:
                                dependencies.append({
                                    "package": match.group(1), 
                                    "version": match.group(2), 
                                    "ecosystem": "RubyGems"
                                })
            except: pass
            
        # Java (Maven - pom.xml)
        pom_xml = os.path.join(self.project_path, "pom.xml")
        if os.path.exists(pom_xml):
            try:
                with open(pom_xml, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Basic regex extract for dependencies (group/artifact/version)
                    deps = re.findall(r'<dependency>[\s\S]*?<groupId>([\a-zA-Z0-9\._\-]+)</groupId>[\s\S]*?<artifactId>([a-zA-Z0-9\._\-]+)</artifactId>[\s\S]*?<version>([a-zA-Z0-9\._\-\s]+)</version>', content)
                    for group, artifact, ver in deps:
                        dependencies.append({
                            "package": f"{group}:{artifact}", 
                            "version": ver.strip(), 
                            "ecosystem": "Maven"
                        })
            except: pass

        # .NET (NuGet - .csproj)
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".csproj"):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extracts <PackageReference Include="Name" Version="1.2.3" />
                            deps = re.findall(r'<PackageReference\s+Include=["\']([a-zA-Z0-9\._\-]+)["\']\s+Version=["\']([a-zA-Z0-9\._\-]+)["\']', content)
                            for name, ver in deps:
                                dependencies.append({
                                    "package": name,
                                    "version": ver.strip(),
                                    "ecosystem": "NuGet"
                                })
                    except: pass
        
        # Ruby Fallback
        if not os.path.exists(gemfile_lock) and os.path.exists(os.path.join(self.project_path, "Gemfile")):
            # Fallback to Gemfile if lock doesn't exist
            try:
                with open(os.path.join(self.project_path, "Gemfile"), 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("gem "):
                            match = re.search(r"gem\s+['\"]([^'\"]+)['\"]", line)
                            if match:
                                dependencies.append({"package": match.group(1), "version": "0.0.0", "ecosystem": "RubyGems"})
            except: pass
            
        # PHP (Composer)
        composer_json = os.path.join(self.project_path, "composer.json")
        if os.path.exists(composer_json):
            try:
                with open(composer_json, 'r') as f:
                    data = json.load(f)
                    all_deps = {**data.get("require", {}), **data.get("require-dev", {})}
                    for name, ver in all_deps.items():
                        if name == "php": continue
                        dependencies.append({"package": name, "version": ver.lstrip("^~>=< "), "ecosystem": "Packagist"})
            except: pass
            
        # Static Web / HTML CDNs
        for root, _, files in os.walk(self.project_path):
            if "node_modules" in root or ".git" in root: continue
            for file in files:
                if file.endswith(".html"):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Match jsdelivr or unpkg CDN links
                            # Examples: https://cdn.jsdelivr.net/npm/chart.js
                            #          https://unpkg.com/lodash@4.17.21/lodash.min.js
                            cdn_matches = re.finditer(r'src=["\']https?://(?:cdn\.jsdelivr\.net/npm/|unpkg\.com/)([a-zA-Z0-9\-_.]+)(?:@([0-9a-zA-Z\-_.]+))?.*?["\']', content)
                            for m in cdn_matches:
                                pkg = m.group(1)
                                ver = m.group(2) if m.group(2) else "latest"
                                # Basic cleanup: chart.js -> chart.js
                                dependencies.append({
                                    "package": pkg,
                                    "version": ver if ver != "latest" else "0.0.0",
                                    "ecosystem": "npm"
                                })
                    except: pass

        return dependencies

    def fetch_vulnerabilities(self, dependencies: List[Dict[str, str]]) -> List[Vulnerability]:
        """Queries OSV.dev for real vulnerabilities."""
        vulnerabilities = []
        
        for dep in dependencies[:50]: # Increased limit for better coverage
            try:
                query = {
                    "version": dep["version"],
                    "package": {"name": dep["package"], "ecosystem": dep["ecosystem"]}
                }
                response = requests.post("https://api.osv.dev/v1/query", json=query, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "vulns" in data:
                        for v in data["vulns"]:
                            summary = v.get("summary", "")
                            description = v.get("details", "")
                            
                            # Heuristic: Extract function names like `merge()` or `_.unset`
                            # Look for backticked names or patterns with ()
                            symbols = set(re.findall(r'`([a-zA-Z0-9_\.$]+(?:(?:\(\))|))|`', summary + description))
                            # Clean symbols (remove empty or just quotes)
                            vulnerable_funcs = [s.strip("()`") for s in symbols if s and len(s) > 2]

                            vulnerabilities.append(Vulnerability(
                                id=v["id"],
                                package=dep["package"],
                                version=dep["version"],
                                severity="HIGH", 
                                summary=summary if summary else "No summary available",
                                vulnerable_functions=vulnerable_funcs
                            ))
                    else:
                        pass # No vulns found for this package/version
                else:
                    pass # Request failed
            except Exception as e:
                # print(f"Error querying OSV: {e}")
                pass
            
        return vulnerabilities

    def analyze_reachability(self, vulnerabilities: List[Vulnerability]) -> ScanResult:
        ecosystems = self.detect_ecosystems()
        
        source_extensions = {
            Ecosystem.PYTHON: [".py"],
            Ecosystem.NODEJS: [".js", ".jsx", ".ts", ".tsx", ".html"],
            Ecosystem.JAVA: [".java"],
            Ecosystem.GO: [".go"],
            Ecosystem.RUST: [".rs"],
            Ecosystem.RUBY: [".rb"],
            Ecosystem.PHP: [".php", ".php5", ".phtml"],
            Ecosystem.DOTNET: [".cs", ".aspx", ".cshtml"],
        }
        
        target_exts = []
        for eco in ecosystems:
            target_exts.extend(source_extensions.get(eco, []))
        
        if not target_exts:
            target_exts = [".py", ".js", ".go", ".java", ".html"]

        found_patterns: Set[str] = set()
        
        for root, _, files in os.walk(self.project_path):
            if "node_modules" in root or ".git" in root or "venv" in root:
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in target_exts):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Check for imports
                            for eco in ecosystems:
                                if eco in self.import_patterns:
                                    matches = self.import_patterns[eco].findall(content)
                                    found_patterns.update(matches)
                            
                            # Generic check for package names in quotes or as keywords
                            content_lower = content.lower()
                            found_patterns.update([v.package.lower() for v in vulnerabilities if v.package.lower() in content_lower])
                    except: continue

        result = ScanResult(ecosystems=ecosystems)
        for vuln in vulnerabilities:
            # Level 1: Is the package even imported?
            signatures = [vuln.package.lower(), vuln.package.lower().replace("-", "_")]
            if vuln.package in self.package_map:
                signatures.extend(self.package_map[vuln.package])
                
            package_imported = False
            files_found = []
            
            # Re-scan specifically for this vulnerability to find source files
            for root, _, files in os.walk(self.project_path):
                if "node_modules" in root or ".git" in root or "venv" in root:
                    continue
                for file in files:
                    if any(file.endswith(ext) for ext in target_exts):
                        f_path = os.path.join(root, file)
                        try:
                            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                
                                # Check package presence in THIS file
                                if any(sig in content for sig in signatures):
                                    package_imported = True
                                    
                                    # Level 2: Specific function check
                                    if not vuln.vulnerable_functions:
                                        if f_path not in files_found: files_found.append(f_path)
                                    else:
                                        if any(func.lower() in content for func in vuln.vulnerable_functions):
                                            if f_path not in files_found: files_found.append(f_path)
                        except: continue

            is_reachable = len(files_found) > 0
            vuln.is_reachable = is_reachable
            # Store relative paths for cleaner output
            vuln.files_referenced = [os.path.relpath(f, self.project_path) for f in files_found[:3]] # Limit to 3 files
            
            if is_reachable:
                result.reachable.append(vuln)
            else:
                result.noise.append(vuln)

        total = len(vulnerabilities)
        if total > 0:
            noise_count = len(result.noise)
            result.metrics = {
                "total": total,
                "reachable": len(result.reachable),
                "noise": noise_count,
                "reduction_pct": (noise_count / total) * 100
            }
        
        return result

    def deep_reconnaissance(self) -> List[RiskFinding]:
        """Scans for secrets and dangerous coding patterns."""
        findings = []
        target_exts = [".py", ".js", ".html", ".php", ".cs", ".java", ".env", ".yaml", ".yml", ".json"]
        
        for root, _, files in os.walk(self.project_path):
            if "node_modules" in root or ".git" in root or "venv" in root:
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in target_exts):
                    f_path = os.path.join(root, file)
                    try:
                        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                # Scan for Secrets
                                for name, pattern in self.recon_patterns["SECRET"].items():
                                    match = re.search(pattern, line)
                                    if match:
                                        findings.append(RiskFinding(
                                            type="SECRET",
                                            severity="CRITICAL",
                                            file=os.path.relpath(f_path, self.project_path),
                                            line=i,
                                            content=line.strip()[:50] + "...",
                                            description=f"Potential {name} detected"
                                        ))
                                
                                # Scan for Dangers
                                for name, pattern in self.recon_patterns["DANGER"].items():
                                    match = re.search(pattern, line)
                                    if match:
                                        findings.append(RiskFinding(
                                            type="DANGER",
                                            severity="MEDIUM",
                                            file=os.path.relpath(f_path, self.project_path),
                                            line=i,
                                            content=line.strip()[:50] + "...",
                                            description=name
                                        ))
                    except: continue
        return findings

