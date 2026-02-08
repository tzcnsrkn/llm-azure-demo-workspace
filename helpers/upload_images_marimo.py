import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    from __future__ import annotations

    import mimetypes
    import socket
    import threading
    import uuid
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from dataclasses import dataclass
    from pathlib import Path
    from urllib.parse import quote, urlparse

    import requests
    from requests.adapters import HTTPAdapter

    # ---- CONFIGURATION ----
    # Update with the new IP from your Terraform output
    BASE_HOST = "74.248.24.95"

    PORTS_TO_TRY = (8080,)

    # Update the prefixes to match the "api_base_url" output
    CACHE_V2_PREFIXES = (
        "/images",        # <--- The correct route found in your logs
        "/api/images",    # Fallback just in case
        "/cache",
    )

    ROOT = r"C:\Workspaces\LLMs_ML\llm-azure-demo-workspace\marimo-mission\02\improvised\dataset_cleaned_by_model\bears"
    TTL_SECONDS = 3600
    WORKERS = 8

    CONNECT_TIMEOUT_SECONDS = 3
    READ_TIMEOUT_SECONDS = 60
    TTL_PARAM = "ttl"

    SUCCESS_CODES = {200, 201, 202, 204}
    # -----------------------

    _tls = threading.local()

    def _get_session() -> requests.Session:
        s = getattr(_tls, "session", None)
        if s is None:
            s = requests.Session()
            adapter = HTTPAdapter(pool_connections=WORKERS * 2, pool_maxsize=WORKERS * 2)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            _tls.session = s
        return s

    def _guess_content_type(p: Path) -> str:
        ct, _ = mimetypes.guess_type(str(p))
        return ct or "application/octet-stream"

    def _iter_files(root: Path) -> list[Path]:
        return [p for p in root.rglob("*") if p.is_file()]

    def _make_key(root: Path, file_path: Path) -> str:
        rel = file_path.relative_to(root).as_posix()
        return rel.replace("/", "__")

    def _url(base: str, path: str) -> str:
        return base.rstrip("/") + "/" + path.lstrip("/")

    def _url_with_key(api_root: str, key: str) -> str:
        return f"{api_root.rstrip('/')}/{quote(key, safe='')}"

    def _check_port_open(host: str, port: int, timeout: int = 2) -> bool:
        """Fast TCP check to see if the port is accepting connections."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    def _expand_bases(host: str) -> list[str]:
        host = host.strip().rstrip("/")
        if host.startswith(("http://", "https://")):
            return [host]

        # Generate candidate URLs based on NSG allowed ports
        bases = []
        for p in PORTS_TO_TRY:
            bases.append(f"http://{host}:{p}")
        return bases

    @dataclass(frozen=True)
    class Candidate:
        name: str
        method: str

        def put(self, session: requests.Session, api_root: str, key: str, file_path: Path, ttl: int | None) -> requests.Response:
            url = _url_with_key(api_root, key)
            params = {TTL_PARAM: str(ttl)} if ttl and ttl > 0 else {}
            ct = _guess_content_type(file_path)
            with file_path.open("rb") as f:
                return session.request(
                    self.method,
                    url,
                    params=params,
                    data=f,
                    headers={"Content-Type": ct},
                    timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
                )

    CANDIDATES = [
        Candidate(name="PUT (raw)", method="PUT"),
        Candidate(name="POST (raw)", method="POST"),
    ]

    def _detect_endpoint(sample_path: Path) -> tuple[str, Candidate] | None:
        s = _get_session()
        probe_key = f"__probe__{uuid.uuid4().hex}"
        print(f"--- Network Diagnostics ---")

        bases = _expand_bases(BASE_HOST)
        valid_bases = []

        # 1. Phase 1: TCP Port Scan
        for base in bases:
            parsed = urlparse(base)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            print(f"Checking TCP connectivity to {host}:{port} ... ", end="", flush=True)
            if _check_port_open(host, port, timeout=2):
                print("OPEN")
                valid_bases.append(base)
            else:
                print("CLOSED/FILTERED (Skipping)")

        if not valid_bases:
            print("\n[!] All ports are blocked or the server is down.")
            print("    Check: 1. Is the VM running? 2. Is the Public IP correct?")
            return None

        # 2. Phase 2: API Path Probe
        print(f"\n--- Probing API Endpoints on Open Ports ---")
        for base in valid_bases:
            for prefix in CACHE_V2_PREFIXES:
                api_root = _url(base, prefix)
                for cand in CANDIDATES:
                    try:
                        # We use a small timeout for probes
                        r = cand.put(s, api_root, probe_key, sample_path, TTL_SECONDS)
                        code = r.status_code
                        r.close()

                        print(f"[{code}] {cand.method} {api_root}/{probe_key}")

                        if code in SUCCESS_CODES:
                            print(f"\n>>> SUCCESS! Found endpoint: {api_root}")
                            return api_root, cand
                    except Exception as e:
                        print(f"[ERR] {cand.method} {api_root}: {e}")

        return None

    def _upload_one(api_root: str, cand: Candidate, root: Path, file_path: Path) -> tuple[str, bool, str]:
        s = _get_session()
        key = _make_key(root, file_path)
        try:
            r = cand.put(s, api_root, key, file_path, TTL_SECONDS)
            ok = r.status_code in SUCCESS_CODES
            msg = f"{r.status_code}"
            if not ok:
                msg += f" {r.text[:100]}"
            r.close()
            return file_path.name, ok, msg
        except Exception as e:
            return file_path.name, False, str(e)

    def main():
        root = Path(ROOT)
        if not root.is_dir():
            print(f"Error: Directory not found: {root}")
            return

        files = _iter_files(root)
        if not files:
            print("No files to upload.")
            return

        print(f"Target Host: {BASE_HOST}")
        print(f"Target Ports: {PORTS_TO_TRY}")

        # Use smallest file for probing
        sample = min(files, key=lambda p: p.stat().st_size)

        detected = _detect_endpoint(sample)
        if not detected:
            print("\nFailed to detect a working API endpoint.")
            return

        api_root, cand = detected
        print(f"\nStarting upload of {len(files)} files to {api_root}...")

        success_count = 0
        fail_count = 0

        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = [ex.submit(_upload_one, api_root, cand, root, p) for p in files]
            for fut in as_completed(futures):
                name, ok, msg = fut.result()
                if ok:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"Progress: {success_count}/{len(files)}...")
                else:
                    fail_count += 1
                    print(f"FAIL {name}: {msg}")

        print(f"\nDone. Success: {success_count}, Failed: {fail_count}")

    if __name__ == "__main__":
        main()
    return


if __name__ == "__main__":
    app.run()
