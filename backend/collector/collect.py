"""Coleta métricas da VPS e envia um snapshot completo para a API."""

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import psutil


def docker_metrics():
    counts = {state: 0 for state in ("running", "stopped", "exited", "restarting")}
    problems = []
    if not shutil.which("docker"):
        return counts, problems
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            capture_output=True, text=True, timeout=8, check=True,
        )
        for line in result.stdout.splitlines():
            item = json.loads(line)
            raw_state = item.get("State", "").lower()
            state = raw_state if raw_state in counts else "stopped"
            counts[state] += 1
            if state in ("exited", "restarting"):
                problems.append({
                    "name": item.get("Names") or item.get("ID", "unknown"),
                    "state": state,
                    "detail": (item.get("Status") or raw_state)[:500],
                })
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"Docker indisponível: {type(exc).__name__}", file=sys.stderr)
    return counts, problems[:100]


def service_metrics():
    services = []
    try:
        definitions = json.loads(os.getenv("DASH_VPS_SERVICES_JSON", "[]"))
        if not isinstance(definitions, list) or len(definitions) > 100:
            raise ValueError("DASH_VPS_SERVICES_JSON deve ser uma lista com até 100 serviços")
        for item in definitions:
            name = item["name"]
            url = item["url"]
            if not isinstance(name, str) or not isinstance(url, str) or not url.startswith(("http://", "https://")):
                raise ValueError("serviço requer name e URL HTTP válidos")
            start = time.perf_counter()
            try:
                with urlopen(Request(url, method="GET"), timeout=5) as response:
                    online = 200 <= response.status < 400
                latency = round((time.perf_counter() - start) * 1000, 1)
            except (OSError, HTTPError, URLError):
                online, latency = False, None
            services.append({"name": name[:120], "description": str(item.get("description", ""))[:500],
                             "online": online, "latency_ms": latency})
    except (ValueError, KeyError, TypeError) as exc:
        # A bad optional probe must not discard host telemetry.  Keep the
        # diagnostic free of configuration contents, which may contain URLs.
        print(f"Configuração de serviços ignorada: {type(exc).__name__}", file=sys.stderr)
        return []
    return services


def collect():
    now = datetime.now(timezone.utc)
    disk = psutil.disk_usage("/")
    memory = psutil.virtual_memory()
    counts, problems = docker_metrics()
    services = service_metrics()
    alerts = []
    for item in problems:
        alerts.append({"priority": "warning", "title": f"Container {item['state']}: {item['name']}",
                       "description": item["detail"], "timestamp": now.isoformat()})
    for item in services:
        if not item["online"]:
            alerts.append({"priority": "critical", "title": f"Serviço offline: {item['name']}",
                           "description": item["description"], "timestamp": now.isoformat()})
    return {
        "collected_at": now.isoformat(), "hostname": socket.gethostname(),
        "cores": psutil.cpu_count(logical=True) or 1,
        "ram_gb": round(memory.total / 1024**3, 2),
        "disk_gb": round(disk.total / 1024**3, 2),
        "os": platform.platform(), "region": os.getenv("DASH_VPS_REGION", ""),
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": memory.percent, "disk_percent": disk.percent,
        "load_1m": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0,
        "uptime_seconds": max(0, int(now.timestamp() - psutil.boot_time())),
        "containers": counts, "services": services,
        "alerts": alerts[:100], "problem_containers": problems,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="imprime o payload sem enviar")
    args = parser.parse_args()
    payload = collect()
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    api_url = os.getenv("DASH_VPS_API_URL", "").rstrip("/")
    token = os.getenv("DASH_VPS_INGEST_TOKEN", "")
    if not api_url or not token:
        print("Configure DASH_VPS_API_URL e DASH_VPS_INGEST_TOKEN", file=sys.stderr)
        return 2
    request = Request(
        f"{api_url}/api/v1/metrics",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            if response.status != 201:
                raise RuntimeError(f"HTTP {response.status}")
    except (OSError, HTTPError, URLError, RuntimeError) as exc:
        status = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
        print(f"Falha ao enviar coleta: {status}", file=sys.stderr)
        return 1
    print("Coleta enviada com sucesso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
