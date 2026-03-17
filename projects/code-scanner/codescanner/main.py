import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from typing import Optional, List
from pathlib import Path

from codescanner.styles import THEME, BRAND_COLOR, SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR, NOISE_COLOR
from codescanner.engine import ReachabilityEngine, Vulnerability, Ecosystem

app = typer.Typer(
    help="codeScanner: Multi-language Supply Chain Security & Risk Analysis",
    no_args_is_help=True
)
console = Console(theme=THEME)

@app.callback()
def main():
    pass

@app.command("scan")
def scan_command(
    path: Path = typer.Argument(..., help="Path to the target directory for risk analysis"),
    severity: str = typer.Option("HIGH", help="Filter by minimum severity (LOW, MEDIUM, HIGH, CRITICAL)")
):
    """
    Run a multi-stage security analysis to uncover reachable supply chain risks.
    """
    scan_logic(path, severity)

def scan_logic(path: Path, severity: str):
    console.print(Panel(
        f"[brand]codeScanner[/] [dim]v0.2.1 - Security & Risk Analysis Utility[/]\n"
        f"[dim]Project Target: {path.absolute()}[/]",
        border_style="brand",
        expand=False
    ))

    engine = ReachabilityEngine(str(path))
    
    with Progress(
        SpinnerColumn(style="brand"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        
        # Stage 1: Ecosystem Fingerprinting
        task1 = progress.add_task("Identifying project ecosystem...", total=1)
        ecosystems = engine.detect_ecosystems()
        progress.update(task1, advance=1)

        # Stage 2: Component Enumeration (SBOM)
        task2 = progress.add_task("Enumerating software components...", total=1)
        dependencies = engine.parse_dependencies()
        progress.update(task2, advance=1)

    # Stage 3: Vulnerability Intelligence Mapping
    task3 = progress.add_task("Mapping real vulnerability intelligence (OSV.dev)...", total=1)
    real_vulnerabilities = engine.fetch_vulnerabilities(dependencies)
    progress.update(task3, advance=1)

    # Stage 4: Reachability Analysis
    task4 = progress.add_task("Evaluating exploit relevance...", total=1)
    results = engine.analyze_reachability(real_vulnerabilities)
    progress.update(task4, advance=1)

    # Stage 5: Deep Reconnaissance
    task5 = progress.add_task("Performing Deep Reconnaissance (Secrets & Sinks)...", total=1)
    recon_findings = engine.deep_reconnaissance()
    progress.update(task5, advance=1)

    # --- REPORTING ---

    eco_str = ", ".join([e.value for e in ecosystems])
    console.print(f"[dim]Detected Ecosystems:[/] [brand]{eco_str}[/]")
    
    if dependencies:
        dep_names = ", ".join([d['package'] for d in dependencies[:5]])
        if len(dependencies) > 5:
            dep_names += f" and {len(dependencies)-5} others"
        console.print(f"[dim]Analyzed Supply Chain:[/] [white]{dep_names}[/]\n")

    if not real_vulnerabilities:
        console.print(Panel(
            "[success]✔[/] [bold white]Security Posture: Clean[/]\n"
            "[dim]No known vulnerabilities were found for the analyzed components in OSV.dev.[/]",
            border_style="success",
            expand=False
        ) if dependencies else "[warning]No components found to analyze.[/]")
        return

    # Reachable Table
    if results.reachable:
        console.print("[bold white]=== Reachable Vulnerabilities ===[/]")
        for v in results.reachable:
            sev_style = "bold red" if v.severity == "CRITICAL" else "orange1"
            console.print(f"[success]✔[/] [bold white]{v.package}[/] ({v.version}) ([{sev_style}]{v.severity}[/] / {v.id})")
            if v.summary:
                console.print(f"  [dim]↳ Summary: {v.summary}[/]")
            
            # Hacker Intelligence
            if v.vulnerable_functions:
                funcs = ", ".join([f"[error]{f}[/]" for f in v.vulnerable_functions[:5]])
                console.print(f"  [dim]↳ Target Symbols:[/] {funcs}")
            
            if v.files_referenced:
                paths = ", ".join([f"[cyan]{p}[/]" for p in v.files_referenced])
                console.print(f"  [dim]↳ Found in:[/] {paths}")
        console.print()

    # Recon Findings Table (Secrets & Dangers)
    if recon_findings:
        console.print("[bold red]=== Reconnaissance Findings (High Value Targets) ===[/]")
        for f in recon_findings:
            color = "bold red" if f.type == "SECRET" else "bold yellow"
            console.print(f"[{color}][!][/] [{color}]{f.type}[/] | {f.description}")
            console.print(f"    [dim]↳ Location :[/] [cyan]{f.file}:{f.line}[/]")
            console.print(f"    [dim]↳ Context  :[/] [white]{f.content}[/]")
        console.print()

    # Noise Table
    if results.noise:
        console.print("[dim]=== Lower-Confidence / Noise Findings ===[/]")
        for v in results.noise:
            console.print(f"[noise]✘[/] {v.package} ({v.version}) ({v.severity} / {v.id})")
        console.print()

    # Security Metrics
    if results.metrics:
        m = results.metrics
        metrics_panel = Panel(
            f"[bold white]Total Found[/]       : [brand]{m['total']}[/]\n"
            f"[bold white]Likely Reachable[/] : [error]{m['reachable']}[/]\n"
            f"[bold white]Noise Filtered[/]   : [noise]{m['noise']}[/]\n"
            f"-----------------------------------\n"
            f"[bold white]Prioritization Gain[/]: [success]{m['reduction_pct']:.1f}%[/]",
            title="=== Security Analysis Metrics ===",
            title_align="left",
            border_style="brand",
            expand=False,
            padding=(1, 2)
        )
        console.print(metrics_panel)


if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        import traceback
        console.print(f"[error]Fatal error:[/] {e}")
        console.print(traceback.format_exc())
