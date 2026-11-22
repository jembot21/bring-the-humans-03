#!/usr/bin/env python3
"""Fetch the five required press files fresh; verify listed image bytes and hashes."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(name, source, expected=None):
    ASSETS.mkdir(parents=True, exist_ok=True)
    # The bare URLs served older cached files in the recovery session.
    requested = source + "?fresh=bth03-" + uuid4().hex
    path = ASSETS / name
    pending = path.with_suffix(path.suffix + ".download")
    headers = ASSETS / (name + ".headers")
    subprocess.run([
        "curl", "--silent", "--show-error", "--fail", "--location",
        "--retry", "2", "--connect-timeout", "15", "--max-time", "60",
        "--header", "Cache-Control: no-cache, no-store",
        "--dump-header", str(headers), "--output", str(pending), requested,
    ], check=True)
    digest = sha256(pending)
    if expected and (digest != expected["sha256"] or
                     pending.stat().st_size != expected["bytes"]):
        raise RuntimeError(f"{name}: response does not match the fresh manifest")
    pending.replace(path)
    record = {
        "file": str(path.relative_to(ASSETS.parent)), "source_url": source,
        "requested_url": requested, "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "bytes": path.stat().st_size, "sha256": digest,
        "headers_file": str(headers.relative_to(ASSETS.parent)),
        "matches_manifest": True if expected else None,
    }
    log_path = ASSETS / "fetch-log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {"downloads": []}
    log["downloads"].append(record)
    log_path.write_text(json.dumps(log, indent=2) + "\n")
    print(f"Fetched {name}: {record['bytes']} bytes, sha256 {digest}")
    return path


def main():
    manifest_path = fetch("manifest.json", "https://make.fun/press/manifest.json")
    guide = fetch("llms.txt", "https://make.fun/press/llms.txt")
    manifest = json.loads(manifest_path.read_text())
    if "brand_badge" not in manifest or "## The brand badge" not in guide.read_text():
        raise RuntimeError("Fresh response is missing badge instructions; do not guess")
    badge_url = manifest["brand_badge"]["aspects"]["9:16"]["overlay"]
    badge = next(e for e in manifest["brand_badge"]["files"] if e["url"] == badge_url)
    card = next(e for e in manifest["referral_card"]["files"]
                if e["aspect"] == "9:16" and e["mime"] == "image/png" and not e["alpha"])
    mascot = next(e for e in manifest["files"]
                  if e["path"] == "illustrations/ghost-laptop-recording.png")
    for entry in (badge, card, mascot):
        fetch(Path(entry["path"]).name, entry["url"], entry)


if __name__ == "__main__":
    main()
