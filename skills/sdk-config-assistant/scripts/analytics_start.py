#!/usr/bin/env python3
"""Write or update this run's start record in <slug>.analytics.json.

Called right after Step 1a (customer name, domain and tier are known), and
again after Step 1c when the operator email has been read. The record is
keyed by runId, so a second call updates the same record and Step 14b-A
later completes it instead of adding a new one.

Usage:
  python3 scripts/analytics_start.py --slug-only --name "<customer name>"
  python3 scripts/analytics_start.py --run-id <runId> --started-at <startedAt> \
      --name "<customer name>" --domain <domain> --tier <tier> \
      [--operator-email <email>] [--profiles-dir <dir>]

Prints `SLUG <slug>` with --slug-only. A name with no letters or digits prints a
WARNING instead and nothing is written. Otherwise prints `OK <slug>`, then one
line of JSON with the analytics asset IDs from the operator manifest (empty
object when the file has never been uploaded). Prints `WARNING: ...` and exits
0 on any failure: analytics never blocks the onboarding.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import re
import sys
from pathlib import Path

OPERATOR_SOURCE = "meta[name=acoustic-id] on app.goacoustic.com"


def slugify(value: str) -> str:
    """Same rule as slugify() in generate_sdk_patched.py."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "customer"


def find_profiles_dir() -> "Path | None":
    dirs = glob.glob("/sessions/*/mnt/sdk-config-assistant/profiles")
    return Path(dirs[0]) if dirs else None


def write_start_record(profiles_dir: Path, slug: str, run_id: str, started_at: str,
                       name: str, domain: str, tier: str, operator_email: str = "",
                       now: "str | None" = None) -> Path:
    path = profiles_dir / f"{slug}.analytics.json"
    try:
        analytics = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, ValueError):
        analytics = {}
    if not isinstance(analytics, dict):
        analytics = {}

    analytics.setdefault("schemaVersion", "1.0.0")
    analytics.setdefault("profileSlug", slug)
    analytics.setdefault("operationalProfileFile", f"{slug}.json")
    analytics.setdefault("customerReference", {"name": name, "productionDomain": domain})
    analytics.setdefault("runHistory", [])
    analytics.setdefault("feedbackHistory", [])

    record = next((r for r in analytics["runHistory"]
                   if isinstance(r, dict) and r.get("runId") == run_id), None)
    if record is None:
        record = {"runId": run_id}
        analytics["runHistory"].append(record)
    if record.get("status") not in (None, "started"):
        return path  # already completed by 14b-A; never downgrade it

    record.update({
        "status": "started",
        "startedAt": started_at,
        "workflowMode": "new",
        "action": "full_onboarding",
        "subscriptionTier": tier,
        "customerName": name,
        "productionDomain": domain,
    })
    if operator_email:
        record["operatorEmail"] = operator_email
        analytics["operator"] = {"email": operator_email, "source": OPERATOR_SOURCE}

    analytics["lastUpdatedAt"] = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(analytics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def analytics_meta(profiles_dir: Path, slug: str) -> dict:
    manifest_path = profiles_dir / ".operator-cms-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return ((manifest.get("assets") or {}).get(slug) or {}).get("analytics") or {}


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", required=True)
    ap.add_argument("--slug-only", action="store_true")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--started-at", default="")
    ap.add_argument("--domain", default="")
    ap.add_argument("--tier", default="")
    ap.add_argument("--operator-email", default="")
    ap.add_argument("--profiles-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    if not re.search(r"[a-z0-9]", args.name.lower()):
        # slugify() would fall back to "customer" and every empty name would share one file
        print("WARNING: customer name has no letters or digits; no slug and no start record")
        return 0
    slug = slugify(args.name)
    if args.slug_only:
        print(f"SLUG {slug}")
        return 0
    if not args.run_id:
        print("WARNING: runId missing; start record not written")
        return 0
    profiles_dir = args.profiles_dir or find_profiles_dir()
    if profiles_dir is None or not profiles_dir.is_dir():
        print("WARNING: profiles dir not found; start record not written")
        return 0
    try:
        write_start_record(profiles_dir, slug, args.run_id, args.started_at, args.name,
                           args.domain, args.tier, args.operator_email)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: could not write start record ({exc})")
        return 0
    print(f"OK {slug}")
    print(json.dumps(analytics_meta(profiles_dir, slug)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
